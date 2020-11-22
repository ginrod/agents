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

def register_msg(msg, file, print_to_file=False, print_to_console=True):
    if print_to_file:
        file.write(msg)
    
    if print_to_console:
        print(msg, end="")

def create_initial_environment():
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
                env[x][y] = (Void(x, y), Void(x, y), Void(x, y))


    # Generate play pen cells
    playpen_cells = find_playpen_cells(env, play_pen_cells_count - 1)

    # Generating play pen cells
    free_cells = [(x, y) for y in range(cols) for x in range(rows)]
    for x, y in playpen_cells:
        env[x][y] = (Void(x, y), Playpen(x, y), Void(x, y))
        free_cells.remove((x, y))
    
    # Generating robot
    idx = random.randint(0, len(free_cells) - 1)
    robotX, robotY = free_cells[idx]

    pi_no_obstacles, _ = find_paths(env, (robotX, robotY), obstacles=None)

    # Generating obstacles
    for _ in range(obstacles_count):
        idx = random.randint(0, len(free_cells) - 1)
        x, y = free_cells[idx]
        env[x][y] = (Void(x, y), Obstacle(x, y), Void(x, y))
        free_cells.remove((x, y))

    walk_obstacles = ((Void, Obstacle, Void),)
    pi, _ = find_paths(env, (robotX, robotY), obstacles=walk_obstacles)
    free_cells = [pos for pos in free_cells if pos in pi]

    # Check that all playpen cells are achievable
    for x, y in playpen_cells:
        if (x, y) not in pi:
            shortest_path_without_obstacles = build_path((robotX, robotY), (x, y), pi_no_obstacles)
            for x, y in shortest_path_without_obstacles[1:len(shortest_path_without_obstacles)-1]:
                env[x][y] = (Void(x, y), Void(x, y), Void(x, y))
                if (x, y) not in free_cells:
                    free_cells.append((x,y))

    # If obstacles and playpen let to few achivable cells try again
    if len(free_cells) < children_count + dirt_count:
        return create_initial_environment()

    # Generating dirt
    for _ in range(dirt_count):
        idx = random.randint(0, len(free_cells) - 1)
        x, y = free_cells[idx]
        env[x][y] = (Void(x, y), Dirt(x, y), Void(x, y))
        free_cells.remove((x, y))

    # Generating children
    for child_num in range(children_count):
        idx = random.randint(0, len(free_cells) - 1)
        x, y = free_cells[idx]
        child = Child(x, y)
        child.num = child_num
        env[x][y] = (Void(x, y), child, Void(x, y))
        free_cells.remove((x, y))

    return env, (robotX, robotY)

def run_simulation(env, file, t=50, print_to_file=False, sim_stats={}, sim_num=None, env_num=None, robot_num=None):
    if sim_num == 2 and env_num == 2 and robot_num == 0:
        foo = 0

    # register_msg(f'\n\n#Turno 0', file, print_to_file, print_to_console=False)
    register_msg(f'\n\n#Turno 0', file, print_to_file, print_to_console=True)
    # register_msg(f'{pretty_print_env(env)}\n\n', file, print_to_file, print_to_console=False)
    register_msg(f'{pretty_print_env(env)}\n\n', file, print_to_file, print_to_console=True)
    rows, cols = len(env), len(env[0])

    t0 = 1
    dirty_cells, void_cells = count_dirty_cells(env), count_void_cells(env)
    children, robot = get_children(env), get_robot(env)
    in_play_pen = children_in_play_pen(env)
    env_info = { 'dirty-cells': dirty_cells, 'void-cells': void_cells, 'children': children, 'in-play-pen': in_play_pen }

    while t0 <= 100 * t:
        if sim_num == 11 and t0 == 3:
            foo = 0

        if dirty_cells >= 0.6 * (void_cells + dirty_cells):
            break

        if in_play_pen == len(children) and dirty_cells == 0:
            break

        # register_msg(f'#Turno {t0}', file, print_to_file, print_to_console=False)
        register_msg(f'#Turno {t0}', file, print_to_file, print_to_console=True)
        
        # Performe a robot turn
        robot.perform_action(env, env_info)

        # Performe an environment change
        all_grids = get_3x3_grids(env)
        children_in_grid_dic = { grid : children_in_grid(env, grid) for grid in all_grids}

        for child in children:
            if child.num == 4:
                foo = 0

            if child == robot.carried_child:
                continue
            
            x, y = child.x, child.y
            if isinstance(env[x][y][1], Playpen):
                continue

            child.react(env)
        
        for grid_left_corner in all_grids:
            dirt_grid(env, grid_left_corner, children_in_grid_dic)

        # Performe a random environment change
        if t0 % t == 0:
            register_msg(' (de variación aleatoria)', file, print_to_file, print_to_console=False)
            random_change(env, robot, children)

        # register_msg(f'{pretty_print_env(env)}\n\n', file, print_to_file, print_to_console=False)
        register_msg(f'{pretty_print_env(env)}\n\n', file, print_to_file, print_to_console=True)

        dirty_cells, void_cells, in_play_pen = count_dirty_cells(env), count_void_cells(env), children_in_play_pen(env)
        env_info['dirty-cells'], env_info['void-cells'], env_info['in-play-pen'] = dirty_cells, void_cells, in_play_pen

        t0 += 1
    
    robot_type = isinstance(robot, ProactiveAgent) and 'ProactiveAgent' or 'ReactiveAgent'

    if t0 == 100 * t + 1:
        register_msg(f'\nLa simulación terminó porque se alcanzó el tiempo {100 * t}\n\n', file, print_to_file=True)
        sim_stats[robot_type]['time'] += 1
    elif dirty_cells >= 0.6 * (void_cells + dirty_cells):
        register_msg(f'\nLa simulación terminó porque la casa estaba sucia. El robot fue despedido\n\n', file, print_to_file=True)
        sim_stats[robot_type]['fired'] += 1
    else:
        register_msg(f'\nLa simulación terminó porque el robot logró poner a los niños en el corral y limpiar la casa\n\n', file, print_to_file=True)
        sim_stats[robot_type]['finish'] += 1

def clone_env(env):
    rows, cols = len(env), len(env[0])
    cloned_env = [[None for _ in range(cols)] for _ in range(rows)]

    for x in range(rows):
        for y in range(cols):
            o1, o2, o3 = env[x][y]
            cloned_env[x][y] = o1.clone(), o2.clone(), o3.clone()
    
    return cloned_env

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', type=int, default=10)
    # parser.add_argument('-i', '--iter', type=int, default=30)
    parser.add_argument('-i', '--iter', type=int, default=1)
    # parser.add_argument('-p', '--print-to-file', type=bool, default=False)
    parser.add_argument('-p', '--print-to-file', type=bool, default=True)

    args = parser.parse_args()
    t, iterations, print_to_file = args.time, args.iter, args.print_to_file

    with open('sim_logs.txt', 'w', encoding='utf-8'): pass
    file = open('sim_logs.txt', 'a', encoding='utf-8')
    
    agents = [ProactiveAgent, ReactiveAgent]
    # agents = [ReactiveAgent, ProactiveAgent]

    sim_stats = {}
    for agent in ['ProactiveAgent', 'ReactiveAgent']:
        sim_stats[agent] = { 'fired': 0, 'finish': 0, 'time': 0 }
    
    random.seed("seed")

    sim_num = 1
    environments = [create_initial_environment() for _ in range(10)]
    for r_num, agent in enumerate(agents):
        for e_num, env_info in enumerate(environments):
            if sim_num == 12 and e_num + 1 == 2 and r_num == 1:
                foo = 0
                env, (rx, ry) = env_info # env and robot position
                o1, o2 = env[7][2], env[7][3]

            env, (rx, ry) = env_info # env and robot position
            env = clone_env(env) # use a clone of the env to keep the initial one

            env[rx][ry] = (Void(rx, ry), agent(rx, ry), Void(rx, ry))

            for _ in range(iterations):
                register_msg(f"#Simulacion {sim_num}\n", file, print_to_file=True)
                register_msg(f"#Robot de tipo {r_num}\n", file, print_to_file=True)
                register_msg(f"#Ambiente {e_num + 1}", file, print_to_file=True)
                run_simulation(env, file, t, print_to_file, sim_stats, sim_num, e_num + 1, r_num)
                sim_num += 1
    
    for agent, stats in sim_stats.items():
        register_msg(f'{agent}\n', file, print_to_file=True, print_to_console=True)
        register_msg(f'Fue despedido: {stats["fired"]} veces\n', file, print_to_file=True, print_to_console=True)
        register_msg(f'Completó la tarea: {stats["finish"]} veces\n', file, print_to_file=True, print_to_console=True)
        register_msg(f'Se detuvo por tiempo: {stats["time"]} veces\n\n', file, print_to_file=True, print_to_console=True)
    
    file.close()