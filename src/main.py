from entities import *
from agents import *
import random, math

def pretty_print_env(env):
    rows, cols = len(env), len(env[0])
    result = ''

    for i in range(rows):
        result += f'\n{env[i][0]}'
        for j in range(1, cols):
            result += f' {env[i][j]}'
    
    return result

def register_msg(msg, file, only_file=False):
    if not only_file:
        print(msg, end="")
    file.write(msg)

def create_initial_environment(agent):
    rows, cols = random.randint(5, 10), random.randint(5, 10)
    env = [[None for _ in range(cols)] for _ in range(rows)]
    
    total_cells = rows * cols
    available_cells_count = total_cells

    # Generate a dirt amount between the 10 and 20 % total cells
    dirt_count = math.floor(random.randint(10, 20) / 100 * total_cells)
    available_cells_count -= dirt_count

    # Generate a obstacles amount between the 10 and 20 % of total cells
    obstacles_count = math.floor(random.randint(10, 20) / 100 * total_cells)
    available_cells_count -= obstacles_count

    # Generate children count between the 10 and 20 % of available cells
    children_count = math.floor(random.randint(10, 20) / 100 * available_cells_count)
    play_pen_cells_count = children_count

    # Generating void cells
    for x in range(rows):
        for y in range(cols):
            if env[x][y] == None:
                env[x][y] = (Void(x, y, env), Void(x, y, env), Void(x, y, env))


    # Generate play pen cells
    playpen_cells = find_playpen_cells(env, play_pen_cells_count - 1)

    # Generating play pen cells
    free_cells = [(x, y) for y in range(cols) for x in range(rows)]
    for x, y in playpen_cells:
        env[x][y] = (Void(x, y, env), Playpen(x, y, env), Void(x, y, env))
        free_cells.remove((x, y))
    
    # Generating robot
    idx = random.randint(0, len(free_cells) - 1)
    robotX, robotY = free_cells[idx]
    env[x][y] = (Void(x, y, env), agent(x, y, env), Void(x, y, env))

    pi_no_obstacles, _ = find_paths(env, (robotX, robotY), obstacles=None)

    # Generating obstacles
    for _ in range(obstacles_count):
        idx = random.randint(0, len(free_cells) - 1)
        x, y = free_cells[idx]
        env[x][y] = (Void(x, y, env), Obstacle(x, y, env), Void(x, y, env))
        free_cells.remove((x, y))

    walk_obstacles = ((Void, Obstacle, Void),)
    pi, _ = find_paths(env, (robotX, robotY), obstacles=walk_obstacles)
    free_cells = [pos for pos in free_cells if pos in pi]

    # Check that all playpen cells are achievable
    for x, y in playpen_cells:
        if (x, y) not in pi:
            shortest_path_without_obstacles = build_path((robotX, robotY), (x, y), pi_no_obstacles)
            for x, y in shortest_path_without_obstacles[1:len(shortest_path_without_obstacles)-1]:
                env[x][y] = (Void(x, y, env), Void(x, y, env), Void(x, y, env))
                if (x,y) in free_cells: free_cells.remove((x,y))

    # Generating dirt
    count = min(dirt_count, len(free_cells))
    for _ in range(dirt_count):
        idx = random.randint(0, len(free_cells) - 1)
        x, y = free_cells[idx]
        env[x][y] = (Void(x, y, env), Dirt(x, y, env), Void(x, y, env))
        free_cells.remove((x, y))

    # Generating children
    for child_num in range(children_count):
        idx = random.randint(0, len(free_cells) - 1)
        x, y = free_cells[idx]
        child = Child(x, y, env)
        child.num = child_num
        env[x][y] = (Void(x, y, env), child, Void(x, y, env))
        free_cells.remove((x, y))

    return env

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
    children = 
    for line in env:
        for _, child_in_pos1, child_in_pos2 in line:
            if isinstance(child_in_pos1, Child) or isinstance(child_in_pos2, Child):
                count += 1
    
    return count


def run_simulation(env, file, t=50):
    register_msg(f'\n{pretty_print_env(env)}\n', file)
    rows, cols = len(env), len(env[0])

    t0 = 1
    dirty_cells, void_cells = count_dirty_cells(env), count_void_cells(env)
    children = get_children(env)

    while t0 <= 100 * t:
        if dirty_cells >= 0.6 * (void_cells + dirty_cells):
            break

        if children_in_play_pen(env) == len(children) and dirty_cells == 0:
            break
        
        # Performe a robot turn
        # Performe an environment change
        for child in children:
            child.react()

        # Performe a random environment change
        if t0 % t == 0:
            pass

        dirty_cells = count_dirty_cells(env)
        t0 += 1
    
    if t0 == t:
        register_msg(f'La simulación terminó porque se alcanzó el tiempo {100 * t}\n\n', file)
    elif dirty_cells >= 0.6 * total_cells:
        register_msg(f'La simulación terminó porque la casa estaba sucia. El robot fue despedido\n\n', file)
    else:
        register_msg(f'La simulación terminó porque el robot logró poner a los niños en el corral y limpiar la casa\n\n', file)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', type=int, default=50)
    args = parser.parse_args()
    t = args.time

    with open('sim_logs.txt', 'w', encoding='utf-8'): pass
    file = open('sim_logs.txt', 'a', encoding='utf-8')
    
    agents = [ProactiveAgent, ReactiveAgent]
    sim_num = 1
    for r_num, agent in enumerate(agents):
        environments = [create_initial_environment(agent) for _ in range(10)]
        for e_num, environment in enumerate(environments):
            for _ in range(30):
                register_msg(f"#Simulacion {sim_num}\n", file)
                register_msg(f"#Robot de tipo {r_num}\n", file)
                register_msg(f"#Ambiente {e_num + 1}", file)
                run_simulation(environment, file, t)
                sim_num += 1
    
    file.close()