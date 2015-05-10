from primative import Direction
class Point (object):
    x = 0
    y = 0

    def __init__ (self, x, y):
        assert isinstance(x, int)
        self.x = x
        assert isinstance(y, int)
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def move(self, direction):
        assert isinstance(direction, Direction)
        self.x += direction.x_delta
        self.y += direction.y_delta
