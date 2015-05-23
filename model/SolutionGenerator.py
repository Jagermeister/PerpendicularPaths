import time
import copy
import itertools
from collections import deque

class SolutionGenerator(object):
    direction_reverse = {}
    direction_delta = {}

    def __init__(self, boardsection, robots, directions):
        self.board = list(itertools.chain.from_iterable(boardsection._board))
        self.robot_objects = copy.deepcopy(robots)
        self.directions = directions
        self.direction_reverse = {
            0b00000001: 0b00000010,
            0b00000010: 0b00000001,
            0b00000100: 0b00001000,
            0b00001000: 0b00000100}
        self.direction_delta = {
            0b00000001: -16,
            0b00000010: +16,
            0b00000100: +1,
            0b00001000: -1}

    def cell_move(self, index, direction, node):
        while True:
            if self.board[index] & direction == direction:
                break
            advanced_index = index + self.direction_delta[direction]
            for robot in node:
                if advanced_index == robot[0]:
                    break
            else:
                index = advanced_index
                continue
            break
        return index

    def moves_from_robots(self, node, goal_index):
        moves = deque()
        for index in range(0, len(self.robot_objects)):
            for direction in self.directions:
                if node[index][1] not in(direction.value, self.direction_reverse[direction.value]):
                    #ricochet rule
                    new_cell = node[index][0]
                    advanced_index = 0
                    while True:
                        if self.board[new_cell] & direction.value == direction.value:
                            break
                        advanced_index = new_cell + self.direction_delta[direction.value]
                        for robot in node:
                            if advanced_index == robot[0]:
                                break
                        else:
                            new_cell = advanced_index
                            continue
                        break
                    if(node[index][0] != new_cell and not(
                            index == 3 and
                            node[index][1] == 0 and
                            new_cell == goal_index)):
                        updated_robots = copy.copy(node)
                        updated_robots[index] = (new_cell, direction.value)
                        moves.append(updated_robots)
        return moves

    def generate(self, robots, goal, directions=None, verbose=False):
        #robots = dictionary key robot value point
        assert len(robots) == 4
        #goal = list of goals
        assert len(goal.robots) == 1#multi goal not supported
        #directions = list of last direction values or 0 for none
        time_start = time.clock()
        if directions is not None:
            assert len(directions) == len(robots)
        else:
            directions = [0] * len(robots)
        #reorganize goal object last
        for i, robot in enumerate(self.robot_objects):
            if robot.value == goal.robots[0].value:
                self.robot_objects.append(self.robot_objects.pop(i))
                break
        start_position = list(
            [(robots[robot].y * 16 + robots[robot].x, directions[ii])
             for i, robot_template
             in enumerate(self.robot_objects)
             for ii, robot
             in enumerate(robots)
             if robot_template.value == robot.value
            ])
        #reorder our robots - put the goal robot last @ [3]
        goal_index = goal.point.y * 16 + goal.point.x
        for direction in self.directions:
            new_cell = self.cell_move(goal_index, direction.value, [])
            if new_cell != goal_index:
                if direction.value in (4, 8):#EorW
                    minx = new_cell if new_cell < goal_index else goal_index
                    maxx = new_cell if new_cell > goal_index else goal_index
                elif direction.value in (1, 2):#NorS
                    miny = new_cell if new_cell < goal_index else goal_index
                    maxy = new_cell if new_cell > goal_index else goal_index
        minymod = miny % 16
        positions_seen = {}
        #directary of seen positions
        path_length = 1
        total_seen_count = 0
        seen_count = 0
        skipped_count = 0
        queue = deque()
        queue.append([start_position])
        while queue:
            path = queue.popleft()
            node = path[-1]
            if len(path) != path_length:
                if verbose:
                    print("{0:02d} - {1:05d}\t sk: {2:05d}\t@ {3}s".format(
                        path_length-1,
                        seen_count,
                        skipped_count,
                        time.clock() - time_start))
                path_length = len(path)
                total_seen_count += seen_count
                seen_count = 0
            seen_count += 1
            if goal_index == node[3][0] or (
                    (node[3][1] in (1, 2) and maxx >= node[3][0] >= minx) or (
                        node[3][1] in (3, 4) and 
                        maxy >= node[3][0] >= miny and 
                        node[3][0] % 16 == minymod)):
                total_seen_count += seen_count
                if verbose:
                    print("\tanswer found in " + str(time.clock() - time_start) + "s")
                    print("\tL{} - total seen: {}; skipped: {}; cache: {};".format(
                        path_length-1,
                        total_seen_count,
                        skipped_count,
                        len(positions_seen)))
                return path
            for adjacent in self.moves_from_robots(node, goal_index):
                first = adjacent[0][0]
                second = adjacent[1][0]
                third = adjacent[2][0]
                if first > second:
                    first, second = second, first
                if second > third:
                    second, third = third, second
                if first > second:
                    first, second = second, first
                key = adjacent[3][0] | first << 8 | second << 16 | third << 24
                if positions_seen.get(key) is None:
                    positions_seen[key] = True
                    new_path = deque(list(path))
                    new_path.append(adjacent)
                    queue.append(new_path)
                else:
                    skipped_count += 1
        print("\tanswer NOT found in " + str(time.clock() - time_start) + "s")
        print("\tL{} - total seen: {}; skipped: {}; cache: {};".format(
            path_length-1,
            total_seen_count,
            skipped_count,
            len(positions_seen)))
