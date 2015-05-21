import random
from .BoardGenerator import *
from .SolutionGenerator import *

class State(object):
    play = 0b00000010
    gg = 0b00010000
    level_restart = 0b00100000
    level_complete = 0b10000000
    game_restart = 0b01000000
    game_complete = 0b00001000

class core:
    board_section = None
    solver = None
    boardgenerator = None
    game_state = 0

    robots_location = {}
    robots_starting_location = {}
    game_move_count = 0
    game_time_count = 0
    move_history = []
        #robot, direction, old cell, new cell
    game_space_touched_count = 0
    space_touched = []
        #id, cell, color
    goal_index = 0

    def __init__ (self):
        self.game_state = State.game_restart
        self.boardgenerator = BoardGenerator()
        self.new_game()

    def board_generate (self, seed=None):
        self.board_section = self.boardgenerator.generate(seed)
        self.directions = Shared.DIRECTIONS
        self.robots = Shared.ROBOTS
        self.solver = SolutionGenerator(
                self.board_section,
                self.robots,
                self.directions
            )
        self.robots_generate()
        random.shuffle (self.board_section.goals)
        self.board_section = Board (
                self.board_section.key,
                self.board_section.board,
                self.board_section.goals[0:5]
            )

    def robots_generate(self):
        self.robots_starting_location = {}
        for r in self.robots:
            robot_placement_attempts = 0
            try_again = True
            while try_again:
                new_point = Point (
                        random.randint (0, self.board_section.width - 1),
                        random.randint (0, self.board_section.height - 1)
                    )
                if new_point.x not in (7,8) and new_point.y not in (7,8):
                    try_again = False
                    for g in self.board_section.goals:
                        if g.point == new_point:
                            try_again = True
                            break
                    for r2 in self.robots_starting_location:
                        if self.robots_starting_location[r2] == new_point:
                            try_again = True
                            break
                assert robot_placement_attempts < 50
                robot_placement_attempts += 1
            self.robots_starting_location[r] = new_point

    def robot_by_cell (self, cell):
        for r in self.robots_location:
            if self.robots_location[r] == cell:
                return r;

    def cell_move (self, point, direction, robot, space_touched_id):
        if self.board_section.board_value (point) & direction.value == direction.value:
            #Wall in point stopping us
            return point
        advanced_cell = copy.copy (point)
        advanced_cell.move (direction)
        for r in self.robots_location:
            if advanced_cell == self.robots_location[r]:
                #blocked by robot in next point
                return point
        self.space_touched.append ((space_touched_id, point, robot.fgcolor()))
        return self.cell_move (advanced_cell, direction, robot, space_touched_id)

    def robot_location_update (self, robot, point):
        self.robots_location[robot] = point

    def move_history_by_robot (self, robot):
        last_move = None
        for m in self.move_history:
            if m[0] == robot:
                last_move = m
        return last_move

    def robot_move (self, robot, direction):
        last_robot_move = self.move_history_by_robot (robot)
        if last_robot_move is not None and (last_robot_move[1] == direction or last_robot_move[1] == direction.reverse()):
            print ("MUST MOVE PERPENDICULAR!")
            return
        if len(self.space_touched) > 0:
            last_space_touched_id = self.space_touched[-1][0] + 1
        else:
            last_space_touched_id = 0
        point = self.robots_location[robot]
        goal = self.board_section.goals[self.goal_index]
        new_cell = self.cell_move (point, direction, robot, last_space_touched_id)
        if point == new_cell:
            print ("CAN NOT MOVE IN THAT DIRECTION")
        elif (  last_robot_move is None and 
                new_cell == goal.point and
                robot in goal.robots
        ):
            print ("MUST MOVE PERPENDICULAR BEFORE GOAL")
            self.space_touched_remove_last()
        else:
            print ("\t" + robot.name + " moved to ", end="")
            print (str(new_cell) + " from " + str(point))
            self.robot_location_update (robot, new_cell)
            self.move_history.append((robot, direction, point, new_cell))

    def space_touched_remove_by_id (self, key):
        self.space_touched = [s for s in self.space_touched if not s[0] == key]

    def space_touched_remove_last (self):
        if len(self.space_touched) > 0:
            self.space_touched_remove_by_id (self.space_touched[-1][0])


    def new_level(self):
        self.move_history = []
        self.space_touched = []
        self.robots_location = {}
        for r in self.robots_starting_location:
            self.robots_location[r] = self.robots_starting_location[r]

    def new_game(self, seed=None):
        self.board_generate(seed)
        self.goal_index = 0
        self.game_move_count = 0
        self.game_time_count = 0
        self.game_space_touched_count = 0
        self.new_level()

    # def play_game(self):
    #     playing = True
    #     while playing:
    #         if self.game_state == State.game_restart:
    #             level_starttime = 0
    #             os.system('cls' if os.name == 'nt' else 'clear')
    #             print ("SEED?")
    #             print ("\tLeave blank for random generation")
    #             print ("\t'L' for last seed")
    #             seed = input("")
    #             if seed.upper() == "L":
    #                 if self.board_section is None:
    #                     seed = None
    #                 else:
    #                     seed = self.board_section.key
    #             self.new_game(seed if seed != "" else None)
    #             self.game_state = State.play
    #         elif self.game_state == State.level_restart:
    #             self.new_level()
    #             self.game_state = State.play
    #         elif self.game_state == State.play:
    #             if level_starttime == 0:
    #                 level_starttime = time.time()
    #             self.display_update()
    #             goal = self.board_section.goals[self.goal_index]
    #             for r in self.robots:
    #                 if r in goal.robots:
    #                     if goal.point == self.robots_location[r]:
    #                         self.game_state = State.level_complete
    #             if self.game_state == State.play:
    #                 self.display_menu()
    #         elif self.game_state == State.level_complete:
    #             self.game_time_count += time.time() - level_starttime
    #             print ("\r\nCONGRATS!")
    #             print ("\t!Level " + str(self.goal_index+1) + " of " + str(len(self.board_section.goals)) + " completed in " + str(len(self.move_history)) + " moves, " + str(time.time() - level_starttime) + " seconds!")
    #             print ("\t!You touched " + str(len(self.space_touched)) + " spaces!")
    #             input ("Ready for next level ???")
    #             os.system('cls' if os.name == 'nt' else 'clear')
    #             level_starttime = time.time()
    #             self.game_move_count += len(self.move_history)
    #             self.game_space_touched_count += len(self.space_touched)
    #             self.robots_starting_location = {}
    #             for r in self.robots_location:
    #                 self.robots_starting_location[r] = self.robots_location[r]
    #             self.goal_index += 1
    #             if self.goal_index == len(self.board_section.goals):
    #                 self.game_state = State.game_complete
    #             else:
    #                 self.game_state = State.level_restart
    #         elif self.game_state == State.game_complete:
    #             print ("Game completed - " + str(self.goal_index) + " level(s) in " + str(self.game_move_count) + " moves, " + str(self.game_time_count) + " seconds!")
    #             print ("You touched " + str(self.game_space_touched_count) + " spaces!")
    #             if input ("\t[P]lay again?\r\n").lower() == "p":
    #                 self.game_state = State.game_restart
    #             else:
    #                 self.game_state = State.gg
    #         elif self.game_state == State.gg:
    #             playing = False
