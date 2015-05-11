from .point import Point
from .goal import Goal

class Board (object):
    def __init__(self, key, board, walls, goalList):
        self._key = key
        self._board = board
        self._width = len(board)
        self._walls = walls
            #list of blocking directions
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

    def _get_goals(self):
        return self._goals
    goals = property (_get_goals, _set_constant)

    def rotate(self, iterations=1):
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
                    for w in self._walls:
                        if c & w.direction.value == w.direction.value:
                            self._board[j][k] += w.direction.rotate.value - w.direction.value
            self._goals = [Goal(Point(self.width-1-g.point.y, g.point.x), g.robots) for g in self.goals]
