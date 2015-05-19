from .point import	Point

class Goal (object):
	def __init__(self, point, robotList):
		assert isinstance(point, Point)
		self.point = point
		assert isinstance(robotList, list)
		self.robots = robotList

	def __str__(self):
		stringout = ""
		for r in self.robots:
			stringout += r.__str__()
		stringout += " at " + self.point.__str__()
		return stringout