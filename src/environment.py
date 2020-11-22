from entities import *

import random

def build_path(start, end, pi):
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

def match_types(curr_cell, types):
    if not types: 
        return False

    c1, c2, c3 = curr_cell
    for t1, t2, t3 in types:
        if isinstance(c1, t1) and isinstance(c2, t2) and isinstance(c3, t3):
            return True
    
    return False

def find_paths(env, s, obstacles):
    rows, cols = len(env), len(env[0])
    visited = [[0 for _ in range(cols)] for _ in range(rows)]
    q, pi = [s], {}

    while len(q) > 0:
        x, y  = q.pop()

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            next_pos = (nx, ny)
            if inside(env, nx, ny) and next_pos != s and visited[nx][ny] == 0 and not match_types(env[nx][ny], obstacles):
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
            if isinstance(child_pos, Child) and isinstance(play_pen_pos, Playpen):
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
        if y != sy and not match_types(env[sx][y], obstacles):
            return False
    
    return True

def creates_horizontal_barrier(env, pos):
    rows, cols = len(env), len(env[0])
    sx, sy = pos

    # Check if puting a child in pos (sx, sy) creates a vertical barrier of obstacles
    # considering a playpen with a child an obstacle for a robot carring another child
    obstacles = ((Void, Obstacle, Void), (Void, Playpen, Child))
    for x in range(rows):
        if x != sx and not match_types(env[x][sy], obstacles):
            return False
    
    return True

def creates_a_barrier(env, pos, robot_pos):
    # Check if puting a child in pos (sx, sy) creates a barrier of obstacles (vertical or horizontal)
    # considering a playpen with a child an obstacle for a robot carring another child
    creates_full_barrier = creates_vertical_barrier(env, pos) or creates_horizontal_barrier(env, pos)

    # walk_obstacles = ((Void, Obstacle, Void), (Void, Playpen, Child))
    # pi, _ = find_paths(env, robot_pos, obstacles=walk_obstacles)
    # playpen_cells = get_element_pos(env, Playpen)

    # any_isolated_playpen_cell = any(map(lambda playpen_pos: playpen_pos not in pi, playpen_cells))

    # return creates_full_barrier or any_isolated_playpen_cell
    return creates_full_barrier

def children_in_grid(env, grid_left_corner):
    sx, sy = grid_left_corner

    children = 0
    for x in range(sx, sx + 3):
        for y in range(sy, sy + 3):
            if match_types(env[x][y], ((Void, Child, Void),)):
                children += 1
    
    return children

def dirt_grid(env, grid_left_corner, children_in_grid_dic):
    sx, sy = grid_left_corner
    children = (sx, sy) in children_in_grid_dic and children_in_grid_dic[sx, sy] or 0 
    
    free_cells = []
    for x in range(sx, sx + 3):
        for y in range(sy, sy + 3):
            if isinstance(env[x][y][1], Void):
                free_cells.append((x, y))
    
    max_dirt_by_children_count = children == 1 and 1 or children == 2 and 3 or children >= 3 and 6 or 0
    random_count = random.randint(0, max_dirt_by_children_count)
    dirt_count = min(random_count, len(free_cells))

    for _ in range(dirt_count):
        idx = random.randint(0, len(free_cells) - 1)
        x, y = free_cells[idx]
        env[x][y] = (Void(x, y), Dirt(x, y), Void(x, y))

def get_element_pos(env, element):
    elements_positions = []
    for line in env:
        for _, element_in_center, _ in line:
            if isinstance(element_in_center, element):
                elements_positions.append((element_in_center.x, element_in_center.y))

    return elements_positions

def clear_positions(env, positions):
    for x, y in positions:
        env[x][y] = Void(x, y), Void(x, y), Void(x, y)

def random_change(env, robot, children):
    # Clear obstacles
    obstacles_positions = get_element_pos(env, Obstacle)
    clear_positions(env, obstacles_positions)
    
    # Clear positions of alone childs
    children_to_be_relocated = []
    for child in children:
        x, y = child.x, child.y
        if match_types(env[x][y], ((Void, Child, Void),)):
            env[x][y] = Void(x, y), Void(x, y), Void(x, y)
            children_to_be_relocated.append(child)
    
    # Clear dirts
    dirts_positions = get_element_pos(env, Dirt)
    if (robot.x, robot.y) in dirts_positions:
        dirts_positions.remove((robot.x, robot.y))

    clear_positions(env, dirts_positions)

    free_cells_positions = get_element_pos(env, Void)
    playpen_cells = get_element_pos(env, Playpen)

    retries = 0
    while retries <= 100:
        # Relocating obstacles
        free_cells = list(free_cells_positions)
        for _ in range(len(obstacles_positions)):
            idx = random.randint(0, len(free_cells) - 1)
            x, y = free_cells[idx]
            env[x][y] = (Void(x, y), Obstacle(x, y), Void(x, y))
            free_cells.remove((x, y))

        walk_obstacles = ((Void, Obstacle, Void),)
        pi, _ = find_paths(env, (robot.x, robot.y), obstacles=walk_obstacles)
        free_cells = [pos for pos in free_cells if pos in pi]

        # Checking that achivable cells count is enough for dirts and children for relocation
        if len(free_cells) < len(dirts_positions) + len(children_to_be_relocated):
            retries += 1
            continue
        
        # Checking that all playpen cells are achievable
        for x, y in playpen_cells:
            if (x, y) not in pi:
                retries += 1
                continue
        
        # Relocating children
        for child in children_to_be_relocated:
            idx = random.randint(0, len(free_cells) - 1)
            x, y = free_cells[idx]
            child.x, child.y = x, y
            env[x][y] = (Void(x, y), child, Void(x, y))
            free_cells.remove((x, y))
        
        # Relocating dirts
        for _ in range(len(dirts_positions)):
            idx = random.randint(0, len(free_cells) - 1)
            x, y = free_cells[idx]
            env[x][y] = (Void(x, y), Dirt(x, y), Void(x, y))
            free_cells.remove((x, y))
        
        break
    
    # Over a 100 attempts a feasible relocation could not be performed
    # so the objects will be return to the original positions
    if retries > 100:
        for x, y in obstacles_positions:
            env[x][y] = Void(x, y), Obstacle(x, y), Void(x, y)
        
        for child in children_to_be_relocated:
            x, y = child.x, child.y
            env[x][y] = Void(x, y), child, Void(x, y)
        
        for x, y in dirts_positions:
            env[x][y] = Void(x, y), Dirt(x, y), Void(x, y)

def deterimine_direction(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    
    return x2 - x1, y2 - y1

def get_3x3_grids(env):
    rows, cols = len(env), len(env[0])
    result = []
    for x in range(0, rows, 3):
        for y in range(0, cols, 3):
            if inside(env, x + 2, y + 2):
                result.append((x, y))
    
    return result

def get_playpen_cells_reachables_only_by_other_playpen_cells(env):
    playpen_cells = get_element_pos(env, Playpen)
    available_neighbours = set()

    for px, py in playpen_cells:
        for dx, dy in directions:
            nx, ny = px + dx, py + dy
            if not inside(env, nx, ny): continue
            if isinstance(env[nx][ny][1], (Agent, Void, Dirt)):
                available_neighbours.add((nx, ny))
    
    result = set()
    obstacles = ((Void, Obstacle, Void), (Void, Playpen, Void), (Void, Playpen, Child), (Agent, Playpen, Child), (Agent, Playpen, Void))
    for n_pos in available_neighbours:
        pi, _ = find_paths(env, n_pos, obstacles)
        for p_pos in playpen_cells:
            if p_pos not in pi:
                result.add(p_pos)
    
    return result

# The most across to an un reachable (without passing by others playpen cells) corner
def get_most_splitting(env, reachables_only_by_playpen):
    corner_dirs = [Direction.north_west(), Direction.north_east(), Direction.south_west(), Direction.south_east()]