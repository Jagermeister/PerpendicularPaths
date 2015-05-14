from primative import *
import time
import copy
import operator
import itertools

class SolutionGenerator (object):
    board_section = None
    minx = 0
    maxx = 0
    miny = 0
    maxy = 0
    direction_reverse = {}

    def __init__ (self, boardsection, robots, directions):
        self.board_section = boardsection
        #self.board = list(itertools.chain.from_iterable(boardsection._board))
        #flatten
        self.robot_objects = copy.deepcopy (robots)
        self.directions = directions
        self.direction_reverse = {
                0b00000001: 0b00000010,
                0b00000010: 0b00000001,
                0b00000100: 0b00001000,
                0b00001000: 0b00000100,
            }

    def is_winning (self, node, goal):
        if (goal.point.x == node[3][0][0] and 
            goal.point.y == node[3][0][1]
        ):
            return True
        elif (
            (goal.point.x == node[3][0][0] and 
            (node[3][0][1] >= self.miny and node[3][0][1] <= self.maxy)) or
            (goal.point.y == node[3][0][1] and 
            (node[3][0][0] >= self.minx and node[3][0][0] <= self.maxx))
        ):
            return True
        return False

    def node_to_int (self, node, goal):
        answer = (node[3][0][0] << 4 | node[3][0][1])
        first, second, third = node[0][0], node[1][0], node[2][0]
        if first > second:
            first, second = second, first
        if second > third:
            second, third = third, second
        if first > second:
            first, second = second, first
        answer |= (first[0] << 12 | first[1] << 8)
        answer |= (second[0] << 20 | second[1] << 16)
        answer |= (third[0] << 28 | third[1] << 24)
        return answer

    def cell_advance (self, cell, direction):
        if direction == 0b00000001:
            return (cell[0], cell[1]-1)
        elif direction == 0b00000010:
            return (cell[0], cell[1]+1)
        elif direction == 0b00000100:
            return (cell[0]+1, cell[1])
        elif direction == 0b00001000:
            return (cell[0]-1, cell[1])

    def cell_move (self, cell, direction, node):
        while True:
#            if ((advanced_cell[0] < 0 or advanced_cell[0] > 15) or
#                (advanced_cell[1] < 0 or advanced_cell[1] > 15)):
#                #Moving would put us out of bounds
#                break
            if self.board_section.board[cell[1]][cell[0]] & direction == direction:
                #Wall in cell stopping us
                break
            advanced_cell = self.cell_advance (cell, direction)
            dr = self.direction_reverse[direction]
            if self.board_section.board[advanced_cell[1]][advanced_cell[0]] & dr == dr:
                #Wall in next cell stopping us
                break
            for r in node:
                if advanced_cell == r[0]:
                    break
            else:
                cell = advanced_cell
                continue
            break
        return cell

    def moves_from_robots (self, node):
        moves = []
        for i, r in enumerate(self.robot_objects):
            for d in self.directions:
                if node[i][1] not in (d.value, self.direction_reverse[d.value]):
                    new_cell = self.cell_move (node[i][0], d.value, node)
                    if node[i][0] != new_cell:
                        updated_robots = copy.copy (node)
                        updated_robots[i] = (new_cell, d.value)
                        moves.append (updated_robots)
        return moves

    def printList(self, path):
        for r in self.robot_objects:
            print (r.name + "\t", end="")
        print ("")
        for robotList in path:
            print ("[", end="")
            for r in robotList:
                print (r, end=" ")
            print ("]")

    def generate (self, robots, goal, directions=None, verbose=False):
        #robots = dictionary key robot value point
        assert len(robots) == 4
        #goal = list of goals
        assert len(goal.robots) == 1#multi goal not supported
        #directions = list of last direction values or 0 for none
        time_start = time.clock()
        for i, r in enumerate (self.robot_objects):
            if r.value == goal.robots[0].value:
                self.robot_objects.append (self.robot_objects.pop(i))
        #reorder our robots - put the goal robot last @ [3]
        if directions is not None:
            assert len(directions) == len(robots)
        else:
            directions = [0] * len(robots)
        start_position = list(
                [   ((robots[r].x, robots[r].y), directions[i])
                    for i, ro in enumerate(self.robot_objects)
                        for r in robots 
                            if ro.value == r.value]
            )
        #flatten into ((x, y), direction.value)
        for d in self.directions:
            new_cell = self.cell_move ((goal.point.x, goal.point.y), d.value, [])
            if new_cell[0] != goal.point.x or new_cell[1] != goal.point.y:
                if d.value in (4,8):#EorW
                    self.minx = new_cell[0] if new_cell[0] < goal.point.x else goal.point.x
                    self.maxx = new_cell[0] if new_cell[0] > goal.point.x else goal.point.x
                elif d.value in (1,2):#NorS
                    self.miny = new_cell[1] if new_cell[1] < goal.point.y else goal.point.y
                    self.maxy = new_cell[1] if new_cell[1] > goal.point.y else goal.point.y
        positions_seen = {}
        #directary of seen positions
        path_length = 1
        total_seen_count = 0
        seen_count = 0
        skipped_count = 0
        queue = []
        queue.append ([start_position])
        while queue:
            path = queue.pop(0)
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
            if self.is_winning (node, goal):
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
            for adjacent in self.moves_from_robots (node):
                key = self.node_to_int(adjacent, goal)
                val = positions_seen.get (key)
                if val is None:
                    positions_seen[key] = True
                    new_path = list (path)
                    new_path.append(adjacent)
                    queue.append(new_path)
                else:
                    skipped_count += 1