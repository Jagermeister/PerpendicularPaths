from .shared import Shared
from .point import Point
from .goal import Goal

class Board(object):
    def __init__(self, key, board, goalList):
        self._key = key
        self._board = board
        self._width = len(board)
        self._goals = goalList

    def __str__(self):
        return "\tkey: {}; width: {}; \r\n\tboard:\r\n\t\t{}\r\n\tgoals:\r\n\t\t{}".format(
            self._key,
            self._width,
            "\r\n\t\t".join([' '.join([str(c) for c in row]) for row in self._board]),
            "\r\n\t\t".join([str(g) for g in self._goals]))

    def _get_height_width(self):
        return self._width
    width = height = property(_get_height_width, None)

    def _get_key(self):
        return self._key
    key = property(_get_key, None)

    def _get_board(self):
        return self._board
    board = property(_get_board, None)

    def board_value(self, point):
        return self._board[point.y][point.x]
    def board_update(self, point, value):
        self._board[point.y][point.x] = value

    def _get_goals(self):
        return self._goals
    goals = property(_get_goals, None)

    def normalize(self):
        #when possible, match every 1 sided wall with its pair
        #example a W wall should have a matching E wall next door
        for y in range(0, self._width):
            for x in range(0, self._width):
                if x != 0 and self._board[y][x-1] & Shared.E.value == Shared.E.value:
                    self._board[y][x] |= Shared.W.value
                if x != self._width - 1 and self._board[y][x+1] & Shared.W.value == Shared.W.value:
                    self._board[y][x] |= Shared.E.value
                if y != 0 and self._board[y-1][x] & Shared.S.value == Shared.S.value:
                    self._board[y][x] |= Shared.N.value
                if y != self._width - 1 and self._board[y+1][x] & Shared.N.value == Shared.N.value:
                    self._board[y][x] |= Shared.S.value

    def rotate(self, iterations=1):
        if iterations > 3:
            iterations = iterations % 4
        if iterations == 0:
            return
        #90 degree rotation of walls, goals
        self._board = [list(x) for x in zip(*self.board[::-1])]
        for j, row in enumerate(self._board):
            for k, column in enumerate(row):
                for direction in Shared.DIRECTIONS:
                    if column & direction.value == direction.value:
                        self._board[j][k] += direction.rotate.value - direction.value
        self._goals = [Goal(Point(self.width-1-goal.point.y, goal.point.x), goal.robots)
                       for goal
                       in self.goals
                      ]
        self.rotate(iterations-1)
