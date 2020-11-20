from environment import *

class Objective:

    @staticmethod
    def build_dirty_alert_objective(env, robot_pos):
        def find(env, robot_pos):
            rows, cols = len(env), len(env[0])
            obstacles = ((Void, Obstacle, Void),)
            pi, visit  = find_paths(env, robot_pos, obstacles)

            closest_path_dirt_len = rows * cols
            closest_dirt_pos = 0, 0
            for x in range(rows):
                for y in range(cols):
                    if isinstance(env[x][y][1], Dirt) and visit[x][y] < closest_path_dirt_len:
                        closest_path_dirt_len = visit[x][y]
                        closest_dirt_pos = x, y
            
            return build_path(robot_pos, closest_dirt_pos, pi)

    def __init__(self, find_func, perfom_func, name=None):
        self.is_in_course = False
        self.find_func = find_func
        self.perfom_func = perfom_func
        self.name = name

class Agent(EnvironmentElement):
    def __str__(self):
        return ' R '

class MySmartAgent(Agent):

    @property
    def objectives(self):
        pass

    def check_dirty_alert(self, void_cells):
        dirty_cells = count_dirty_cells(self.env)

        return dirty_cells >= 0.55 * (void_cells + dirty_cells)

class ProactiveAgent(Agent):
    pass

class ReactiveAgent(Agent):
    pass