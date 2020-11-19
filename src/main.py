from agents import *
from environment import *
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

def run_simulation(env, file, t=50):
    register_msg(f'\n{pretty_print_env(env)}\n', file, only_file=True)
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

        register_msg(f'\n{pretty_print_env(env)}\n', file, only_file=True)

        dirty_cells = count_dirty_cells(env)
        t0 += 1
    
    if t0 == 100 * t + 1:
        register_msg(f'\nLa simulación terminó porque se alcanzó el tiempo {100 * t}\n\n', file)
    elif dirty_cells >= 0.6 * (void_cells + dirty_cells):
        register_msg(f'\nLa simulación terminó porque la casa estaba sucia. El robot fue despedido\n\n', file)
    else:
        register_msg(f'\nLa simulación terminó porque el robot logró poner a los niños en el corral y limpiar la casa\n\n', file)

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