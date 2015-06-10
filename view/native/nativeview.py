"""View for native graphics like lines, circles, and rectangles"""
from view import viewinterface as v
import pygame
from pygame.locals import *
import os
from model.primative import Point, Shared

class Robot(pygame.sprite.Sprite):
    def __init__(self, color, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10,10])
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = position
        pygame.draw.circle(self.image, color, (5, 5), 5, 0)

class Wall(pygame.sprite.Sprite):
    def __init__(self, direction, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([25,25])
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = position
        if direction == Shared.W.value:
            pygame.draw.line(self.image, NativeView.BLACK, [0,0], [0,20], 4)
        elif direction == Shared.S.value:
            pygame.draw.line(self.image, NativeView.BLACK, [0,20], [20,20], 4)

class NativeView(v.ViewInterface):
    """Leverage pygame framework for drawing of primative objects"""
    screen = None
    background = None
    model = None
    board = None
    robots = None
    wall_group = pygame.sprite.Group()
    robot_group = pygame.sprite.Group()

    # RGB Colors
    BLACK = (  0,   0,   0)
    WHITE = (255, 255, 255)
    BLUE =  (  0,   0, 255)
    GREEN = (  0, 255,   0)
    RED =   (255,   0,   0)
    YELLOW =(255, 255,   0)
    PURPLE =(255,   0, 255)
    TRANS  =(  1,   1,   1)
    GRAY   =(211, 211, 211)

    SIZE = width, height = 600, 600

    def init(self, model):
        """Initialize screen"""
        self.model = model
        model.game_new()        
        pygame.init()
        self.screen = pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption('Perpendicular Paths')

        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(self.WHITE)

        # Draw the board, robots, and goal
        self.board = pygame.Surface((321,321))
        self.board = self.board.convert()
        self.board.fill(self.GRAY)
        self.robots = pygame.Surface((320,320))
        self.robots = self.robots.convert()
        self.robots.set_colorkey(self.TRANS)
        self.robots.fill(self.TRANS)
        pygame.draw.rect(self.board, self.BLACK, [0,0,320,320], 4)
        for i in range (1,16):
            pygame.draw.line(self.board, self.BLACK, [i*20, 0], [i*20, 320], 1)
            pygame.draw.line(self.board, self.BLACK, [0, i*20], [320, i*20], 1)
        for j, row in enumerate(self.model.board_section.board):
            for k, cell in enumerate(row):
                point = Point(k, j)
                if cell & Shared.W.value:
                    self.wall_group.add(Wall(Shared.W.value, (point.x*20+10, point.y*20+10)))
                if cell & Shared.S.value:
                    self.wall_group.add(Wall(Shared.S.value, (point.x*20+10, point.y*20+10)))
        for r in self.model.robots_location:
            color = r.nativecolor()
            point = self.model.robots_location[r]
            self.robot_group.add(Robot(color, (point.x*20+10, point.y*20+10)))
        self.robot_group.draw(self.robots)
        self.wall_group.draw(self.board)
        goal = self.model.board_section.goals[self.model.goal_index]
        pygame.draw.rect(self.board, self.PURPLE, (goal.point.x*20+5,goal.point.y*20+5,12,12), 0)

        
    def handle_events(self):
        """Translate user input to model actions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

    def display(self):
        """Blit everything to the screen"""
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.board, (50,50))
        self.screen.blit(self.robots, (50,50))
        pygame.display.flip()

    def quit(self):
        """Clean up assets and unload graphic objects"""
        pygame.quit()