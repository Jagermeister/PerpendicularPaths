from ctypes import *
import os
import copy
import random
from primative import *

class BoardGenerator(object):
    #board
    board_width = 16
    section_width = 8

    board_sections = []

    walls = []
    directions = []
    robots = []

    def __init__ (self):
        #TODO: Directions, Walls, Robots should all be 
        # configurations read from a file
        east = Direction ("East", 0b00000100, 1, 0)
        north = Direction ("North", 0b00000001, 0, -1, east)
        west = Direction ("West", 0b00001000, -1, 0, north)
        south = Direction ("South", 0b00000010, 0, 1, west)
        east.rotate = south

        self.directions = [
                north,
                south,
                east,
                west
            ]

        self.walls = [
                Wall ("North", north),
                Wall ("South", south),
                Wall ("East", east),
                Wall ("West", west)
            ]

        self.robots = [
                Robot ("Red", 0b00010000),
                Robot ("Blue", 0b00100000),
                Robot ("Yellow", 0b01000000),
                Robot ("Green", 0b10000000)
            ]
        self.__board_sections_load()

    def __board_sections_load (self):
        board_section_key = 0
        n = self.directions[0].value
        s = self.directions[1].value
        e = self.directions[2].value
        w = self.directions[3].value
        r = self.robots[0]
        b = self.robots[1]
        y = self.robots[2]
        g = self.robots[3]
        #board sections described with the center
        #piece being in the bottom right (SE) corner
        #this is so all sections start same orientation
        # aka the last row, last cell should be "w|n"
        #TODO: load sections from file?
        board_section_key += 1
        self.board_sections.append (
            Board (
                board_section_key,
                [
                    [w|n,n,n,n,n|e,w|n,n,n],
                    [w,s,0,0,0,0,s|e,w],
                    [w|e,w|n,0,0,0,0,n,0],
                    [w,0,0,0,0,0,0,0],
                    [w,0,0,0,0,0,s,0],
                    [w|s,0,0,0,0,0,n|e,w],
                    [w|n,0,e,w|s,0,0,0,s],
                    [w,0,0,n,0,0,e,w|n]
                ],
                self.walls,
                [
                    Goal(Point(6,1), [y]),
                    Goal(Point(1,2), [g]),
                    Goal(Point(6,5), [b]),
                    Goal(Point(3,6), [r])
                ]
             )
        )
        board_section_key += 1
        self.board_sections.append(
            Board (
                board_section_key,
                [
                    [w|n,n,s|n,n,n|e,w|n,n,n],
                    [w,e,w|n,0,0,0,0,0],
                    [w,0,0,0,0,0,0,0],
                    [w,0,0,0,0,e,w|s,0],
                    [w|s,0,0,0,s,0,n,0],
                    [w|n,0,0,0,n|e,w,0,0],
                    [w,s|e,w,0,0,0,0,s],
                    [w,0,0,0,0,0,e,w | n]
                ],
                self.walls,
                [
                    Goal(Point(2,1), [y]),
                    Goal(Point(6,3), [b]),
                    Goal(Point(4,5), [r]),
                    Goal(Point(1,6), [g])
                ]
            )
        )
        board_section_key += 1
        self.board_sections.append(
            Board (
                board_section_key,
                [
                    [w|n,n,n,n|e,w|n,n,n,n],
                    [w|e,w|s,0,0,0,0,s,0],
                    [w,n,0,0,0,0,n|e,w],
                    [w,0,0,0,0,0,0,0],
                    [w,0,s|e,0,0,0,0,s],
                    [w|s,0,n,0,0,0,e,w|n],
                    [w|n,0,0,0,0,0,0,s],
                    [w,0,0,0,0,0,e,w|n]
                ],
                self.walls,
                [
                    Goal(Point(1,1), [r]),
                    Goal(Point(6,2), [g]),
                    Goal(Point(2,4), [b]),
                    Goal(Point(7,5), [y])
                ]
            )
        )
        board_section_key += 1
        self.board_sections.append(
            Board (
                board_section_key,
                [
                    [w|n,n,n,n,n|e,w|n,n,n],
                    [w,0,s|e,w,0,0,0,0],
                    [w,0,n,0,0,0,0,0],
                    [w|e,w|s,0,0,0,0,s,0],
                    [w|s,n,0,0,0,e,w|n,0],
                    [w|n,0,0,0,0,s,0,0],
                    [w,0,0,0,0,n|e,w,s],
                    [w,0,0,s|e,w,0,e,w|n]
                ],
                self.walls,
                [
                    Goal(Point(2,1), [r]),
                    Goal(Point(1,3), [g]),
                    Goal(Point(6,4), [y]),
                    Goal(Point(5,6), [b]),
                    Goal(Point(3,7), [r,b,y,g])
                ]
            )
        )

    def generate (self, key = None):
        board_top = []
        board_bot = []
        sections = []
        if key is None:
            sections = copy.copy (self.board_sections)
            random.shuffle (sections)
            sections = sections[:4]
        else:
            for k in key.split("_"):
                sections.append (copy.copy (next(s for s in self.board_sections if s.key == int(k))))

        for i, s in enumerate (sections):
            s.rotate(i)

        #put together: 1@0d + 2@90d + 3@180d + 4@270d
        for x in range(0, 8):
            board_top.append (sections[0].board[x] + sections[1].board[x])
            board_bot.append (sections[3].board[x] + sections[2].board[x])
        board_top.extend (board_bot)
        #patch board walls together
        for j, r in enumerate (board_top):
            for k, c in enumerate (r):
                if (j + 1 < self.board_width - 1 and
                    board_top[j][k] & self.directions[1].value == self.directions[1].value and
                    board_top[j+1][k] & self.directions[0].value != self.directions[0].value):
                    #if the next row is available, make sure we have matching S, N
                    board_top[j+1][k] += self.directions[0].value
                if (k + 1 < self.board_width - 1 and
                    board_top[j][k] & self.directions[2].value == self.directions[2].value and
                    board_top[j][k+1] & self.directions[3].value != self.directions[3].value):
                    #if the next col is available, make sure we have matching E, W
                    board_top[j][k+1] += self.directions[3].value
        #goals have to have x,y updated based on region
        goals = sections[0].goals + [Goal(Point(g.point.x + 8, g.point.y), g.robots) for g in sections[1].goals]
        goals += [Goal(Point(g.point.x + 8, g.point.y + 8), g.robots) for g in sections[2].goals]
        goals += [Goal(Point(g.point.x, g.point.y + 8), g.robots) for g in sections[3].goals]
        return Board(
                "_".join([str(s.key) for s in sections]),
                board_top,
                self.walls,
                goals
            )