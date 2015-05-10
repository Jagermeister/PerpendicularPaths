#    N = NORTH =  0b00000001
#    S = SOUTH =  0b00000010
#    E = EAST =   0b00000100
#    W = WEST =   0b00001000
class Direction (object):
    name = ""
    rotate = None
    value = 0
    #base 1 unique id
    x_delta = 0
    y_delta = 0

    def __init__ (self, name, value, x_delta, y_delta, rotate = None):
        assert isinstance(name, str)
        self.name = name
        assert isinstance(value, int)
        self.value = value
        assert isinstance(x_delta, int)
        self.x_delta = x_delta
        assert isinstance(y_delta, int)
        self.y_delta = y_delta
        assert rotate is None or isinstance(rotate, Direction)
        self.rotate = rotate

    def reverse(self):
        assert self.rotate is not None
        return self.rotate.rotate
