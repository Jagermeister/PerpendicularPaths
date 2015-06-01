from .direction import Direction
from .robot import Robot
import configparser
from os import path

class Shared:
    E = EAST = Direction("East", 4, 1, 0)
    N = NORTH = Direction("North", 1, 0, -1, EAST)
    W = WEST = Direction("West", 8, -1, 0, NORTH)
    S = SOUTH = Direction("South", 2, 0, 1, WEST)
    EAST.rotate = SOUTH
    DIRECTIONS = [N, S, E, W]

    R = RED = Robot("Red", 16)
    B = BLUE = Robot("Blue", 32)
    Y = YELLOW = Robot("Yellow", 64)
    G = GREEN = Robot("Green", 128)
    O = ORANGE = Robot("Orange", 256)
    P = PURPLE = Robot("Purple", 512)
    V = SILVER = Robot("Silver", 1024)
    ROBOTS = [R, B, Y, G]
    EXPAND = [V]
    LUNARL = [O, P]

    __config = None
    def config():
        """Load our config.ini file which has our settings as key=value"""
        if Shared.__config is None:
            Shared.__config = configparser.ConfigParser()
            file_path = path.relpath("model/config/config.ini")
            with open(file_path) as config_file:
                Shared.__config.read_file(config_file)
        return Shared.__config

    def robot_by_name(name):
        #TODO pass in which robots to use
        name = name.upper()
        for robot in Shared.ROBOTS:
            if name == robot.name or name == robot.name[0]:
                return robot

    def direction_by_name(name):
        name = name.upper()
        for direction in Shared.DIRECTIONS:
            if name == direction.name or name == direction.name[0]:
                return direction
