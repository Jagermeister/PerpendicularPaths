from ctypes import *
import os
import time
import random
from BoardGenerator import *
from SolutionGenerator import *

class State(object):
    menu = 0b00000001
    play = 0b00000010
    option = 0b00000100
    gg = 0b00010000
    level_restart = 0b00100000
    level_complete = 0b10000000
    game_restart = 0b01000000
    game_complete = 0b00001000

class PerpendicularPaths:
    board_section = None
        #BoardSection
    solver = None
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
    std_output_hdl = None

    def __init__ (self):
        self.game_state = State.menu

    def board_generate (self):
        g = BoardGenerator()
        self.board_section = g.generate("1_2_3_4")
        self.directions = g.directions
        self.robots = g.robots
        self.solver = SolutionGenerator(
                self.board_section,
                self.robots,
                self.directions
            )
        self.robots_generate()
        random.shuffle (self.board_section.goals)
        self.board_section = Board (123, self.board_section.board, g.walls, self.board_section.goals[0:5])

    def robots_generate(self):
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

    def space_touched_by_xy (self, cell):
        color = 15 if os.name == 'nt' else ''
        for i, s in enumerate(self.space_touched):
            if s[1] == cell:
                color = s[2]
        return color

    def color_update (self, color, bgcolor=15 if os.name == 'nt' else 0):
        if os.name == 'nt':
            print ("", end="", flush=True)
            if self.std_output_hdl is None:
                STD_OUTPUT_HANDLE_ID = c_ulong(0xfffffff5)
                windll.Kernel32.GetStdHandle.restype = c_ulong
                self.std_output_hdl = windll.Kernel32.GetStdHandle(STD_OUTPUT_HANDLE_ID)
            windll.Kernel32.SetConsoleTextAttribute(self.std_output_hdl, bgcolor | color)
        else:
            print ("\033[" + str(bgcolor) + str(color) + "m", end="")


    def display_update(self):       
        goal = self.board_section.goals[self.goal_index]
        print ("Goal " + str(self.goal_index+1) + " of " + str(len(self.board_section.goals)) + ": move " + goal.robots[0].name + " to cell (" + (str(goal.point.x)) + ", " + str(goal.point.y) + ")", end="\r\n\t")
        for r in range (0, self.board_section.width):
            print (" _", end="")
        print ("")
        for j, r in enumerate(self.board_section.board):
            print ("\t", end="")
            for k, c in enumerate(r):
                point = Point (k, j)
                if c & self.directions[3].value == self.directions[3].value:
                    print ("|", end="")
                elif k % 8 != 0:
                    print (" ", end="")

                robot = self.robot_by_cell (point)
                back_color = 0
                color = 15
                if robot is None:
                    color = self.space_touched_by_xy (point)
                    if goal.point == point:
                        back_color = 0x0050 if os.name == 'nt' else 45
                else:
                    back_color = robot.bgcolor()

                self.color_update (color, back_color)
                #RODO: South wall
                if c & self.directions[1].value == self.directions[1].value:
                    print ("_", end="")
                else:
                    print (".", end="")
                self.color_update (0)
                
                if (k + 1) % 8 == 0 and c & self.directions[2].value != self.directions[2].value:
                    #end of board section and no an east way
                    print (" ", end="")
                if (k + 1) % 16 == 0:
                    print ("|", end="")
                    move_count = len(self.move_history)
                    if move_count > 0:
                        if j == 0:
                            print ("\tPrevious Moves (" + str(move_count) + "):", end="")
                        elif move_count >= j:
                            last_move = self.move_history[-1*j]
                            print ("\t" + str(move_count-j+1) + ". " + last_move[0].name + " " + last_move[1].name + " from ", end="")
                            print (last_move[2], end="")
                    
            print ("")

    def cell_move (self, point, direction, robot, space_touched_id):
        advanced_cell = copy.copy (point)
        advanced_cell.move (direction)
        if ((advanced_cell.x < 0 or advanced_cell.x > 15) or
            (advanced_cell.y < 0 or advanced_cell.y > 15)):
            #Moving would put us out of bounds
            return point
        if self.board_section.board_value (point) & direction.value == direction.value:
            #Wall in point stopping us
            return point
        if self.board_section.board_value (advanced_cell) & direction.reverse().value == direction.reverse().value:
            #Wall in next point stopping us
            return point
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
            print ("ROBOT MUST RICOCHET!")
            return
        if len(self.space_touched) > 0:
            last_space_touched_id = self.space_touched[-1][0] + 1
        else:
            last_space_touched_id = 0
        point = self.robots_location[robot]
        new_cell = self.cell_move (point, direction, robot, last_space_touched_id)
        if (point == new_cell):
            print ("CAN NOT MOVE IN THAT DIRECTION")
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

    def display_menu (self):
        robot_direction = input ("""\r\nMove with two characters:
\tColor:\t\t [R]ed, [B]lue, [Y]ellow, [G]reen
\tDirection:\t [N]orth, [S]outh, [E]ast, [W]est
""" + ("\tExample:\t YS aka move Yellow South\r\n" if self.goal_index == 0 else "") +
"""\t""" + ("[U]ndo - [R]eset - " if len(self.move_history) > 0 else "") + "[Q]uit [S]olve\r\n""")
        os.system('cls' if os.name == 'nt' else 'clear')
        robot_direction = robot_direction.lower()
        robot = 0
        direction = 0
        if len(robot_direction) == 1:
            if robot_direction == "q":
                self.game_state = State.gg
                return
            elif robot_direction == "r":
                if len(self.move_history) > 0:
                    self.game_state = State.level_restart
                    return
            elif robot_direction == "u":
                if len(self.move_history) > 0:
                    last_move = self.move_history.pop(-1)
                    self.robot_location_update (last_move[0], last_move[2])
                    self.space_touched_remove_last()
                    print ("\tReverted move of " + last_move[0].name + " to " + str(last_move[3]))
                    return
            elif robot_direction == "s":
                print ("Solving...")
                answer = self.solver.generate (
                        self.robots_location,
                        self.board_section.goals[self.goal_index],
                        True
                    )
                if answer is not None:
                    print ("Move", end="\t")
                    for r in self.robots:
                        print (r.name, end="\t\t")
                    print ("")
                    for i, move in enumerate(answer):
                        print ("({0:02d}.".format (i), end=" ")
                        for m in move:
                            print ("({0:02d},".format (m[0][0]), end=" ")
                            print ("{0:02d})".format (m[0][1]), end=" ")
                            if m[1] != 0:
                                print (next(d for d in self.directions if d.value == m[1]), end="\t")
                            else:
                                print ("     ", end="\t")
                        print ("")
                return
        elif len(robot_direction) == 2:
            #TODO: Fix hardcode
            if robot_direction[0] == "r":
                robot = self.robots[0]
            elif robot_direction[0] == "b":
                robot = self.robots[1]
            elif robot_direction[0] == "y":
                robot = self.robots[2]
            elif robot_direction[0] == "g":
                robot = self.robots[3]

            if robot_direction[1] == "n":
                direction = self.directions[0]
            elif robot_direction[1] == "s":
                direction = self.directions[1]
            elif robot_direction[1] == "e":
                direction = self.directions[2]
            elif robot_direction[1] == "w":
                direction = self.directions[3]

        if robot and direction:
            print ("\tMoving " + robot.name + " in the direction " + direction.name)
            self.robot_move (robot, direction)
        else:
            print ("\t**Command '" + robot_direction + "' is not recognized!**\r\n")

    def top_menu(self):
        print ("""
  |\_/|        ****************************    (\_/)
 / @ @ \       *  "Purrrfectly pleasant"  *   (='.'=)
( > º < )      *   Perpendicular Paths    *   (")_(")
 `>>x<<`       *                          *
 /  O  \       ****************************
""")

    def bot_menu(self):
        print ("""
\t               )\._.,--....,'``.
\t .b--.        /;   _.. \   _\  (`._ ,.
\t`=,-,-'~~~   `----(,_..'--(,_..'`-.;.'
""")

    def play_menu(self):
        self.top_menu()
        print ("Press [P] to Play!")
        self.bot_menu()
        answer = input ()
        if len(answer) == 1 and answer.lower() == "p":
            self.game_state = State.game_restart
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        else:
            self.game_state = State.gg

    def new_level(self):
        self.move_history = []
        self.space_touched = []
        self.robots_location = {}
        for r in self.robots_starting_location:
            self.robots_location[r] = self.robots_starting_location[r]

    def new_game(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.board_generate()
        self.goal_index = 0
        self.game_move_count = 0
        self.game_time_count = 0
        self.game_space_touched_count = 0
        self.new_level()

    def play_game(self):
        playing = True
        level_starttime = 0
        while playing:
            if self.game_state == State.menu:
                os.system('cls' if os.name == 'nt' else 'clear')
                self.play_menu()
            elif self.game_state == State.option:
                self.game_state = State.play
            elif self.game_state == State.game_restart:
                os.system('cls' if os.name == 'nt' else 'clear')
                self.new_game()
                self.game_state = State.play
            elif self.game_state == State.level_restart:
                self.new_level()
                self.game_state = State.play
            elif self.game_state == State.play:
                if level_starttime == 0:
                    level_starttime = time.clock()
                self.display_update()
                goal = self.board_section.goals[self.goal_index]
                for r in self.robots:
                    if r in goal.robots:
                        if goal.point == self.robots_location[r]:
                            self.game_state = State.level_complete
                if self.game_state == State.play:
                    self.display_menu()
            elif self.game_state == State.level_complete:
                self.game_time_count += time.clock() - level_starttime
                print ("\r\nCONGRATS!!!")
                print ("\t!Level " + str(self.goal_index+1) + " of " + str(len(self.board_section.goals)) + " completed in " + str(len(self.move_history)) + " moves, " + str(time.clock() - level_starttime) + " seconds!")
                print ("\t!You touched " + str(len(self.space_touched)) + " spaces!")
                print ("Next level loading...", end="", flush=True)
                for i in range (1, 24):# if self.goal_index == 0 else 18):
                    time.sleep (0.33)
                    print (".", end="", flush=True)
                os.system('cls' if os.name == 'nt' else 'clear')
                level_starttime = time.clock()
                self.game_move_count += len(self.move_history)
                self.game_space_touched_count += len(self.space_touched)
                self.robots_starting_location = {}
                for r in self.robots_location:
                    self.robots_starting_location[r] = self.robots_location[r]
                self.goal_index += 1
                if self.goal_index == len(self.board_section.goals):
                    self.game_state = State.game_complete
                else:
                    self.game_state = State.level_restart
            elif self.game_state == State.game_complete:
                print ("Game completed - " + str(self.goal_index) + " level(s) in " + str(self.game_move_count) + " moves, " + str(self.game_time_count) + " seconds!")
                print ("You touched " + str(self.game_space_touched_count) + " spaces!")
                if input ("\t[P]lay again?\r\n").lower() == "p":
                    self.game_state = State.menu
                else:
                    playing = False
            elif self.game_state == State.gg:
                print ("""
   |\      _,,,---,,_
   /,`.-'`'    -.  ;-;;,_
  |,4-  ) )-,_..;\ (  `'-'
 '---''(_/--'  `-'\_)
\t You died.
""")
                playing = False

game = PerpendicularPaths()
game.play_game()
