from ctypes import *
import os
import copy
import json
import random
from .primative import *

class BoardGenerator(object):
    #board
    board_sections = []

    def __init__ (self):
        n = Shared.N.value
        s = Shared.S.value
        e = Shared.E.value
        w = Shared.W.value

        empty = [0]*8
        for i in range (len(empty)):
            if i == 0:
                empty[i] = [n|w, n, n, n, n, n, n, n]
            elif i == 7:
                empty[i] = [w, 0, 0, 0, 0, 0, 0, w|n]
            else:
                empty[i] = [w, 0, 0, 0, 0, 0, 0, 0]
        
        with open('model/config/board.json') as data_file:
            data = json.load(data_file)
            for i, section in enumerate(data):
                if section["type"] == "classic":
                    #N along top, W along left, NW@7,7
                    goalList = []
                    for goal in section["goals"]:
                        robotList = []
                        for robot in goal[2]:
                            if robot == "R":
                                robotList.append (Shared.R)
                            if robot == "Y":
                                robotList.append (Shared.Y)
                            if robot == "B":
                                robotList.append (Shared.B)
                            if robot == "G":
                                robotList.append (Shared.G)
                        goalList.append (Goal(Point (goal[0], goal[1]), robotList))
                    board = Board (
                            section["id"],
                            copy.deepcopy (empty),
                            goalList
                        )
                    for wall in section["walls"]:
                        value = 0
                        for direction in wall[2]:
                            if direction == "N":
                                value |= n
                            if direction == "S":
                                value |= s
                            if direction == "E":
                                value |= e
                            if direction == "W":
                                value |= w
                        board._board[wall[1]][wall[0]] |= value
                    board.normalize()
                    #patch walls giving every N a neighbor S
                    self.board_sections.append (board)

        assert len(self.board_sections) >= 4

    def random_section (self):
        random.shuffle (self.board_sections)
        return copy.deepcopy (self.board_sections[0])

    def generate (self, key=None):
        board_top = []
        board_bot = []
        sections = []
        keys = []
        if key is not None:
            keys = key.split("_")[:4]
        
        for i in range (len(keys), 4):
            keys.append("")

        for k in keys:
            match = [s for s in self.board_sections if s.key == k]
            if len(match) > 0:
                sections.append (copy.deepcopy (match[0]))
            else:
                sections.append (self.random_section())

        assert len(sections) == 4
        for i, s in enumerate (sections):
            s.rotate(i)

        #put together: 1@0d + 2@90d + 3@180d + 4@270d
        for x in range(0, 8):
            board_top.append (sections[0].board[x] + sections[1].board[x])
            board_bot.append (sections[3].board[x] + sections[2].board[x])
        board_top.extend (board_bot)
        #goals have to have x,y updated based on region
        goals = sections[0].goals + [Goal(Point(g.point.x + 8, g.point.y), g.robots) for g in sections[1].goals]
        goals += [Goal(Point(g.point.x + 8, g.point.y + 8), g.robots) for g in sections[2].goals]
        goals += [Goal(Point(g.point.x, g.point.y + 8), g.robots) for g in sections[3].goals]
        board = Board(
                "_".join([str(s.key) for s in sections]),
                board_top,
                goals
            )
        board.normalize()
        return board