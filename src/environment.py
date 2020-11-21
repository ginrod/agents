from entities import *

import random

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


def get_robot(env):
    for line in env:
        for robot_in_pos1, robot_in_pos2, _ in line:
            if isinstance(robot_in_pos1, Agent):
                return robot_in_pos1

            if isinstance(robot_in_pos2, Agent):
                return robot_in_pos2

def creates_vertical_barrier(env, pos):
    rows, cols = len(env), len(env[0])
    sx, sy = pos

    # Check if puting a child in pos (sx, sy) creates a vertical barrier of obstacles
    # considering a playpen with a child an obstacle for a robot carring another child
    obstacles = ((Void, Obstacle, Void), (Void, Playpen, Child))
    for y in range(cols):
        if y != ys and not isinstance(env[sx][y], obstacles):
            return False
    
    return True

def creates_horizontal_barrier(env, pos):
    rows, cols = len(env), len(env[0])
    sx, sy = pos

    # Check if puting a child in pos (sx, sy) creates a vertical barrier of obstacles
    # considering a playpen with a child an obstacle for a robot carring another child
    obstacles = ((Void, Obstacle, Void), (Void, Playpen, Child))
    for x in range(rows):
        if x != sx and not isinstance(env[x][sy], obstacles):
            return False
    
    return True

def creates_a_barrier(env, pos):
    # Check if puting a child in pos (sx, sy) creates a barrier of obstacles (vertical or horizontal)
    # considering a playpen with a child an obstacle for a robot carring another child
    return creates_vertical_barrier(env, pos) or creates_horizontal_barrier(env, pos)