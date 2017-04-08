import unittest
from model.primative import Shared, Point, Board, Goal
from model import core

class TestMoveUndo(unittest.TestCase):
    def setUp(self):
        self.pp = core.PerpendicularPaths()
        self.move = (Shared.R, Shared.E, 0, 1)        

    def tearDown(self):
        core.PerpendicularPaths.move_history = []

    def testMoveIsRemoved(self):
        self.pp.move_history.append(self.move)
        self.pp.move_undo()
        self.assertEqual(len(self.pp.move_history), 0)

class TestMoveHistoryByRobot(unittest.TestCase):
    def setUp(self):
        self.pp = core.PerpendicularPaths()
        self.move = (Shared.R, Shared.E, 0, 1)

    def tearDown(self):
        core.PerpendicularPaths.move_history = []

    def testReturnsMove(self):
        self.pp.move_history.append(self.move)
        self.assertEqual(self.pp.move_history_by_robot(Shared.R), self.move)

class TestRobotByCell(unittest.TestCase):
    def setUp(self):
        self.pp = core.PerpendicularPaths()

    def tearDown(self):
        pass

    def testReturnsRobot(self):
        self.assertEqual(self.pp.robot_by_cell(0), Shared.R)

class TestGoal(unittest.TestCase):
    def setUp(self):
        self.pp = core.PerpendicularPaths()
        self.pp.game_new()
        self.pp.game_state = core.State.play

    def tearDown(self):
        pass

    def testReturnsGoal(self):
        self.assertEqual(self.pp.goal(), self.pp.board_section.goals[0])