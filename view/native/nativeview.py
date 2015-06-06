"""View for native graphics like lines, circles, and rectangles"""
from view import viewinterface as v
import pygame
from pygame.locals import *

class Robot(pygame.sprite.Sprite):
    def __init__(self, color, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10,10])
        self.image.fill(NativeView.WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = position
        pygame.draw.circle(self.image, color, (5, 5), 5, 0)

class NativeView(v.ViewInterface):
    """Leverage pygame framework for drawing of primative objects"""
    screen = None
    background = None
    model = None
    board = None
    robots = None
    robot_group = pygame.sprite.Group()

    # RGB Colors
    BLACK = (  0,   0,   0)
    WHITE = (255, 255, 255)
    BLUE =  (  0,   0, 255)
    GREEN = (  0, 255,   0)
    RED =   (255,   0,   0)
    YELLOW =(255, 255,   0)
    TRANS  =(  1,   1,   1)

    SIZE = width, height = 600, 600
    SPEED = [2, 2]

    # Robot locations (this is just for initial layout design!!)
    red_bot    = (0,0)
    blue_bot   = (3,14)
    green_bot  = (9, 4)
    yellow_bot = (15,12)

    def init(self, model):
        """Initialise screen"""
        self.model = model
        pygame.init()
        self.screen = pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption('Perpendicular Paths')

        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(self.WHITE)

        # Draw the board
        self.board = pygame.Surface((320,320))
        self.board = self.board.convert()
        self.board.fill(self.WHITE)
        pygame.draw.rect(self.board, self.BLACK, [0,0,320,320], 4)
        for i in range (1,16):
            pygame.draw.line(self.board, self.BLACK, [i*20, 0], [i*20, 320], 1)
            pygame.draw.line(self.board, self.BLACK, [0, i*20], [320, i*20], 1)

        # Draw the Robots
        self.robots = pygame.Surface((320,320))
        self.robots = self.robots.convert()
        self.robots.set_colorkey(self.TRANS)
        self.robots.fill(self.TRANS)
        self.robot_group.add(Robot(self.RED, (self.red_bot[0]*20+10, self.red_bot[1]*20+10)))
        self.robot_group.add(Robot(self.BLUE, (self.blue_bot[0]*20+10, self.blue_bot[1]*20+10)))
        self.robot_group.add(Robot(self.GREEN, (self.green_bot[0]*20+10, self.green_bot[1]*20+10)))
        self.robot_group.add(Robot(self.YELLOW, (self.yellow_bot[0]*20+10, self.yellow_bot[1]*20+10)))
        self.robot_group.draw(self.robots)

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
        pass
