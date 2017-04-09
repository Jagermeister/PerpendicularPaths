"""Entry point for end to end test"""
from view import viewfactory as vf
from model import core as pp
from model.primative import Shared, Robot, Direction

class EndToEndTest(object):
    def __init__(self, core, view):
        self.core = core
        self.view = view
        self.events = []
        self.robot = None
        self.direction = None
        self.result = []

    def gameNew(self):
        '''starts a new game in the core'''
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

    def setRobotR(self):
        self.robot = Shared.R

    def setRobotB(self):
        self.robot = Shared.B

    def setRobotY(self):
        self.robot = Shared.Y

    def setRobotG(self):
        self.robot = Shared.G

    def setDirectionE(self):
        self.direction = Shared.E

    def setDirectionN(self):
        self.direction = Shared.N

    def setDirectionW(self):
        self.direction = Shared.W

    def setDirectionS(self):
        self.direction = Shared.S

    def moveRobot(self, coreRobot=None, direction=None):
        '''coreRobot = Robot object -- direction = Shared.E etc
        code is referenced from nativeview.py handle_events release left click
        the referenced code SHOULD be substantially more modular
        If any changes are made to the view these tests will break'''
        if coreRobot is None or isinstance(coreRobot, Robot) is False:
            coreRobot = self.robot
        if direction is None or isinstance(direction, Direction) is False:
            direction = self.direction
        self.view.desired_move = direction
        robot = self.view.robot_object_to_sprite(coreRobot)

        start_position = self.core.robots_location[robot.robot_object]
        move_result = self.core.robot_move(robot.robot_object, self.view.desired_move)
        if move_result == pp.PPMoveStatus.MOVE_SUCCESS:
            point = self.core.robots_location[robot.robot_object]
            distance = abs(start_position.x - point.x + start_position.y - point.y)
            robot.set_final_destination(self.view.board_cell_to_pixel(point), distance)
            self.view.desired_move = None
            self.view.add_move_to_history()
            self.view.space_touched_add_move(self.core.move_history[-1])

    def tearDown(self):
        self.robot = None
        self.direction = None

    def locationTest(self):
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
        if self.core.game_move_count == 9:
            self.result.append("Move count --- PASS")
        else:
            self.result.append("Move count --- FAIL")            

    def displayResult(self):
        for result in self.result:
            print(result)
        quit()

    def addEvent(self):
        self.events.append([self.gameNew])
        self.events.append([self.setRobotY, self.setDirectionE, self.moveRobot, self.tearDown])
        self.events.append([self.setRobotY, self.setDirectionS, self.moveRobot, self.tearDown])
        self.events.append([self.setRobotY, self.setDirectionW, self.moveRobot, self.tearDown])
        self.events.append([self.setRobotY, self.setDirectionN, self.moveRobot, self.tearDown])
        self.events.append([self.setRobotY, self.setDirectionE, self.moveRobot, self.tearDown])
        self.events.append([self.setRobotB, self.setDirectionE, self.moveRobot, self.tearDown])
        self.events.append([self.setRobotB, self.setDirectionS, self.moveRobot, self.tearDown])
        self.events.append([self.setRobotB, self.setDirectionW, self.moveRobot, self.tearDown])
        self.events.append([self.setRobotB, self.setDirectionN, self.moveRobot, self.tearDown])
        self.events.append([self.locationTest, self.moveCountTest])
        self.events.append([self.displayResult])

    def runEvents(self):
        if len(self.events) > 0:
            # you're doing a first in first out queue
            # pop() may not be the most efficient option
            for event in self.events[0]:
                event()
            self.events.pop(0)

def main():
    """simple game loop to link a view with our model logic"""
    model = pp.PerpendicularPaths()
    view = vf.factory_create()
    view.init(model)
    test = EndToEndTest(model, view)
    test.addEvent()
    while 1:
        test.runEvents()
        view.handle_events()
        view.update()
        view.display()
    view.quit()

if __name__ == '__main__':
    main()