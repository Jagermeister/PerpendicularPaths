from .primative import *
import time
import copy
import itertools
from collections import deque

class SolutionGenerator (object):
    direction_reverse = {}
    direction_delta = {}

    def __init__ (self, boardsection, robots, directions):
        self.board = list(itertools.chain.from_iterable(boardsection._board))
        self.robot_objects = copy.deepcopy (robots)
        self.directions = directions
        self.direction_reverse = {
                0b00000001: 0b00000010,
                0b00000010: 0b00000001,
                0b00000100: 0b00001000,
                0b00001000: 0b00000100,
            }
        self.direction_delta = {
                0b00000001: -16,
                0b00000010: +16,
                0b00000100: +1,
                0b00001000: -1,
            }

    def node_to_int (self, node):
        first, second, third = node[0][0], node[1][0], node[2][0]
        if first > second:
            first, second = second, first
        if second > third:
            second, third = third, second
        if first > second:
            first, second = second, first
        return node[3][0] | first << 8 | second << 16 | third << 24

    def cell_move (self, index, direction, node):
        while True:
            if self.board[index] & direction == direction:
                break
            advanced_index = index + self.direction_delta[direction]
            for r in node:
                if advanced_index == r[0]:
                    break
            else:
                index = advanced_index
                continue
            break
        return index

    def moves_from_robots (self, node, goal_index):
        moves = deque()
        for i, r in enumerate(self.robot_objects):
            for d in self.directions:
                if node[i][1] not in (d.value, self.direction_reverse[d.value]):
                    #ricochet rule
                    new_cell = node[i][0]
                    advanced_index = 0
                    while True:
                        if self.board[new_cell] & d.value == d.value:
                            break
                        advanced_index = new_cell + self.direction_delta[d.value]
                        for r in node:
                            if advanced_index == r[0]:
                                break
                        else:
                            new_cell = advanced_index
                            continue
                        break
                    if (node[i][0] != new_cell and not (
                            i == 3 and
                            node[i][1] == 0 and
                            new_cell == goal_index
                        )
                    ):
                        updated_robots = copy.copy (node)
                        updated_robots[i] = (new_cell, d.value)
                        moves.append (updated_robots)
        return moves

    def generate (self, robots, goal, directions=None, verbose=False):
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
        for i, r in enumerate (self.robot_objects):
            if r.value == goal.robots[0].value:
                self.robot_objects.append (self.robot_objects.pop(i))
                break
        start_position = list(
                [   (robots[r].y * 16 + robots[r].x, directions[ii])
                    for i, ro in enumerate(self.robot_objects)
                        for ii, r in enumerate(robots) 
                            if ro.value == r.value]
            )
        #reorder our robots - put the goal robot last @ [3]
        goal_index = goal.point.y * 16 + goal.point.x
        for d in self.directions:
            new_cell = self.cell_move (goal_index, d.value, [])
            if new_cell != goal_index:
                if d.value in (4,8):#EorW
                    minx = new_cell if new_cell < goal_index else goal_index
                    maxx = new_cell if new_cell > goal_index else goal_index
                elif d.value in (1,2):#NorS
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
        queue.append ([start_position])
        while queue:
            path = queue.popleft()
            node = path[-1]
            if len(path) != path_length:
                if verbose:
                    print (
                            "{0:02d}".format (path_length-1) + " - " + 
                            "{0:05d}".format (seen_count) + "\t sk: " + 
                            "{0:05d}".format (skipped_count) + "\t@ " + 
                            str(time.clock() - time_start) + "s"
                        )
                path_length = len(path)
                total_seen_count += seen_count
                seen_count = 0
            seen_count += 1
            if (
                (goal_index == node[3][0]) or
                (
                    (
                        (node[3][1] in (1,2) and maxx >= node[3][0] >= minx) or
                        (node[3][1] in (3,4) and maxy >= node[3][0] >= miny and node[3][0] % 16 == minymod)
                    )
                )
            ):
                total_seen_count += seen_count
                if verbose:
                    print ("\tanswer found in " + str(time.clock() - time_start) + "s")
                    print (
                            "\tL" + str(path_length-1) + 
                            " - total seen:" + str(total_seen_count) + 
                            "; skipped: " + str(skipped_count) + 
                            "; cache: " + str(len(positions_seen))
                        )
                return path
            for adjacent in self.moves_from_robots (node, goal_index):
                first = adjacent[0][0]; second = adjacent[1][0]; third = adjacent[2][0]
                if first > second:
                    first, second = second, first
                if second > third:
                    second, third = third, second
                if first > second:
                    first, second = second, first
                key = adjacent[3][0] | first << 8 | second << 16 | third << 24
                if positions_seen.get (key) is None:
                    positions_seen[key] = True
                    new_path = deque(list (path))
                    new_path.append(adjacent)
                    queue.append(new_path)
                else:
                    skipped_count += 1
        print ("\tanswer NOT found in " + str(time.clock() - time_start) + "s")
        print (
                "\tL" + str(path_length-1) + 
                " - total seen:" + str(total_seen_count) + 
                "; skipped: " + str(skipped_count) + 
                "; cache: " + str(len(positions_seen))
            ) 