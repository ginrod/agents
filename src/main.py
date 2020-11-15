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
            env[x][y] = Playpen(x, y, env)
            free_cells.remove((x, y))
    
    # Generating dirt
    for _ in range(dirt_count):
        idx = random.randint(0, len(free_cells))
        x, y = free_cells[idx]
        env[x][y] = Dirt(x, y, env)
        free_cells.remove((x, y))
    
    # Generating obstacles
    for _ in range(obstacles_count):
        idx = random.randint(0, len(free_cells))
        x, y = free_cells[idx]
        env[x][y] = Obstacle(x, y, env)
        free_cells.remove((x, y))
    
    # Generating children
    for _ in range(children_count):
        idx = random.randint(0, len(free_cells))
        x, y = free_cells[idx]
        env[x][y] = Child(x, y, env)
        free_cells.remove((x, y))
    
    # Generating robot
    idx = random.randint(0, len(free_cells))
    x, y = free_cells[idx]
    env[x][y] = agent(x, y, env)

    return env

def run_simulation(env):
    pass

if __name__ == '__main__':
    with open('sim_logs.txt', 'w'): pass
    file = open('sim_logs.txt', 'a')
    
    agents = [ProactiveAgent, ReactiveAgent]
    sim_num = 1
    for r_num, agent in enumerate(agents):
        environments = [create_initial_environment(agent) for _ in range(10)]
        for e_num, environment in enumerate(environments):
            register_msg(f"#Simulacion {sim_num}\n", file)
            register_msg(f"#Robot de tipo {r_num}\n", file)
            register_msg(f"#Ambiente {e_num + 1}", file)
            run_simulation(environment)
            sim_num += 1
    
    file.close()