import copy
import json
import random
from .primative import Shared, Point, Goal, Board

class BoardGenerator(object):
    #board
    __board_sections = []
    
    generated = False
    """"""

    def __init__(self):
        board_width = 8
        empty = [0]*board_width
        for i in range(len(empty)):
            if i == 0: #First
                empty[i] = [Shared.N.value|Shared.W.value]
                empty[i] += [Shared.N.value]*(board_width-1)
            elif i == board_width-1: #Last
                empty[i] = [Shared.W.value]
                empty[i] += [0]*(board_width-2)
                empty[i] += [Shared.W.value|Shared.N.value]
            else: #Middle
                empty[i] = [Shared.W.value]
                empty[i] += [0]*(board_width-1)

        with open('model/config/board.json') as data_file:
            data = json.load(data_file)
            for i, section in enumerate(data):
                if section["type"] == "classic":
                    #N along top, W along left, NW@7,7
                    goals = []
                    for goal in section["goals"]:
                        robots = []
                        for robot in goal[2]:
                            robots.append(Shared.robot_by_name(robot))
                        goals.append(Goal(Point(goal[0], goal[1]), robots))
                    board = Board(
                        section["id"],
                        copy.deepcopy(empty),
                        goals)
                    for wall in section["walls"]:
                        value = 0
                        for direction in wall[2]:
                            value |= Shared.direction_by_name(direction).value
                        board._board[wall[1]][wall[0]] |= value
                    board.normalize()
                    #patch walls giving every N a neighbor S
                    self.__board_sections.append(board)

        assert len(self.__board_sections) >= 4

    def random_section(self):
        random.shuffle(self.__board_sections)
        return copy.deepcopy(self.__board_sections[0])

    def __generate_by_board_section_keys(self, board_section_keys):
        assert board_section_keys is None or len(board_section_keys) == 4
        board_top = []
        board_bot = []
        sections = []
        keys = []
        for board_key in board_section_keys:
            match = [section for section in self.__board_sections if section.key == board_key]
            if len(match) > 0:
                sections.append(copy.deepcopy(match[0]))
            else:
                sections.append(self.random_section())

        assert len(sections) == 4
        for i, section in enumerate(sections):
            section.rotate(i)

        #put together: 1@0d + 2@90d + 3@180d + 4@270d
        for row in range(0, 8):
            board_top.append(sections[0].board[row] + sections[1].board[row])
            board_bot.append(sections[3].board[row] + sections[2].board[row])
        board_top.extend(board_bot)
        #goals have to have x,y updated based on region
        goals = sections[0].goals
        goals += [Goal(Point(goal.point.x + 8, goal.point.y), goal.robots) for goal in sections[1].goals]
        goals += [Goal(Point(goal.point.x + 8, goal.point.y + 8), goal.robots) for goal in sections[2].goals]
        goals += [Goal(Point(goal.point.x, goal.point.y + 8), goal.robots) for goal in sections[3].goals]
        board = Board(
            "".join([str(section.key) for section in sections]),
            board_top,
            goals)
        board.normalize()
        return board

    def __generate_by_dimension(self, dimension):
        assert isinstance(dimension, int) and dimension > 0
        empty = [0]*dimension
        for i in range(dimension):
            empty[i] = []
            if i == 0:
                empty[i].append(Shared.N.value|Shared.W.value)
                empty[i] += [Shared.N.value]*(dimension-2)
                empty[i].append(Shared.N.value|Shared.E.value)
            elif i == dimension-1:
                empty[i].append(Shared.W.value|Shared.S.value)
                empty[i] += [Shared.S.value]*(dimension-2)
                empty[i].append(Shared.E.value|Shared.S.value)
            else:
                empty[i].append(Shared.W.value)
                empty[i] += [0]*(dimension-2)
                empty[i].append(Shared.E.value)
        return Board(
            "E{}".format(dimension),
            empty,
            [Goal(Point(2, 2), [Shared.R])])

    def generate(self, board_section_keys=None, dimension=None):
        """
        board_section_keys = cooresponds to list of keys set in /config/board.json
        dimension = matrix width 
        """
        if board_section_keys is not None and len(board_section_keys) == 4:
            return self.__generate_by_board_section_keys(board_section_keys)
        elif isinstance(dimension, int) and dimension > 0:
            return self.__generate_by_dimension(dimension)
        else:
            return None

