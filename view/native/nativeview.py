"""View for native graphics like lines, circles, and rectangles"""
from view import viewinterface as v
from model.primative import Point, Shared
import pygame, os, sys, math, time
from pygame.locals import *
from model.core import PPMoveStatus

class Robot(pygame.sprite.Sprite):
    robot_object = None
    animation_start_time = None
    animation_duration = 1.0
    start_point = None
    destination = None

    def __init__(self, position, robot_object, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([size,size])
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.start_point = position
        self.rect.center = self.start_point
        self.robot_object = robot_object
        pygame.draw.circle(
            self.image,
            self.robot_object.rgbcolor(),
            (int(size/2), int(size/2)),
            int(size/3), 0)

    def set_destination(self, point):
        """Set destination x,y based off self.robot_object"""
        self.destination = point
        self.animation_start_time = time.clock()

    def update(self):
        """updates the robot's location if a move is initiated"""    
        if self.destination:
            elapsed_percentage = (time.clock() - self.animation_start_time) / self.animation_duration
            if elapsed_percentage < 1.0:
                self.dx = self.destination[0] - self.start_point[0]
                self.dy = self.destination[1] - self.start_point[1]
                self.x = self.start_point[0] + elapsed_percentage * self.dx
                self.y = self.start_point[1] + elapsed_percentage * self.dy
            else:
                self.x = self.destination[0]
                self.y = self.destination[1]
                self.destination = None
                self.animation_start_time = None
                self.start_point = (self.x, self.y)
            self.rect.center = (self.x, self.y)

class Wall(pygame.sprite.Sprite):
    def __init__(self, direction, position, length):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([length+2,length+2])
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = position
        if direction == Shared.W.value:
            pygame.draw.line(self.image, NativeView.BLACK, [0,0], [0,length], 4)
        elif direction == Shared.S.value:
            pygame.draw.line(self.image, NativeView.BLACK, [0,length], [length,length], 4)

class Goal(pygame.sprite.Sprite):
    def __init__(self, color, position, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([size*2/3,size*2/3])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = position

class Grid(pygame.sprite.Sprite):
    def __init__(self, size, position, start, end):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(size)
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = position
        pygame.draw.line(self.image, NativeView.BLACK, start, end, 1)

class MovesBorder(pygame.sprite.Sprite):
    def __init__(self, color, position, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([size,size])
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = position
        pygame.draw.rect(self.image, color, (0,0,size,size), 3)

class DirectionIndicator(pygame.sprite.Sprite):
    def __init__(self, position, start, end):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(position)
        self.image.set_colorkey(NativeView.TRANS)
        self.image.fill(NativeView.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = (position[0]/2,position[1]/2)
        pygame.draw.line(self.image, NativeView.PURPLE, start, end, 3)

class MoveHistoryText(pygame.sprite.Sprite):
    def __init__(self, position, display_text):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([160, 20]).convert()
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
    #Core
    model = None
    #Surfaces
    screen = None
    background = None 
    gameplay = None
    move_history = None
    #Event variables
    move_robot = None
    move_direction = None
    click_x = None
    click_y = None
    robot_clicked = False
    possible_moves = None
    is_dragging = False
    desired_move = None
    #Groups
    all_sprites_group = pygame.sprite.Group()
    wall_group = pygame.sprite.Group()
    robot_group = pygame.sprite.Group()
    possible_moves_group = pygame.sprite.Group()
    direction_indicator = None
    move_history_group = pygame.sprite.Group()
    #RGB Colors
    BLACK = (  0,   0,   0)
    WHITE = (255, 255, 255)
    BLUE =  (  0,   0, 255)
    GREEN = (  0, 255,   0)
    RED =   (255,   0,   0)
    YELLOW =(255, 255,   0)
    PURPLE =(255,   0, 255)
    TRANS  =(  1,   1,   1)
    GRAY   =(211, 211, 211)
    #Size, Spacing, and offsets
    SIZE = width, height = 1280, 720
    board_x_offset = 40
    board_y_offset = 40
    spaces = 16
    space_size = 40 #16 spaces at 40px = 640x640 board

    def init(self, model):
        """Initialize screen"""
        self.model = model
        model.game_new()        
        pygame.init()
        self.screen = pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption('Perpendicular Paths')
        self.background = pygame.Surface(self.SIZE).convert()
        self.background.fill(self.WHITE)
        self.gameplay = pygame.Surface(self.SIZE).convert()
        self.gameplay.set_colorkey(self.TRANS)
        self.gameplay.fill(self.TRANS)
        self.show_move_history()
        self.screen.blit(self.background, (0,0))

        #Create the grid
        size = self.spaces * self.space_size
        for i in range (1,self.spaces):
            self.all_sprites_group.add(Grid(
                self.SIZE,
                (self.width / 2, self.height / 2),
                [i * self.space_size + self.board_x_offset, self.board_y_offset],
                [i * self.space_size + self.board_x_offset, self.space_size * self.spaces + self.board_y_offset]))
            self.all_sprites_group.add(Grid(
                self.SIZE,
                (self.width / 2, self.height / 2),
                [self.board_x_offset, i * self.space_size + self.board_y_offset],
                [self.space_size * self.spaces + self.board_x_offset, i * self.space_size + self.board_y_offset]))

        #Create the walls
        for j, row in enumerate(self.model.board_section.board):
            #constant north wall
            point = Point(j, -1)
            wall_N = Wall(
                Shared.S.value,
                self.board_cell_to_pixel(point),
                self.space_size)
            wall_N.add(self.all_sprites_group, self.wall_group)
            #constant east wall
            point = Point(self.spaces,j)
            wall_E = Wall(
                Shared.W.value,
                self.board_cell_to_pixel(point),
                self.space_size)
            wall_E.add(self.all_sprites_group, self.wall_group)
            #walls defined by the game core
            for k, cell in enumerate(row):
                point = Point(k, j)
                wall_W = None
                wall_S = None
                if cell & Shared.W.value:
                    wall_W = Wall(
                        Shared.W.value,
                        self.board_cell_to_pixel(point),
                        self.space_size)
                    wall_W.add(self.all_sprites_group, self.wall_group)
                if cell & Shared.S.value:
                    wall_S = Wall(
                        Shared.S.value,
                        self.board_cell_to_pixel(point),
                        self.space_size)
                    wall_S.add(self.all_sprites_group, self.wall_group)

        #Create the robots
        for r in self.model.robots_location:
            point = self.model.robots_location[r]
            robot = Robot(
                self.board_cell_to_pixel(point),
                r,
                self.space_size)
            robot.add(self.all_sprites_group, self.robot_group)

        #Create the goal
        goal = self.model.goal()
        color = goal.robots[0].rgbcolor()
        self.all_sprites_group.add(Goal(
            color,
            self.board_cell_to_pixel(goal.point),
            self.space_size))

    def board_cell_to_pixel(self, point):
        """Given point for board, return the center point pixels in an x,y tuple"""
        return(point.x * self.space_size + (self.space_size / 2) + self.board_x_offset,
            point.y * self.space_size + (self.space_size / 2) + self.board_y_offset)

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

    def show_possible_moves(self, position, size):
        """Displays possible moves for selected robot"""
        self.possible_moves = None
        robot = [robot for robot in self.robot_group if robot.rect.collidepoint(position)]
        if len(robot) == 1:
            self.robot_clicked = True
            self.move_robot = robot[0]
            self.possible_moves = self.model.robot_moves(self.move_robot.robot_object)
            color = self.move_robot.robot_object.rgbcolor()
            for moves in self.possible_moves:
                #robot, direction, from, to
                move_to = self.board_cell_to_pixel(moves[3])
                border = MovesBorder(color, move_to, size)
                border.add(self.all_sprites_group, self.possible_moves_group)

    def hide_possible_moves(self):
        for border_sprite in self.possible_moves_group:
            border_sprite.kill()

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

    def show_direction_indicator(self, size):
        legal_moves = [move for move in self.possible_moves if move[1] == self.move_direction]
        if legal_moves: 
            legal_move = legal_moves[0]
            #robot, direction, old cell, new cell
            move_direction_end = self.board_cell_to_pixel(legal_move[3])
            self.desired_move = self.move_direction
            if self.direction_indicator is not None:
                self.direction_indicator.kill()
            self.direction_indicator = DirectionIndicator(
                (self.width,self.height),
                self.move_robot.rect.center,
                move_direction_end)
            self.all_sprites_group.add(self.direction_indicator)

    def handle_events(self):
        """Translate user input to model actions"""
        robot_clicked = False
        self.screen.fill(self.WHITE)
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                #left click
                self.click_x, self.click_y = event.pos
                self.show_possible_moves((self.click_x,self.click_y), self.space_size)

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                #release left click
                self.hide_possible_moves()
                if self.desired_move is not None:
                    move_result = self.model.robot_move(self.move_robot.robot_object, self.desired_move)
                    if move_result == PPMoveStatus.MOVE_SUCCESS:
                        point = self.model.robots_location[self.move_robot.robot_object]
                        self.move_robot.set_destination(self.board_cell_to_pixel(point))
                        self.desired_move = None
                self.move_robot = None
                self.is_dragging = False
                self.move_direction = None
                if self.direction_indicator is not None:
                    self.direction_indicator.kill()

            elif event.type == MOUSEMOTION and event.buttons[0] == 1 and self.move_robot is not None:
                #left click on a robot and drag
                self.is_dragging = True
                self.desired_move = None
                relative_position = pygame.mouse.get_pos()
                dy = float(relative_position[1] - self.click_y)
                dx = float(relative_position[0] - self.click_x)
                rad = math.atan2(dy,dx)
                degrees = (90 - ((rad*180) / math.pi)) % 360
                self.move_direction = self.degrees_to_direction(degrees)
                self.show_direction_indicator(NativeView.space_size)

            elif event.type == pygame.QUIT:
                self.quit()

            elif event.type == KEYDOWN and event.key == K_SPACE:
                for sprite in self.all_sprites_group:
                    print(sprite)

    def update(self):
        pass

    def display(self):
        """Blit everything to the screen"""
        self.gameplay.fill(self.WHITE)
        self.all_sprites_group.update()
        self.all_sprites_group.draw(self.gameplay)
        self.screen.blit(self.gameplay, (0,0))
        pygame.display.update() 
        
        self.show_move_history()
        self.screen.blit(self.move_history, (700,40))
        pygame.display.update()
        
    def quit(self):
        """Clean up assets and unload graphic objects"""
        pygame.quit()
        sys.exit()