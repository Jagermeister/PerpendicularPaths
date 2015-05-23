from .direction import Direction
class Wall(object):
    name = ""
    direction = None

    def __init__(self, name, direction):
        assert isinstance(name, str)
        self.name = name.upper()
        assert isinstance(direction, Direction)
        self.direction = direction
