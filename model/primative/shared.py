from .direction import Direction
from .robot import Robot
import configparser
from os import path

class Shared:
    E = EAST = Direction("East", 0b00000100, 1, 0)
    N = NORTH = Direction("North", 0b00000001, 0, -1, EAST)
    W = WEST = Direction("West", 0b00001000, -1, 0, NORTH)
    S = SOUTH = Direction("South", 0b00000010, 0, 1, WEST)
    EAST.rotate = SOUTH

    DIRECTIONS = [N, S, E, W]

    R = RED = Robot("Red", 0b00010000)
    B = BLUE = Robot("Blue", 0b00100000)
    Y = YELLOW = Robot("Yellow", 0b01000000)
    G = GREEN = Robot("Green", 0b10000000)

    ROBOTS = [R, B, Y, G]

    __config = None
    def config():
        if Shared.__config is None:
            Shared.__config = configparser.ConfigParser()
            file_path = path.relpath("model/config/config.ini")
            with open(file_path) as config_file:
                Shared.__config.read_file(config_file)
        return Shared.__config

    def robot_by_name(name):
        name = name.upper()
        for robot in Shared.ROBOTS:
            if name == robot.name or name == robot.name[0]:
                return robot

    def direction_by_name(name):
        name = name.upper()
        for direction in Shared.DIRECTIONS:
            if name == direction.name or name == direction.name[0]:
                return direction
