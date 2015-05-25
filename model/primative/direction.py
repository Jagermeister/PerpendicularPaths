"""Representing possible orientation of object on board"""
class Direction(object):
    """basic properties for name and deltas for travel"""
    name = ""
    rotate = None
    value = 0
    #base 1 unique id
    x_delta = 0
    y_delta = 0

    def __init__(self, name, value, x_delta, y_delta, rotate=None):
        """ensure data requirements met before assignment"""
        assert isinstance(name, str)
        assert len(name) > 0
        self.name = name
        assert isinstance(value, int)
        self.value = value
        assert isinstance(x_delta, int)
        self.x_delta = x_delta
        assert isinstance(y_delta, int)
        self.y_delta = y_delta
        assert rotate is None or isinstance(rotate, Direction)
        self.rotate = rotate

    def __str__(self): 
        """debug output of name"""
        return self.name.rjust(5)

    def reverse(self):
        """180 degree rotation of self"""
        assert self.rotate is not None
        return self.rotate.rotate

    def rotate(self):
        """90 degree rotation of self"""
        assert self.rotate is not None
        return self.rotate
