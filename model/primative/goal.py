"""Struct for goal point on board"""
from .point import Point

class Goal(object):
    """couple a point with list of winning objects"""

    def __init__(self, point, robotList):
        """require valid instances"""
        assert isinstance(point, Point)
        self.point = point
        assert isinstance(robotList, list)
        self.robots = robotList

    def __str__(self):
        """debug output"""
        stringout = ""
        for robot in self.robots:
            stringout += robot.__str__()
        stringout += " at " + self.point.__str__()
        return stringout
