"""View for native graphics like lines, circles, and rectangles"""
from view import viewinterface as v
import pygame
from pygame.locals import *
import os
from model.primative import Point, Shared
import math

class Robot(pygame.sprite.Sprite):
    robot_object = None

    def __init__(self, position, robot_object):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10,10])
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.robot_object = robot_object
        pygame.draw.circle(self.image, self.robot_object.rgbcolor(), (5, 5), 5, 0)
        

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

class DirectionIndicator(pygame.sprite.Sprite):
    def __init__(self, position, start, end):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([320,320])
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = position
        pygame.draw.line(self.image, NativeView.PURPLE, start, end, 3)

class MoveHistoryText(pygame.sprite.Sprite):
    def __init__(self, position, display_text):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([160, 20]).convert()
        #self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = position
        font = pygame.font.Font(None, 16)
        text = font.render(display_text, 1, NativeView.WHITE)
        textpos = text.get_rect()
        textpos.centerx = 80
        self.image.blit(text, textpos)

class NativeView(v.ViewInterface):
    """Leverage pygame framework for drawing of primative objects"""
    model = None
    #Core
    screen = None
    background = None  
    board = None
    robots = None
    goal = None
    move_history = None
    direction_indicator = None
    moves_border = None
    #Surfaces
    move_robot = None
    move_direction = None
    click_pos = None
    robot_clicked = False
    possible_moves = None
    is_dragging = False
    desired_move = None
    all_sprites = pygame.sprite.Group()
    wall_group = pygame.sprite.Group()
    robot_group = pygame.sprite.Group()
    goal_group = pygame.sprite.Group()
    moves_border_group = pygame.sprite.Group()
    direction_indicator_group = pygame.sprite.Group()
    move_history_group = pygame.sprite.Group()

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
        self.show_robots()
        self.show_goal()
        self.show_move_history()
        
    def handle_events(self):
        """Translate user input to model actions"""
        robot_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.click_pos = event.pos
                self.show_possible_moves(event.pos)

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if self.desired_move is not None:
                    self.model.robot_move(self.move_robot.robot_object, self.desired_move)
                    self.robot_group.empty()
                    self.show_robots()
                    self.desired_move = None
                self.move_robot = None
                self.is_dragging = False
                self.moves_border_group.empty()
                self.moves_border.fill(self.TRANS)
                self.direction_indicator_group.empty()
                if self.direction_indicator is not None:
                    self.direction_indicator.fill(self.TRANS)
                self.move_direction = None

            elif event.type == MOUSEMOTION and event.buttons[0] == 1 and self.move_robot is not None:
                self.show_direction_indicator()

    def degrees_to_direction(self, degrees):
        """Utility to convert degrees from an angle to a direction"""
        if 125 >= degrees > 55:
            return Shared.E
        elif 215>= degrees > 145:
            return Shared.N
        elif 305 >= degrees > 235:
            return Shared.W
        elif 35 >= degrees or degrees >= 325:
            return Shared.S

    def show_board(self):
        """Displays the board"""
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
        
    def show_robots(self):
        """Displays the robots"""    
        self.robots = pygame.Surface((320,320))
        self.robots = self.robots.convert()
        self.robots.set_colorkey(self.TRANS)
        self.robots.fill(self.TRANS)
        for r in self.model.robots_location:
            point = self.model.robots_location[r]
            self.robot_group.add(Robot((point.x*20+10, point.y*20+10), r))
        self.robot_group.draw(self.robots)

    def show_goal(self):
        """Displays the goal"""
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
        self.possible_moves = None
        self.moves_border = pygame.Surface((320,320))
        self.moves_border = self.goal.convert()
        self.moves_border.set_colorkey(self.TRANS)
        self.moves_border.fill(self.TRANS)
        move_robot_click_pos = (position[0]-50, position[1]-50)
        robot = [robot for robot in self.robot_group if robot.rect.collidepoint(move_robot_click_pos)]
        if len(robot) == 1:
            self.robot_clicked = True
            self.move_robot = robot[0]
            self.possible_moves = self.model.robot_moves(self.move_robot.robot_object)
            color = self.move_robot.robot_object.rgbcolor()
            for m in self.possible_moves:
                move_to = (m[3].x*20+10, m[3].y*20+10)
                self.moves_border_group.add(MovesBorder(color, move_to))
        self.moves_border_group.draw(self.moves_border)

    def show_move_history(self):
        """Displays the move history list"""
        self.move_history_group.empty()
        self.move_history = pygame.Surface((160,320))
        self.move_history = self.move_history.convert()
        self.move_history.set_colorkey(self.TRANS)
        self.move_history.fill(self.TRANS)
        for j, move in enumerate(self.model.move_history):
            self.move_history_group.add(MoveHistoryText((0+80,j*20+10), "{}. {} {} from {}".format(
                j+1,
                move[0].name,
                move[1].name,
                move[2])))
        self.move_history_group.draw(self.move_history)

    def show_direction_indicator(self):
        """Displays the direction intended to move in"""
        self.direction_indicator_group.empty()
        self.is_dragging = True
        self.desired_move = None
        self.direction_indicator = pygame.Surface((320,320))
        self.direction_indicator = self.direction_indicator.convert()
        self.direction_indicator.set_colorkey(self.TRANS)
        self.direction_indicator.fill(self.TRANS)
        move_robot_rel_pos = pygame.mouse.get_pos()
        dy = float(move_robot_rel_pos[1] - self.click_pos[1])
        dx = float(move_robot_rel_pos[0] - self.click_pos[0])
        m = 0.0 if dx == 0 else dy/dx
        rad = math.atan2(dy,dx)
        degrees = (90 - ((rad*180) / math.pi)) % 360
        self.move_direction = self.degrees_to_direction(degrees)
        legal_moves = [move for move in self.possible_moves if move[1] == self.move_direction]
        if legal_moves:
            legal_move = legal_moves[0]
            #robot, direction, old cell, new cell
            move_direction_end = (legal_move[3].x*20+10, legal_move[3].y*20+10)
            self.desired_move = self.move_direction
            self.direction_indicator_group.add(DirectionIndicator((160,160), self.move_robot.rect.center, move_direction_end))
            self.direction_indicator_group.draw(self.direction_indicator)

    def display(self):
        """Blit everything to the screen"""
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.board, (50,50))
        self.screen.blit(self.robots, (50,50))
        self.screen.blit(self.goal, (50,50))
        if self.robot_clicked:
            self.screen.blit(self.moves_border, (50,50))
            if self.move_direction:
                self.screen.blit(self.direction_indicator, (50,50))
        self.show_move_history()
        self.screen.blit(self.move_history, (400,50))
        pygame.display.update()

    def quit(self):
        """Clean up assets and unload graphic objects"""
        quit()