from primative import *
import time
import copy

class SolutionGenerator (object):
    board_section = None

    def __init__ (self, boardsection, robots, directions):
        self.board_section = boardsection
        self.robot_objects = robots
        self.directions = directions

    def is_winning (self, node, goal):
        for i, r in enumerate (self.robot_objects):
            for gr in goal.robots:
                if (gr.value & r.value == r.value and 
                    goal.point.x == node[i][0][0] and 
                    goal.point.y == node[i][0][1]
                ):
                    return True
        return False

    def node_to_int (self, node):
        #RED1RED2BLU1BLU2YEL1YEL2GRE1GRE2
        answer = 0
        for i, r in enumerate (self.robot_objects):
            if r.name == "Red":
                answer |= (node[i][0][0] << 28 | node[i][0][1] << 24)
            elif r.name == "Blue":
                answer |= (node[i][0][0] << 20 | node[i][0][1] << 16)
            elif r.name == "Yellow":
                answer |= (node[i][0][0] << 12 | node[i][0][1] << 8)
            elif r.name == "Green":
                answer |= (node[i][0][0] << 4 | node[i][0][1])
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

    def direction_reverse (self, direction):
        if direction == 0b00000001:
            return 0b00000010
        elif direction == 0b00000010:
            return 0b00000001
        elif direction == 0b00000100:
            return 0b00001000
        elif direction == 0b00001000:
            return 0b00000100

    def cell_move (self, cell, direction, node):
        advanced_cell = self.cell_advance (cell, direction)
        if ((advanced_cell[0] < 0 or advanced_cell[0] > 15) or
            (advanced_cell[1] < 0 or advanced_cell[1] > 15)):
            #Moving would put us out of bounds
            return cell
        if self.board_section.board[cell[1]][cell[0]] & direction == direction:
            #Wall in cell stopping us
            return cell
        if self.board_section.board[advanced_cell[1]][advanced_cell[0]] & self.direction_reverse (direction) == self.direction_reverse (direction):
            #Wall in next cell stopping us
            return cell
        for r in node:
            if advanced_cell == r[0]:
                return cell
        return self.cell_move (advanced_cell, direction, node)

    def moves_from_robots (self, node):
        moves = []
        for i, r in enumerate(self.robot_objects):
            for d in self.directions:
                if node[i][1] not in (d.value, d.reverse().value):
                    new_cell = self.cell_move (node[i][0], d.value, node)
                    if node[i][0] != new_cell:
                        updated_robots = copy.copy (node)
                        updated_robots[i] = (new_cell, d.value)
                        moves.append (updated_robots)
        #self.printList (moves)
        #input ("self.printList (moves)")
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

    def generate (self, robots, goal, verbose=False):
        #robots = dictionary key robot value point
        #goal = list of goals
        time_start = time.clock()
        start_position = list(
                [   ((robots[r].x, robots[r].y), 0)
                    for ro in self.robot_objects 
                        for r in robots 
                            if ro == r]
            )
        #flatten into ((x, y), direction.value)
        positions_seen = {}
        #directary of seen positions to remove cycle
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
                            "{0:02d}".format (path_length) + " - " + 
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
                    print ("\tL" + str(path_length) + " - seen:" + str(seen_count) + "; skipped: " + str(skipped_count) + "; total seen: " + str(total_seen_count))
                return path
            for adjacent in self.moves_from_robots (node):
                key = self.node_to_int(adjacent)
                val = positions_seen.get (key)
                if val is None:
                    positions_seen[key] = True
                    new_path = list (path)
                    new_path.append(adjacent)
                    queue.append(new_path)
                else:
                    skipped_count += 1