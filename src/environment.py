from entities import *

import random

class Direction:

    @staticmethod
    def north():
        return -1, 0
    
    @staticmethod
    def north_east():
        return -1, 1
    
    @staticmethod
    def east():
        return 0, 1
    
    @staticmethod
    def south_east():
        return 1, 1
    
    @staticmethod
    def south():
        return 1, 0
    
    @staticmethod
    def south_west():
        return 1, -1
    
    @staticmethod
    def west():
        return 0, -1
    
    @staticmethod
    def north_west():
        return -1, -1

directions = [Direction.north(), Direction.north_east(), Direction.east(), Direction.south_east(), 
              Direction.south(), Direction.south_west(), Direction.west(), Direction.north_west()]

def inside(env, x, y):
    rows, cols = len(env), len(env[0])
    return 0 <= x < rows and 0 <= y < cols

def build_path(start, end, pi):
    if not end in pi: return []

    path, curr = [], end
    while curr != start:
        path.append(curr)
        curr = pi[curr]
    path.append(start)
    path.reverse()

    return path

def random_walk(env, visited, pi, start_pos, curr_pos, length):
    dirs = list(directions)
    x, y = curr_pos
    curr_len = visited[x][y]

    while curr_len < length and len(dirs) > 0:
        dx, dy = dirs[random.randint(0, len(dirs) - 1)]
        nx, ny = x + dx, y + dy

        if inside(env, nx, ny) and (nx, ny) != start_pos and visited[nx][ny] == 0: 
            pi[nx, ny] = (x, y)
            visited[nx][ny] = visited[x][y] + 1
            rx, ry = random_walk(env, visited, pi, start_pos, (nx, ny), length)
            if visited[rx][ry] == length:
                return (rx, ry)
        
        dirs.remove((dx, dy))

    return curr_pos

def find_playpen_cells(env, length):
    rows, cols = len(env), len(env[0])
    visited, pi = [[0 for _ in range(cols)] for _ in range(rows)], {}
    start_pos = random.randint(0, rows - 1), random.randint(0, cols - 1)
    end_pos = random_walk(env, visited, pi, start_pos, start_pos, length)

    play_pen_cells = build_path(start_pos, end_pos, pi)

    return play_pen_cells
    
def find_paths(env, s, obstacles):
    def match_obstacles(curr_cell):
        if not obstacles: 
            return False

        c1, c2, c3 = curr_cell
        for t1, t2, t3 in obstacles:
            if isinstance(c1, t1) and isinstance(c2, t2) and isinstance(c3, t3):
                return True
        
        return False

    rows, cols = len(env), len(env[0])
    visited = [[0 for _ in range(cols)] for _ in range(rows)]
    q, pi = [s], {}

    while len(q) > 0:
        x, y  = q.pop()

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            next_pos = (nx, ny)
            if inside(env, nx, ny) and next_pos != s and visited[nx][ny] == 0 and not match_obstacles(env[nx][ny]):
                q.insert(0, next_pos)
                pi[next_pos] = (x, y)
                visited[nx][ny] = visited[x][y] + 1
    
    return pi, visited

def count_dirty_cells(env):
    count = 0
    for line in env:
        for _, dirt_pos, _ in line:
            if isinstance(dirt_pos, Dirt):
                count += 1
    
    return count

def count_void_cells(env):
    count = 0
    for line in env:
        for _, cell_center, _ in line:
            if isinstance(cell_center, Void):
                count += 1
    
    return count

def children_in_play_pen(env):
    count = 0
    for line in env:
        for _, play_pen_pos, child_pos in line:
            if isinstance(child_pos, Child) and isinstance(play_pen_pos, PlayPen):
                count += 1
    
    return count

def get_children(env):
    children = []
    for line in env:
        for _, child_in_pos1, child_in_pos2 in line:
            if isinstance(child_in_pos1, Child):
                children.append(child_in_pos1)

            if isinstance(child_in_pos2, Child):
                children.append(child_in_pos1)
    
    return children