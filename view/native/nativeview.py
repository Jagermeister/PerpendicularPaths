"""View for native graphics like lines, circles, and rectangles"""
from view import viewinterface as v
import pygame
from pygame.locals import *

class NativeView(v.ViewInterface):
    """Leverage pygame framework for drawing of primative objects"""
    screen = None
    background = None
    model = None
    board = None
    
    # Colors
    BLACK = (  0,   0,   0)
    WHITE = (255, 255, 255)
    BLUE =  (  0,   0, 255)
    GREEN = (  0, 255,   0)
    RED =   (255,   0,   0)
    YELLOW =(255, 255,   0)

    SIZE = (600, 600)

    # Robot locations (this is just for initial layout design!!)
    red_bot = (0,0)
    blue_bot = (3,14)
    green_bot = (9, 4)
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
        pygame.draw.circle(self.board, self.RED, (self.red_bot[0]*20+10, self.red_bot[1]*20+10), 5, 0)
        pygame.draw.circle(self.board, self.BLUE, (self.blue_bot[0]*20+10, self.blue_bot[1]*20+10), 5, 0)
        pygame.draw.circle(self.board, self.GREEN, (self.green_bot[0]*20+10, self.green_bot[1]*20+10), 5, 0)
        pygame.draw.circle(self.board, self.YELLOW, (self.yellow_bot[0]*20+10, self.yellow_bot[1]*20+10), 5, 0)


    def handle_events(self):
        """Translate user input to model actions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

    def display(self):
        """Blit everything to the screen"""
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.board, (50,50))
        pygame.display.flip()

    def quit(self):
        """Clean up assets and unload graphic objects"""
        pygame.quit()
        pass
