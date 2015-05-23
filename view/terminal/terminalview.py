from view import viewinterface as v
import os
import time
import sys
from ctypes import c_ulong, windll
from model.core import State
from model.primative import Point, Shared

class terminalview(v.viewinterface):
	std_output_hdl = None

	def init(self, model):
		self.model = model

	def display_menu(self):
		robot_direction = input("""\r\nMove with two characters:
\tColor:\t\t [R]ed, [B]lue, [Y]ellow, [G]reen
\tDirection:\t [N]orth, [S]outh, [E]ast, [W]est
\t""" +("[U]ndo - [R]eset " if len(self.model.move_history) > 0 else "\t\t ") + 
("[S]olve - " if len((self.model.board_section.goals[self.model.goal_index]).robots) == 1 else "") + "[N]ew Game - [Q]uit\r\n""")
		os.system('cls' if os.name == 'nt' else 'clear')
		robot_direction = robot_direction.lower()
		robot = 0
		direction = 0
		if len(robot_direction) == 1:
			if robot_direction == "q":
				self.model.game_state = State.game_over
				return
			elif robot_direction == "r":
				if len(self.model.move_history) > 0:
					self.model.game_state = State.level_restart
					return
			elif robot_direction == "u":
				if len(self.model.move_history) > 0:
					last_move = self.model.move_history.pop(-1)
					self.model.robot_location_update(last_move[0], last_move[2])
					self.model.space_touched_remove_last()
					print("\tReverted move of " + last_move[0].name + " to " + str(last_move[3]))
					return
			elif robot_direction == "s" and len(self.model.board_section.goals[self.model.goal_index].robots) == 1:
				print("Solving...")
				directions = []
				for r in self.model.robots_location:
					lastmove = self.model.move_history_by_robot(r)
					if lastmove is not None:
						directions.append(lastmove[1].value)
					else:
						directions.append(0)

				answer = self.model.solver.generate(
						self.model.robots_location,
						self.model.board_section.goals[self.model.goal_index],
						directions,
						True
					)
				if answer is not None:
					print("Move", end="\t")
					for r in self.model.solver.robot_objects:
						print(r.name, end="\t\t")
					print("")
					for i, move in enumerate(answer):
						print("({0:02d}.".format(i), end=" ")
						for m in move:
							print("({0:02d},".format(m[0] % 16), end=" ")
							print("{0:02d})".format(int(m[0] / 16)), end=" ")
							if m[1] != 0:
								print(next(d for d in Shared.DIRECTIONS if d.value == m[1]), end="\t")
							else:
								print("     ", end="\t")
						print("")
				return
			elif robot_direction == "n":
				self.model.game_state = State.game_restart
				return
		elif len(robot_direction) == 2:
		    #TODO: Fix hardcode
		    if robot_direction[0] == "r":
		        robot = Shared.ROBOTS[0]
		    elif robot_direction[0] == "b":
		        robot = Shared.ROBOTS[1]
		    elif robot_direction[0] == "y":
		        robot = Shared.ROBOTS[2]
		    elif robot_direction[0] == "g":
		        robot = Shared.ROBOTS[3]

		    if robot_direction[1] == "n":
		        direction = Shared.DIRECTIONS[0]
		    elif robot_direction[1] == "s":
		        direction = Shared.DIRECTIONS[1]
		    elif robot_direction[1] == "e":
		        direction = Shared.DIRECTIONS[2]
		    elif robot_direction[1] == "w":
		        direction = Shared.DIRECTIONS[3]

		if robot and direction:
		    print("\tMoving " + robot.name + " in the direction " + direction.name)
		    self.model.robot_move(robot, direction)
		else:
		    print("\t**Command '" + robot_direction + "' is not recognized!**\r\n")

	def handle_events(self):
		if self.model.game_state == State.game_restart:
			os.system('cls' if os.name == 'nt' else 'clear')
			print("SEED?")
			print("\tLeave blank for random generation")
			print("\t'L' for last seed")
			seed = input("")
			if seed.upper() == "L":
			    if self.model.board_section is None:
			        seed = None
			    else:
			        seed = self.model.board_section.key
			self.model.new_game(seed if seed != "" else None)
		elif self.model.game_state == State.level_restart:
			self.model.new_level()
			self.model.game_state = State.play
		elif self.model.game_state == State.play:
			# if level_starttime is None:
			#     level_starttime = time.time()
#			self.model.display_update()
			goal = self.model.board_section.goals[self.model.goal_index]
			for r in Shared.ROBOTS:
			    if r in goal.robots:
			        if goal.point == self.model.robots_location[r]:
			            self.model.game_state = State.level_complete
			if self.model.game_state == State.play:
			    self.display_menu()
		elif self.model.game_state == State.level_complete:
			# self.model.game_time_count += time.time() - level_starttime
			print("\r\nCONGRATS!")
			# print("\t!Level " + str(self.model.goal_index+1) + " of " + str(len(self.model.board_section.goals)) + " completed in " + str(len(self.model.move_history)) + " moves, " + str(time.time() - level_starttime) + " seconds!")
			print("\t!You touched " + str(len(self.model.space_touched)) + " spaces!")
			input("Ready for next level ???")
			os.system('cls' if os.name == 'nt' else 'clear')
			# level_starttime = time.time()
			self.model.game_move_count += len(self.model.move_history)
			self.model.game_space_touched_count += len(self.model.space_touched)
			self.model.robots_starting_location = {}
			for r in self.model.robots_location:
				self.model.robots_starting_location[r] = self.model.robots_location[r]
			self.model.goal_index += 1
			if self.model.goal_index == len(self.model.board_section.goals):
				self.model.game_state = State.game_complete
			else:
				self.model.game_state = State.level_restart
		elif self.model.game_state == State.game_complete:
			print("Game completed - " + str(self.model.goal_index) + " level(s) in " + str(self.model.game_move_count) + " moves, " + str(self.model.game_time_count) + " seconds!")
			print("You touched " + str(self.model.game_space_touched_count) + " spaces!")
			if input("\t[P]lay again?\r\n").lower() == "p":
				self.model.game_state = State.game_restart
			else:
				self.model.game_state = State.game_over
		elif self.model.game_state == State.game_over:
			raise SystemExit

	def update(self):
		pass

	def space_touched_by_xy(self, cell):
		color = 15 if os.name == 'nt' else ''
		for i, s in enumerate(self.model.space_touched):
			if s[1] == cell:
				color = s[2]
		return color

	def color_update(self, color, bgcolor=15 if os.name == 'nt' else 0):
		if os.name == 'nt':
			print("", end="", flush=True)
			if self.std_output_hdl is None:
				STD_OUTPUT_HANDLE_ID = c_ulong(0xfffffff5)
				windll.Kernel32.GetStdHandle.restype = c_ulong
				self.std_output_hdl = windll.Kernel32.GetStdHandle(STD_OUTPUT_HANDLE_ID)
			windll.Kernel32.SetConsoleTextAttribute(self.std_output_hdl, bgcolor | color)
		else:
			print("\033[" + str(bgcolor) + ";" + str(color) + "m", end="")

	def display(self):
		goal = self.model.board_section.goals[self.model.goal_index]
		print("Goal " + str(self.model.goal_index+1) + " of " + str(len(self.model.board_section.goals)) + ": move " + goal.robots[0].name + " to cell(" +(str(goal.point.x)) + ", " + str(goal.point.y) + ")", end="\r\n\t")
		for r in range(0, self.model.board_section.width):
			print(" _", end="")
		print("")
		for j, r in enumerate(self.model.board_section.board):
			print("\t", end="")
			for k, c in enumerate(r):
				point = Point(k, j)
				if c & Shared.DIRECTIONS[3].value == Shared.DIRECTIONS[3].value:
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
				#RODO: South wall
				if c & Shared.DIRECTIONS[1].value == Shared.DIRECTIONS[1].value:
					print("_", end="")
				else:
					print(".", end="")
				self.color_update(0)

				if(k + 1) % 8 == 0 and c & Shared.DIRECTIONS[2].value != Shared.DIRECTIONS[2].value:
					#end of board section and no an east way
					print(" ", end="")
				if(k + 1) % 16 == 0:
					print("|", end="")
					move_count = len(self.model.move_history)
					if move_count > 0:
						if j == 0:
							print("\tPrevious Moves(" + str(move_count) + "):", end="")
						elif move_count >= j:
							last_move = self.model.move_history[-1*j]
							print("\t" + str(move_count-j+1) + ". " + last_move[0].name + " " + last_move[1].name + " from ", end="")
							print(last_move[2], end="")
			print("")
		print("SEED: " + self.model.board_section.key)


	def quit(self):
		pass