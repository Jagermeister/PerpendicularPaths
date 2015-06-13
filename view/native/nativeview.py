"""View for native graphics like lines, circles, and rectangles"""
from view import viewinterface as v
import pygame
from pygame.locals import *
import os
from model.primative import Point, Shared

class Robot(pygame.sprite.Sprite):
    color = None
    robot_object = None

    def __init__(self, color, position, robot_object):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10,10])
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = position
        pygame.draw.circle(self.image, color, (5, 5), 5, 0)
        self.color = color
        self.robot_object = robot_object

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

class Goal(pygame.sprite.Sprite):
    def __init__(self, color, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([12,12])
        self.image.fill(NativeView.PURPLE)
        self.rect = self.image.get_rect()
        self.rect.center = position
        pygame.draw.rect(self.image, color, (2,2,8,8), 0)

class MovesBorder(pygame.sprite.Sprite):
    def __init__(self, color, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([20,20])
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = position
        pygame.draw.rect(self.image, color, (0,0,20,20), 2)

class NativeView(v.ViewInterface):
    """Leverage pygame framework for drawing of primative objects"""
    screen = None
    background = None
    model = None
    board = None
    robots = None
    goal = None
    moves_border = None
    robot_clicked = False
    wall_group = pygame.sprite.Group()
    robot_group = pygame.sprite.Group()
    goal_group = pygame.sprite.Group()
    moves_border_group = pygame.sprite.Group()

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
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(self.WHITE)
        self.show_board()
        
    def handle_events(self):
        """Translate user input to model actions"""
        robot_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                click_pos = (event.pos[0]-50, event.pos[1]-50)
                self.show_possible_moves(click_pos)

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                self.moves_border_group.empty()
                self.moves_border.fill(self.TRANS)

    def show_board(self):
        """Displays the board, robots, and goal"""
        self.board = pygame.Surface((321,321))
        self.board = self.board.convert()
        self.board.fill(self.GRAY)                
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
        self.wall_group.draw(self.board)
        
        self.robots = pygame.Surface((320,320))
        self.robots = self.robots.convert()
        self.robots.set_colorkey(self.TRANS)
        self.robots.fill(self.TRANS)
        for r in self.model.robots_location:
            color = r.rgbcolor()
            point = self.model.robots_location[r]
            self.robot_group.add(Robot(color, (point.x*20+10, point.y*20+10), r))
        self.robot_group.draw(self.robots)

        self.goal = pygame.Surface((320,320))
        self.goal = self.goal.convert()
        self.goal.set_colorkey(self.TRANS)
        self.goal.fill(self.TRANS)
        goal = self.model.goal()
        color = goal.robots[0].rgbcolor()
        self.goal_group.add(Goal(color, (goal.point.x*20+10,goal.point.y*20+10)))
        self.goal_group.draw(self.goal)

    def show_possible_moves(self, position):
        """Displays possible moves for selected robot"""
        self.moves_border = pygame.Surface((320,320))
        self.moves_border = self.goal.convert()
        self.moves_border.set_colorkey(self.TRANS)
        self.moves_border.fill(self.TRANS)
        robot = [robot for robot in self.robot_group if robot.rect.collidepoint(position)]
        if len(robot) == 1:
            self.robot_clicked = True
            move_robot = robot[0]
            move_robot_click_pos = position
            possible_moves = self.model.robot_moves(move_robot.robot_object)
            color = move_robot.color
            for m in possible_moves:
                move_to = (m[3].x*20+10, m[3].y*20+10)
                self.moves_border_group.add(MovesBorder(color, move_to))
        self.moves_border_group.draw(self.moves_border)

    def display(self):
        """Blit everything to the screen"""
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.board, (50,50))
        self.screen.blit(self.robots, (50,50))
        self.screen.blit(self.goal, (50,50))
        if self.robot_clicked:
            self.screen.blit(self.moves_border, (50,50))
        pygame.display.update()

    def quit(self):
        """Clean up assets and unload graphic objects"""
        quit()