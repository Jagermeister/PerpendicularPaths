import random
import copy
from .primative import Shared, Point, Board
from .BoardGenerator import BoardGenerator
from .SolutionGenerator import SolutionGenerator

class State(object):
    play = 0b00000010
    game_over = 0b00010000
    level_restart = 0b00100000
    level_complete = 0b10000000
    game_restart = 0b01000000
    game_complete = 0b00001000

class PerpendicularPaths:
    board_section = None
    solver = None
    __boardgenerator = None
    game_state = 0

    robots_location = {}
    __robots_starting_location = {}
    game_move_count = 0
    game_time_count = 0
    level_time = 0
    move_history = []
        #robot, direction, old cell, new cell
    game_space_touched_count = 0
    space_touched = []
        #id, cell, color
    goal_index = 0

    def __init__(self):
        self.game_state = State.game_restart
        self.__boardgenerator = BoardGenerator()
        self.new_game()

    def __board_generate(self, seed=None):
        self.board_section = self.__boardgenerator.generate(seed)
        self.solver = SolutionGenerator(
            self.board_section,
            Shared.ROBOTS,
            Shared.DIRECTIONS)
        self.__robots_generate()
        random.shuffle(self.board_section.goals)
        self.board_section = Board(
            self.board_section.key,
            self.board_section.board,
            self.board_section.goals[0:5])

    def __robots_generate(self):
        self.__robots_starting_location = {}
        for robot in Shared.ROBOTS:
            robot_placement_attempts = 0
            try_again = True
            while try_again:
                new_point = Point(
                    random.randint(0, self.board_section.width - 1),
                    random.randint(0, self.board_section.height - 1))
                if new_point.x not in(7, 8) and new_point.y not in(7, 8):
                    try_again = False
                    for goal in self.board_section.goals:
                        if goal.point == new_point:
                            try_again = True
                            break
                    for robot_placed in self.__robots_starting_location:
                        if self.__robots_starting_location[robot_placed] == new_point:
                            try_again = True
                            break
                assert robot_placement_attempts < 50
                robot_placement_attempts += 1
            self.__robots_starting_location[robot] = new_point

    def __cell_move(self, point, direction, robot, space_touched_id):
        if self.board_section.board_value(point) & direction.value == direction.value:
            #Wall in point stopping us
            return point
        advanced_cell = copy.copy(point)
        advanced_cell.move(direction)
        for _robot in self.robots_location:
            if advanced_cell == self.robots_location[_robot]:
                #blocked by robot in next point
                return point
        self.space_touched.append((space_touched_id, point, robot.fgcolor()))
        return self.__cell_move(advanced_cell, direction, robot, space_touched_id)

    def move_history_by_robot(self, robot):
        #CALLABLE BY OUTSIDE WORLD
        last_move = None
        for move in self.move_history:
            if move[0] == robot:
                last_move = move
        return last_move

    def robot_by_cell(self, cell):
        #CALLABLE BY OUTSIDE WORLD
        for robot in self.robots_location:
            if self.robots_location[robot] == cell:
                return robot

    def robot_move(self, robot, direction):
        #CALLABLE BY OUTSIDE WORLD
        last_move = self.move_history_by_robot(robot)
        if (last_move is not None and
                (last_move[1] == direction or last_move[1] == direction.reverse())):
            print("MUST MOVE PERPENDICULAR!")
            return
        if len(self.space_touched) > 0:
            last_space_touched_id = self.space_touched[-1][0] + 1
        else:
            last_space_touched_id = 0
        point = self.robots_location[robot]
        goal = self.board_section.goals[self.goal_index]
        new_cell = self.__cell_move(point, direction, robot, last_space_touched_id)
        if point == new_cell:
            print("CAN NOT MOVE IN THAT DIRECTION")
        elif last_move is None and new_cell == goal.point and robot in goal.robots:
            print("MUST MOVE PERPENDICULAR BEFORE GOAL")
            if len(self.space_touched) > 0:
                last_id = self.space_touched[-1][0]
                self.space_touched = [s for s in self.space_touched if not s[0] == last_id]
        else:
            print("\t" + robot.name + " moved to ", end="")
            print(str(new_cell) + " from " + str(point))
            self.robots_location[robot] = new_cell
            self.move_history.append((robot, direction, point, new_cell))

    def new_level(self):
        #per level information: movehistory, spaces, robots
        assert self.game_state in [State.level_restart, State.game_restart]
        self.move_history = []
        self.space_touched = []
        self.robots_location = {}
        self.level_time = 0
        for robot in self.__robots_starting_location:
            self.robots_location[robot] = self.__robots_starting_location[robot]
        self.game_state = State.play

    def new_game(self, seed=None):
        #generate board, setup goal, setup robots, start time
        assert self.game_state == State.game_restart
        self.__board_generate(seed)
        self.goal_index = 0
        self.game_move_count = 0
        self.game_time_count = 0
        self.game_space_touched_count = 0
        self.new_level()

    # def play_game(self):
    #     playing = True
    #     while playing:
            # if self.game_state == State.game_restart:
            #     level_starttime = 0
            #     os.system('cls' if os.name == 'nt' else 'clear')
            #     print("SEED?")
            #     print("\tLeave blank for random generation")
            #     print("\t'L' for last seed")
            #     seed = input("")
            #     if seed.upper() == "L":
            #         if self.board_section is None:
            #             seed = None
            #         else:
            #             seed = self.board_section.key
            #     self.new_game(seed if seed != "" else None)
            #     self.game_state = State.play
            # elif self.game_state == State.level_restart:
            #     self.new_level()
            #     self.game_state = State.play
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
    #             print("\r\nCONGRATS!")
    #             print("\t!Level " + str(self.goal_index+1) + " of " +
        #str(len(self.board_section.goals))
        #+ " completed in " + str(len(self.move_history)) + " moves, " + str(time.time()
            #- level_starttime) + " seconds!")
    #             print("\t!You touched " + str(len(self.space_touched)) + " spaces!")
    #             input("Ready for next level ???")
    #             os.system('cls' if os.name == 'nt' else 'clear')
    #             level_starttime = time.time()
    #             self.game_move_count += len(self.move_history)
    #             self.game_space_touched_count += len(self.space_touched)
    #             self.__robots_starting_location = {}
    #             for r in self.robots_location:
    #                 self.__robots_starting_location[r] = self.robots_location[r]
    #             self.goal_index += 1
    #             if self.goal_index == len(self.board_section.goals):
    #                 self.game_state = State.game_complete
    #             else:
    #                 self.game_state = State.level_restart
    #         elif self.game_state == State.game_complete:
    #             print("Game completed - " + str(self.goal_index) + " level(s) in "
    # + str(self.game_move_count) +
        #" moves, " + str(self.game_time_count) + " seconds!")
    #             print("You touched " + str(self.game_space_touched_count) + " spaces!")
    #             if input("\t[P]lay again?\r\n").lower() == "p":
    #                 self.game_state = State.game_restart
    #             else:
    #                 self.game_state = State.game_over
    #         elif self.game_state == State.game_over:
    #             playing = False
