"""Representation of a board with goals"""
from .shared import Shared
from .point import Point
from .goal import Goal

class Board(object):
    """Encapsulate matrix and goals"""

    def __init__(self, key, board, goalList):
        """matrix and goal list"""
        self._key = key
        self._board = board
        self._width = len(board)
        self._goals = goalList

    def __str__(self):
        """override string output for debug"""
        return "\tkey: {}; width: {}; \r\n\tboard:\r\n\t\t{}\r\n\tgoals:\r\n\t\t{}".format(
            self._key,
            self._width,
            "\r\n\t\t".join([' '.join([str(c) for c in row]) for row in self._board]),
            "\r\n\t\t".join([str(g) for g in self._goals]))

    def _get_height_width(self):
        """"width getter"""
        return self._width
    width = height = property(_get_height_width, None)

    def _get_key(self):
        """"key getter"""
        return self._key
    key = property(_get_key, None)

    def _get_board(self):
        """"board getter"""
        return self._board
    board = property(_get_board, None)

    def board_value(self, point):
        """"board value getter"""
        return self._board[point.y][point.x]
    def board_update(self, point, value):
        """"board value setter"""
        self._board[point.y][point.x] = value

    def _get_goals(self):
        """"goal list getter"""
        return self._goals
    goals = property(_get_goals, None)

    def normalize(self):
        """when possible, match every 1 sided wall with its pair
        example a W wall should have a matching E wall next door"""
        for col in range(0, self._width):
            for row in range(0, self._width):
                if row != 0 and self._board[col][row-1] & Shared.E.value:
                    self._board[col][row] |= Shared.W.value
                if row != self._width - 1 and self._board[col][row+1] & Shared.W.value:
                    self._board[col][row] |= Shared.E.value
                if col != 0 and self._board[col-1][row] & Shared.S.value:
                    self._board[col][row] |= Shared.N.value
                if col != self._width - 1 and self._board[col+1][row] & Shared.N.value:
                    self._board[col][row] |= Shared.S.value

    def rotate(self, iterations=1):
        """'iterations'*90degree rotation of matrix values and goals"""
        if iterations > 3:
            iterations = iterations % 4
        if iterations == 0:
            return
        #90 degree rotation of walls, goals
        self._board = [list(x) for x in zip(*self.board[::-1])]
        for j, row in enumerate(self._board):
            for k, column in enumerate(row):
                for direction in Shared.DIRECTIONS:
                    if column & direction.value:
                        self._board[j][k] += direction.rotate.value - direction.value
        self._goals = [Goal(Point(self.width-1-goal.point.y, goal.point.x), goal.robots)
                       for goal
                       in self.goals
                      ]
        self.rotate(iterations-1)
