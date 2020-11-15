from entities import *
from agents import *
import random, math

def register_msg(msg, file):
    print(msg, end="")
    file.write(msg)

def create_initial_environment(agent):
    rows, cols = random.randint(5, 10), random.randint(5, 10)
    env = [[None for y in range(cols)] for x in range(rows)]
    
    total_cells = rows * cols
    available_cells_count = total_cells

    # Generate a dirt amount between the 10 and 20 % total cells
    dirt_count = math.floor(random.randrange(0.1, 0.2) * total_cells)
    available_cells_count -= dirt_count

    # Generate a obstacles amount between the 10 and 20 % of total cells
    obstacles_count = math.floor(random.randrange(0.1, 0.2) * total_cells)
    available_cells_count -= obstacles_count

    # Generate children between the 5 and 10 % of available cells
    children_count = math.floor(random.randrange(0.05, 0.1) * available_cells_count)
    play_pen_cells_count = children_count

    # Generate play pen dimensions
    play_pen_rows = random.randint(1, play_pen_cells_count)
    play_pen_cols = play_pen_cells_count // play_pen_rows

    # Generate play pen dimensions left corner
    play_pen_x = random.randint(0, play_pen_rows - 1)
    play_pen_y = random.randint(0, play_pen_cols - 1)

    # Generating play pen cells
    free_cells = [(x, y) for x in range(rows) for y in range(cols)]
    for x in range(play_pen_x, play_pen_rows):
        for y in range(play_pen_y, play_pen_cols):
            env[x][y] = (Void(x, y, env), Playpen(x, y, env), Void(x, y, env))
            free_cells.remove((x, y))
    
    # Generating dirt
    for _ in range(dirt_count):
        idx = random.randint(0, len(free_cells))
        x, y = free_cells[idx]
        env[x][y] = (Void(x, y, env), Dirt(x, y, env), Void(x, y, env))
        free_cells.remove((x, y))
    
    # Generating obstacles
    for _ in range(obstacles_count):
        idx = random.randint(0, len(free_cells))
        x, y = free_cells[idx]
        env[x][y] = (Void(x, y, env), Obstacle(x, y, env), Void(x, y, env))
        free_cells.remove((x, y))
    
    # Generating children
    for _ in range(children_count):
        idx = random.randint(0, len(free_cells))
        x, y = free_cells[idx]
        env[x][y] = (Void(x, y, env), Child(x, y, env), Void(x, y, env))
        free_cells.remove((x, y))
    
    # Generating robot
    idx = random.randint(0, len(free_cells))
    x, y = free_cells[idx]
    env[x][y] = (Void(x, y, env), agent(x, y, env), Void(x, y, env))

    # Generating void cells
    for x in range(rows):
        for y in range(cols):
            if env[x][y] == None:
                env[x][y] = [Void(x, y, env), Void(x, y, env), Void(x, y, env)]

    return env

def count_dirty_cells(env):
    count = 0
    for line in env:
        for _, dirt_pos, _ in line:
            if isinstance(dirt_pos, Dirt):
                count += 1
    
    return count

def children_in_play_pen(env):
    count = 0
    for line in env:
        for _, play_pen_pos, child_pos in line:
            if isinstance(child_pos, Child) and isinstance(play_pen_pos, PlayPen):
                count += 1
    
    return count

def count_children(env):
    count = 0
    for line in env:
        for _, child_in_pos1, child_in_pos2 in line:
            if isinstance(child_pos1, Child) or isinstance(child_in_pos2, Child):
                count += 1
    
    return count

def run_simulation(env, t=100):
    register_msg(f'\n{env}\n')
    total_cells = len(env) * len(env[0])

    t0 = 0
    dirty_cells = count_dirty_cells(env)
    children_count = count_children(env)

    # Performe a robot turn

    while t0 < t:
        if dirty_cells >= 0.6 * total_cells:
            break

        if children_in_play_pen(env) == children_count and dirty_cells = 0:
            break
        
        # Performe an environment change
        # Performe a robot turn

        dirty_cells = count_dirty_cells(env)
        t0 += 1
    
    if t0 == t:
        register_msg(f'La simulación terminó porque se alcanzó el tiempo {t}\n')
    elif dirty_cells >= 0.6 * total_cells:
        register_msg(f'La simulación terminó porque la casa estaba sucia. El robot fue despedido\n')
    else:
        register_msg(f'La simulación terminó porque el robot logró poner a lso niños en el corral y limpiar la casa\n')

if __name__ == '__main__':
    with open('sim_logs.txt', 'w'): pass
    file = open('sim_logs.txt', 'a')
    
    agents = [ProactiveAgent, ReactiveAgent]
    sim_num = 1
    for r_num, agent in enumerate(agents):
        environments = [create_initial_environment(agent) for _ in range(10)]
        for e_num, environment in enumerate(environments):
            for _ in range(30):
                register_msg(f"#Simulacion {sim_num}\n", file)
                register_msg(f"#Robot de tipo {r_num}\n", file)
                register_msg(f"#Ambiente {e_num + 1}", file)
                run_simulation(environment)
                sim_num += 1
    
    file.close()