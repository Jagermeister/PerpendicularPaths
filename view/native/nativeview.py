"""View for native graphics like lines, circles, and rectangles"""
from view import viewinterface as v
import pygame
from pygame.locals import *

class NativeViewState(object):
    """describe mode of terminal view from intial load, menu, and game"""
    load = 0 #Initial load
    menu = 1 #Menu Screen
    game = 2 #Play Game

class NativeView(v.ViewInterface):
    """Leverage pygame framework for drawing of primative objects"""
    screen = None
    background = None
    model = None
    view_state = 1   #NativeViewState

    BLACK = (  0,   0,   0)
    WHITE = (255, 255, 255)
    BLUE =  (  0,   0, 255)
    GREEN = (  0, 255,   0)
    RED =   (255,   0,   0)
    YELLOW =(255, 255,   0)
    
    SIZE =  (600, 600)

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

        # Display some text
        font = pygame.font.Font(None, 36)
        text = font.render("Hello There", 1, self.BLACK)
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        self.background.blit(text, textpos)


    def show_board(self):
        goal = self.model.board_section.goals[self.model.goal_index]
        font = pygame.font.Font(None, 24)
        text = font.render("Goal {} of {}: move {} to cell ({}, {})".format(
            self.model.goal_index+1,
            len(self.model.board_section.goals),
            " or ".join([robot.name for robot in goal.robots]),
            goal.point.x,
            goal.point.y), 1, BLACK)
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        self.background.blit(text, textpos)


    def handle_events(self):
        """Translate user input to model actions"""
        for event in pygame.event.get():
            if self.view_state == NativeViewState.menu:
                if event.type == MOUSEBUTTONUP:
                    font = pygame.font.Font(None, 24)
                    text = "\n\r[U]p or [D]own to move menu\n\r"                    
                    textpos = text.get_rect()
                    textpos.centerx = self.background.get_rect().centerx
                    self.background.blit(text, textpos)
                    answer = event.button.upper
                    print(answer)
                    if answer == "U":
                        if self.menu_key > 0:
                            self.menu_key -= 1
                    elif answer == "D":
                        if self.menu_key < len(self.menu_options) - 1:
                            self.menu_key += 1
                    elif not answer:
                        if self.menu_key == 0:
                            self.game_new()
                        elif self.menu_key == 1:
                            seed = input("""SEED?
                                Leave blank for random generation
                                'L' for last seed\n\r>""").upper()
                            self.game_new(seed)
                        elif self.menu_key == 2:
                            self.game_new("E5", False)

            elif event.type == pygame.QUIT:
                self.quit()


    def display(self):
        """Blit everything to the screen"""
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def quit(self):
        """Clean up assets and unload graphic objects"""
        pygame.quit()
        pass