"""View for native graphics like lines, circles, and rectangles"""
from view import viewinterface as v
import pygame
from pygame.locals import *

class NativeView(v.ViewInterface):
    """Leverage pygame framework for drawing of primative objects"""
    screen = None
    background = None
    model = None
    

    def init(self, model):
        """Initialise screen"""
        self.model = model
        pygame.init()
        self.screen = pygame.display.set_mode((300, 350))
        pygame.display.set_caption('Basic Pygame program')

        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((250, 250, 250))

        # Display some text
        font = pygame.font.Font(None, 36)
        text = font.render("Hello There", 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        self.background.blit(text, textpos)

    def handle_events(self):
        """Translate user input to model actions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

    def display(self):
        """Blit everything to the screen"""
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def quit(self):
        """Clean up assets and unload graphic objects"""
        #pygame.quit()
        pass
