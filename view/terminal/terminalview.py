"""Terminal view for model display"""
from view import viewinterface as v
import os
from ctypes import c_ulong, windll
from model.core import State
from model.primative import Point, Shared

class TerminalView(v.ViewInterface):
    """Cross platform terminal output for model; basic input() events"""
    std_output_hdl = None
    model = None
    is_new_game = None
    seed_last = None

    def init(self, model):
        """Keep model and start new game"""
        self.model = model
        self.is_new_game = True

    def display_clear(self):
        """Utility for cross platform terminal clear"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def game_new(self):
        """ask for seed to create new game"""
        self.display_clear()
        print("SEED?")
        print("\tLeave blank for random generation")
        print("\t'L' for last seed")
        seed = input("")
        if seed.upper() == "L" and self.seed_last:
            seed = self.seed_last
        self.display_clear()
        self.is_new_game = False
        if seed:
            self.seed_last = seed
            print("SEED Requested: {}".format(seed))
        self.model.game_new(seed if seed else None)

    def display_menu(self):
        """display commands and handle events for playing"""
        options = []
        if len(self.model.move_history) > 0:
            options += ["Undo", "Reset"]
        if len(self.model.goal().robots) == 1:
            options.append("Solve")
        options += ["New Game", "Quit"]
        if self.model.goal_index < len(self.model.board_section.goals) - 1:
            options.append("Advance Level")
        if self.model.goal_index > 0:
            options.append("Previous Level")

        print("\r\n\tColor:\t\t{}\r\n\tDirection:\t{}\r\n{}".format(
            ", ".join(["[{}]{}".format(robot.name[0], robot.name[1:])
                       for robot in Shared.ROBOTS]),
            ", ".join(["[{}]{}".format(direction.name[0], direction.name[1:])
                       for direction in Shared.DIRECTIONS]),
            ", ".join(["[{}]{}".format(option[0], option[1:]) for option in options])))
        robot_direction = input().lower()
        self.display_clear()
        robot = 0
        direction = 0
        if robot_direction == "q":
            raise SystemExit
        elif robot_direction == "r":
            if len(self.model.move_history) > 0:
                self.model.level_restart()
                return
        elif robot_direction == "u":
            if len(self.model.move_history) > 0:
                last_move = self.model.move_undo()
                print("\tReverted move of {} to {}".format(
                    last_move[0].name,
                    last_move[3]))
                return
        elif robot_direction == "s" and len(self.model.goal().robots) == 1:
            print("Solving...")
            directions = []
            for robot_location in self.model.robots_location:
                lastmove = self.model.move_history_by_robot(robot_location)
                directions.append(0 if lastmove is None else lastmove[1].value)
            answer = self.model.solver.generate(
                self.model.robots_location,
                self.model.goal(),
                directions,
                True)
            if answer is not None:
                print("Move\t{}".format(
                    "\t\t".join([robot.name
                                 for robot
                                 in self.model.solver.robot_objects])))
                for i, move in enumerate(answer):
                    print("{:02d}. {}".format(
                        i,
                        "\t".join(["({:02d}, {:02d}) {}".format(
                            robot[0] % 16,
                            int(robot[0] / 16),
                            "     " if robot[1] == 0 else next(
                                direction
                                for direction
                                in Shared.DIRECTIONS
                                if direction.value == robot[1]))
                                   for robot in move])))
            return
        elif robot_direction == "n":
            self.is_new_game = True
            return
        elif robot_direction == "p" and self.model.goal_index > 0:
            self.model.level_previous()
            return
        elif robot_direction == "a" and self.model.goal_index < len(self.model.board_section.goals) - 1:
            self.model.level_next()
            return
        elif len(robot_direction) == 2:
            robot = Shared.robot_by_name(robot_direction[0])
            direction = Shared.direction_by_name(robot_direction[1])
        if robot and direction:
            print("\tMoving {} in the direction {}".format(robot.name, direction.name))
            self.model.robot_move(robot, direction)
        else:
            print("\t**Command '{}' not recognized!**\r\n".format(robot_direction))

    def handle_events(self):
        if self.is_new_game:
            self.game_new()
        elif self.model.game_state == State.play:
            self.display_menu()
        elif self.model.game_state == State.level_complete:
            print("""\r\nCONGRATS!
                !Level {} of {} completed in {} moves, {} seconds!
                !You touched {} spaces!""".format(
                    self.model.goal_index+1,
                    len(self.model.board_section.goals),
                    len(self.model.move_history),
                    self.model.level_time,
                    len(self.model.space_touched)))
            input("Ready for next level ???")
            self.display_clear()
            self.model.level_new()
        elif self.model.game_state == State.game_complete:
            print("""Game completed - {} level(s) in {} moves, {} seconds!
                You touched {} spaces!""".format(
                    self.model.goal_index + 1,
                    self.model.game_move_count,
                    self.model.game_time_count,
                    self.model.game_space_touched_count))
            if input("\t[P]lay again?\r\n").lower() == "p":
                self.display_clear()
                self.model.game_new()
            else:
                raise SystemExit

    def update(self):
        """no internal state to update for terminal view"""
        pass

    def space_touched_by_xy(self, cell):
        """Color used to display most recent move history at 'cell'"""
        color = 15 if os.name == 'nt' else ''
        for space in self.model.space_touched:
            if space[1] == cell:
                color = space[2]
        return color

    def color_update(self, color, bgcolor=15 if os.name == 'nt' else 0):
        """cross platform background and foreground color output"""
        if os.name == 'nt':
            print("", end="", flush=True)
            if self.std_output_hdl is None:
                standard_output_handle = c_ulong(0xfffffff5)
                windll.Kernel32.GetStdHandle.restype = c_ulong
                self.std_output_hdl = windll.Kernel32.GetStdHandle(standard_output_handle)
            windll.Kernel32.SetConsoleTextAttribute(self.std_output_hdl, bgcolor | color)
        else:
            print("\033[" + str(bgcolor) + ";" + str(color) + "m", end="")

    def display(self):
        goal = self.model.board_section.goals[self.model.goal_index]
        print("Goal {} of {}: move {} to cell ({}, {})".format(
            self.model.goal_index+1,
            len(self.model.board_section.goals),
            " or ".join([robot.name for robot in goal.robots]),
            goal.point.x,
            goal.point.y))
        print("\t" + " _"*self.model.board_section.width)
        for j, row in enumerate(self.model.board_section.board):
            print("\t", end="")
            for k, cell in enumerate(row):
                point = Point(k, j)
                if cell & Shared.DIRECTIONS[3].value:
                    print("|", end="")
                elif k % 8 != 0:
                    print(" ", end="")

                robot = self.model.robot_by_cell(point)
                back_color = 0
                color = 15 if os.name == 'nt' else '30'
                if robot is None:
                    if goal.point == point:
                        back_color = 0x0050 if os.name == 'nt' else 45
                    else:
                        color = self.space_touched_by_xy(point)
                else:
                    back_color = robot.bgcolor()

                self.color_update(color, back_color)
                print("_" if cell & Shared.DIRECTIONS[1].value else ".", end="")
                self.color_update(0)
                if(k + 1) % 8 == 0 and not cell & Shared.DIRECTIONS[2].value:
                    print(" ", end="") #end of board section and no east way
                if(k + 1) % 16 == 0:
                    print("|", end="")
                    move_count = len(self.model.move_history)
                    if move_count > 0:
                        if j == 0:
                            print("\tMove History({}):".format(move_count), end="")
                        elif move_count >= j:
                            last_move = self.model.move_history[-1*j]
                            print("\t{}. {} {} from {}".format(
                                move_count-j+1,
                                last_move[0].name,
                                last_move[1].name,
                                last_move[2]), end="")
            print("")
        robot_location_seed = "".join(["{}{:02d}{:02d}".format(
            robot.name[0],
            self.model.robots_location[robot].x,
            self.model.robots_location[robot].y) for robot in self.model.robots_location])
        goal_seed = "|".join(["{}{:02d}{:02d}".format(
            "".join([robot.name[0] for robot in goal.robots]),
            goal.point.x,
            goal.point.y) for goal in self.model.board_section.goals])
        print("SEED Level: {}!{}!{}".format(
            self.model.board_section.key,
            robot_location_seed,
            goal_seed.split("|")[self.model.goal_index]))
        print("SEED Game : {}!{}!{}".format(
            self.model.board_section.key,
            robot_location_seed,
            goal_seed))

    def quit(self):
        pass
