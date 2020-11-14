from entities import *
from agents import *

def register_msg(msg, file):
    print(msg, end="")
    file.write(msg)

def create_initial_environment(agent):
    pass

def run_simulation(env):
    pass

if __name__ == '__main__':
    with open('sim_logs.txt', 'w'): pass
    file = open('sim_logs.txt', 'a')
    
    agents = [ProactiveAgent(), ReactiveAgent()]
    sim_num = 1
    for r_num, agent in enumerate(agents):
        environments = [create_initial_environment(agent) for _ in range(10)]
        for e_num, environment in enumerate(environments):
            register_msg(f"#Simulacion {sim_num}\n")
            register_msg(f"#Robot de tipo {r_num}\n")
            register_msg(f"#Ambiente {e_num + 1}")
            run_simulation(env)
            sim_num += 1
    
    file.close()