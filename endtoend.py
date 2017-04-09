"""Entry point for end to end test"""
from view import viewfactory as vf
from model import core as pp
from model.primative import Shared, Robot, Direction

'''test library classes'''

class TestSuite(object):
    def __init__(self, core, view):
        self.core = core
        self.view = view
        self.cases = []

    def addCase(self, case):
        self.cases.append(case)

    def execute(self):
        if len(self.cases) > 0:
            if len(self.cases[0].events) > 0:
                self.cases[0].execute()
            else: # no event cases left to execute
                self.cases[0].runTests()
                self.cases[0].displayResult()
                self.cases.pop(0)
        else:
            #currently quits after all cases are evaluated
            #there needs to be some tear down between cases
            quit()

class TestCase(object):
    def __init__(self, name, core, view):
        self.name = name
        self.core = core
        self.view = view
        self.events = []
        self.result = []

    def addEvent(self, event):
        self.events.append(event)

    def execute(self):
        # you're doing a first in first out queue
        # pop() may not be the most efficient option
        # maybe each event should execute their own actions
        if len(self.events) > 0:
            event = self.events.pop(0)
            for action in event.actions:
                action.execute()

    def locationTest(self):
        # this should not be a part of every TestCase
        if self.core.robots_location[Shared.R].x == 0 and self.core.robots_location[Shared.R].y == 1:
            self.result.append("Location of Red Robot --- PASS")
        else:
            self.result.append("Location of Red Robot --- FAIL")
        if self.core.robots_location[Shared.B].x == 2 and self.core.robots_location[Shared.B].y == 6:
            self.result.append("Location of Blue Robot --- PASS")
        else:
            self.result.append("Location of Blue Robot --- FAIL")
        if self.core.robots_location[Shared.Y].x == 11 and self.core.robots_location[Shared.Y].y == 5:
            self.result.append("Location of Yellow Robot --- PASS")
        else:
            self.result.append("Location of Yellow Robot --- FAIL")
        if self.core.robots_location[Shared.G].x == 15 and self.core.robots_location[Shared.G].y == 5:
            self.result.append("Location of Green Robot --- PASS")
        else:
            self.result.append("Location of Green Robot --- FAIL")

    def moveCountTest(self):
        # this should not be a part of every TestCase        
        if self.core.game_move_count == 9:
            self.result.append("Move count --- PASS")
        else:
            self.result.append("Move count --- FAIL")

    def runTests(self):
        # this is needs to be moved out
        self.locationTest()
        self.moveCountTest()

    def displayResult(self):
        print(self.name)
        for result in self.result:
            print(result)

class Event(object):
    def __init__(self):
        self.actions = []

    def addAction(self, action):
        self.actions.append(action)

class Action(object):
    def __init__(self):
        pass

    def execute(self):
        pass

'''app specific implementations'''

class StartNewGame(Action):
    def __init__(self, core, view):
        super().__init__()
        self.core = core
        self.view = view

    def execute(self):
        '''core.py -> PerpendicularPaths.game_new() takes optional parameter seed
        seed in the format of {BoardSectionKey}*4 + ! +
        {ObjectName}[0]{Point}*4 + ! + {GoalObjectName}[0]{GoalPoint}
        Example: A1A2A3A4!R0301B0415G0005Y1213!YBGR1203|B1515
            BoardSection: A1A2A3A4
            Object Point: R0301B0415G0005Y1213
            Goal Objects: YBGR1203|B1515
        PerpendicularPaths.game_new() is called from nativeview.py -> NativeView.init()
        '''
        self.core.game_new(seed="A2C2A2B4!B0905R0001Y1306G1505!B0206|Y0604|G1014|B1205|R0102")
        self.view.draw_level()

class RobotMove(Action):
    def __init__(self, core, view, robot, direction):
        super().__init__()
        assert isinstance(robot, Robot)
        assert isinstance(direction, Direction)
        self.core = core
        self.view = view
        self.robot = robot
        self.direction = direction

    def execute(self):
        '''code is referenced from nativeview.py handle_events release left click
        the referenced code SHOULD be substantially more modular
        If any changes are made to the view these tests will break'''
        self.view.desired_move = self.direction
        robot = self.view.robot_object_to_sprite(self.robot)
        #begin code from view
        start_position = self.core.robots_location[robot.robot_object]
        move_result = self.core.robot_move(robot.robot_object, self.view.desired_move)
        if move_result == pp.PPMoveStatus.MOVE_SUCCESS:
            point = self.core.robots_location[robot.robot_object]
            distance = abs(start_position.x - point.x + start_position.y - point.y)
            robot.set_final_destination(self.view.board_cell_to_pixel(point), distance)
            self.view.desired_move = None
            self.view.add_move_to_history()
            self.view.space_touched_add_move(self.core.move_history[-1])

''' code to actually run this
this will definitely change and become modular!
creating the actions will be redundant, this is the only part that can be
but maybe make all those three lines into one liners'''
def buildSuite(core, view):
    suite = TestSuite(core, view)
    caseA = TestCase("Move to goal", core, view)

    eventA = Event()
    eventA.addAction(StartNewGame(core, view))
    caseA.addEvent(eventA)

    eventB = Event()
    eventB.addAction(RobotMove(core, view, Shared.Y, Shared.E))
    caseA.addEvent(eventB)

    eventC = Event()
    eventC.addAction(RobotMove(core, view, Shared.Y, Shared.S))
    caseA.addEvent(eventC)

    eventD = Event()
    eventD.addAction(RobotMove(core, view, Shared.Y, Shared.W))
    caseA.addEvent(eventD)

    eventE = Event()
    eventE.addAction(RobotMove(core, view, Shared.Y, Shared.N))
    caseA.addEvent(eventE)

    eventF = Event()
    eventF.addAction(RobotMove(core, view, Shared.Y, Shared.E))
    caseA.addEvent(eventF)

    eventG = Event()
    eventG.addAction(RobotMove(core, view, Shared.B, Shared.E))
    caseA.addEvent(eventG)

    eventH = Event()
    eventH.addAction(RobotMove(core, view, Shared.B, Shared.S))
    caseA.addEvent(eventH)

    eventI = Event()
    eventI.addAction(RobotMove(core, view, Shared.B, Shared.W))
    caseA.addEvent(eventI)

    eventJ = Event()
    eventJ.addAction(RobotMove(core, view, Shared.B, Shared.N))
    caseA.addEvent(eventJ)

    suite.addCase(caseA)
    return suite


def main():
    """simple game loop to link a view with our model logic"""
    model = pp.PerpendicularPaths()
    view = vf.factory_create()
    view.init(model)
    suite = buildSuite(model, view) #ADDED FOR TESTING
    while 1:
        suite.execute() #ADDED FOR TESTING
        view.handle_events()
        view.update()
        view.display()
    view.quit()

if __name__ == '__main__':
    main()