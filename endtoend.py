"""Entry point for end to end test"""
from view import viewfactory as vf
from model import core as pp
from model.primative import Shared, Robot, Direction
import pygame, time
from pygame.locals import *

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
            #pass

class TestCase(object):
    def __init__(self, name, core, view):
        self.name = name
        self.core = core
        self.view = view
        self.events = []
        self.result = []
        self.waitTime = 0
        self.previousTime = 0

    def addEvent(self, event):
        self.events.append(event)

    def execute(self):
        # you're doing a first in first out queue
        # pop() may not be the most efficient option
        # maybe each event should execute their own actions
        if len(self.events) > 0:
            if self.waitTime <= 0:
                event = self.events.pop(0)
                for action in event.actions:
                    action.execute()
                self.waitTime = event.waitAfter
                self.previousTime = pygame.time.get_ticks()
            else:
                self.waitTime -= pygame.time.get_ticks() - self.previousTime
                self.previousTime = pygame.time.get_ticks()

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
    def __init__(self, waitAfter):
        self.actions = []
        self.waitAfter = waitAfter # time in milliseconds to wait AFTER the event before the next

    def addAction(self, action):
        self.actions.append(action)

class Action(object):
    def __init__(self):
        pass

    def execute(self):
        pass

'''app specific implementations'''

class StartNewGame(Action):
    '''This has not been switched to event input based
    the new game button on the view does not allow input of a seed'''
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

class MouseButtonEvent(Action):
    '''Add a pygame mouse button event to the queue
    <Event(5-MouseButtonDown {'button': 1, 'pos': (373, 407)})>
    <Event(6-MouseButtonUp {'pos': (625, 292), 'button': 1})>
    types:
    5 = MouseButtonDown
    6 = MouseButtonUp
    {
    pos:
    (x, y)
    button:
    1 = left mouse
    }
    '''
    def __init__(self, eventType, button, pos):
        super().__init__()
        self.type = eventType
        self.button = button
        self.pos = pos

    def execute(self):
        pygame.event.post(pygame.event.Event(self.type, {'button': self.button, 'pos': self.pos}))

class MouseMotionEvent(Action):
    '''Add a pygame mouse motion event to the queue
    type:
    4 = MouseMotion
    click was at: <Event(5-MouseButtonDown {'pos': (583, 296), 'button': 1})>
    motion:
    <Event(4-MouseMotion {'pos': (583, 295), 'rel': (0, -1), 'buttons': (1, 0, 0)})>
    <Event(4-MouseMotion {'pos': (583, 277), 'rel': (0, -18), 'buttons': (1, 0, 0)})>
    <Event(4-MouseMotion {'pos': (583, 261), 'rel': (0, -16), 'buttons': (1, 0, 0)})>
    <Event(4-MouseMotion {'pos': (583, 250), 'rel': (0, -11), 'buttons': (1, 0, 0)})>
    pos = location after move
    rel = distance moved
    buttons = what is clicked while moving?
    '''
    def __init__(self, pos, rel, buttons):
        super().__init__()
        self.type = 4
        self.pos = pos
        self.rel = rel
        self.buttons = buttons

    def execute(self):
        pygame.event.post(pygame.event.Event(self.type, {'pos': self.pos, 'rel': self.rel, 'buttons': self.buttons}))

''' code to actually run this
this will definitely change and become modular!
creating the actions will be redundant, this is the only part that can be
but maybe make all those three lines into one liners'''
def buildSuite(core, view):
    suite = TestSuite(core, view)
    caseA = TestCase("Move to goal", core, view)

    eventA = Event(0)
    eventA.addAction(StartNewGame(core, view))
    caseA.addEvent(eventA)

    eventB = Event(1000)
    eventB.addAction(MouseButtonEvent(5, 1, (583, 301)))
    eventB.addAction(MouseMotionEvent((584, 301), (1, 0), (1, 0, 0)))
    eventB.addAction(MouseButtonEvent(6, 1, (584, 301)))
    caseA.addEvent(eventB)

    eventC = Event(1000)
    eventC.addAction(MouseButtonEvent(5, 1, (663, 304)))
    eventC.addAction(MouseMotionEvent((663, 305), (0, 1), (1, 0, 0)))
    eventC.addAction(MouseButtonEvent(6, 1, (663, 305)))
    caseA.addEvent(eventC)

    eventD = Event(1000)
    eventD.addAction(MouseButtonEvent(5, 1, (657, 498)))
    eventD.addAction(MouseMotionEvent((654, 498), (-3, 0), (1, 0, 0)))
    eventD.addAction(MouseButtonEvent(6, 1, (654, 498)))
    caseA.addEvent(eventD)

    eventE = Event(1000)
    eventE.addAction(MouseButtonEvent(5, 1, (461, 499)))
    eventE.addAction(MouseMotionEvent((461, 487), (0, 12), (1, 0, 0)))
    eventE.addAction(MouseButtonEvent(6, 1, (461, 487)))
    caseA.addEvent(eventE)

    eventF = Event(1000)
    eventF.addAction(MouseButtonEvent(5, 1, (458, 261)))
    eventF.addAction(MouseMotionEvent((459, 261), (0, 1), (1, 0, 0)))
    eventF.addAction(MouseButtonEvent(6, 1, (459, 261)))
    caseA.addEvent(eventF)

    eventG = Event(1000)
    eventG.addAction(MouseButtonEvent(5, 1, (416, 260)))
    eventG.addAction(MouseMotionEvent((426, 260), (10, 2), (1, 0, 0)))
    eventG.addAction(MouseButtonEvent(6, 1, (426, 260)))
    caseA.addEvent(eventG)

    eventH = Event(1000)
    eventH.addAction(MouseButtonEvent(5, 1, (455, 261)))
    eventH.addAction(MouseMotionEvent((455, 264), (0, 3), (1, 0, 0)))
    eventH.addAction(MouseButtonEvent(6, 1, (455, 264)))
    caseA.addEvent(eventH)

    eventI = Event(1000)
    eventI.addAction(MouseButtonEvent(5, 1, (460, 580)))
    eventI.addAction(MouseMotionEvent((448, 580), (-12, 0), (1, 0, 0)))
    eventI.addAction(MouseButtonEvent(6, 1, (448, 580)))
    caseA.addEvent(eventI)

    eventJ = Event(1000)
    eventJ.addAction(MouseButtonEvent(5, 1, (138, 578)))
    eventJ.addAction(MouseMotionEvent((138, 569), (0, -9), (1, 0, 0)))
    eventJ.addAction(MouseButtonEvent(6, 1, (138, 569)))
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