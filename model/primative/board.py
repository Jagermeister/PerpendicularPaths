from .shared import Shared
from .point import Point
from .goal import Goal

class Board (object):
    def __init__(self, key, board, goalList):
        self._key = key
        self._board = board
        self._width = len(board)
        self._goals = goalList

    def __str__(self):
        return "\tkey: " + str(self._key) + "; width: " + str(self._width) + """;
\tboard:\r\n\t\t""" + "\r\n\t\t".join([' '.join([str(c) for c in row]) for row in self._board]) + """
\tgoals:\r\n\t\t""" + "\r\n\t\t".join([str(g) for g in self._goals])

    def _set_constant(self):
        raise ConstantValue("Cannot reassign constant value")

    def _get_height_width(self):
        return self._width
    width = height = property (_get_height_width, _set_constant)

    def _get_key(self):
        return self._key
    key = property (_get_key, _set_constant)

    def _get_board(self):
        return self._board
    board = property (_get_board, _set_constant)

    def board_value (self, point):
        return self._board[point.y][point.x]
    def board_update (self, point, value):
        self._board[point.y][point.x] = value

    def _get_goals (self):
        return self._goals
    goals = property (_get_goals, _set_constant)

    def normalize (self):
        for y in range(0, self._width):
            for x in range(0, self._width):
                # print ("(" + str(x) + "," + str(y) + ") -> " + str(self._board[y][x]) + ";\t", end="")
                # if y != 0:
                #     print ("N:" + str(self._board[y-1][x]) + ";", end="\t")
                # else:
                #     print ("", end="\t")
                # if y != (self._width - 1):
                #     print ("S:" + str(self._board[y+1][x]) + ";", end="\t")
                # else:
                #     print ("", end="\t")
                # if x != (self._width - 1):
                #     print ("E:" + str(self._board[y][x+1]) + ";", end="\t")
                # else:
                #     print ("", end="\t")
                # if x != 0:
                #     print ("W:" + str(self._board[y][x-1]) + ";", end="\t")
                # else:
                #     print ("", end="\t")
                if x != 0 and self._board[y][x-1] & Shared.E.value == Shared.E.value:
                    self._board[y][x] |= Shared.W.value
                if x != (self._width - 1) and self._board[y][x+1] & Shared.W.value == Shared.W.value:
                    self._board[y][x] |= Shared.E.value
                if y != 0 and self._board[y-1][x] & Shared.S.value == Shared.S.value:
                    self._board[y][x] |= Shared.N.value
                if y != (self._width - 1) and self._board[y+1][x] & Shared.N.value == Shared.N.value:
                    self._board[y][x] |= Shared.S.value
                # print ("\t==> " + str(self._board[y][x]))
        #input (self._key)

    def rotate (self, iterations=1):
        if iterations > 3:
            iterations = iterations % 4
        if iterations == 0:
            return
        #90 degree rotation per iteration
        for i in range(0, iterations):
            #90 degree rotation of walls, goals
            self._board = [list(x) for x in zip(*self.board[::-1])]
            for j, r in enumerate(self._board):
                for k, c in enumerate(r):
                    for w in Shared.DIRECTIONS:
                        if c & w.value == w.value:
                            self._board[j][k] += w.rotate.value - w.value
            self._goals = [Goal(Point(self.width-1-g.point.y, g.point.x), g.robots) for g in self.goals]
