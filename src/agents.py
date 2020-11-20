from environment import *

class Objective:

    @staticmethod
    def build_dirty_alert_objective(env, robot):
        def find(env, robot):
            robot_pos = robot.x, robot.y
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

        def perform(env, robot):
            robot_pos = robot.x, robot.y
            path = find(env, robot_pos)
            x, y = robot_pos

            if len(path) == 1:
                robot.clean()
                return

            robot.move(path[1])
        
        return Objective(find, perform, name="dirty-alert")

    @staticmethod
    def build_clean_objective(env, robot):
        def find(env, robot):
            robot_pos = robot.x, robot.y
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

        def perform(env, robot):
            robot_pos = robot.x, robot.y
            path = find(env, robot_pos)
            x, y = robot_pos

            if len(path) == 1:
                robot.clean()
                return

            robot.move(path[1])
        
        return Objective(find, perform, name="clean")
    
    @staticmethod
    def build_bring_children_to_playpen_objective(env, robot, children):
        def find_child(env, robot):
            robot_pos = robot.x, robot.y
            rows, cols = len(env), len(env[0])
            obstacles = ((Void, Obstacle, Void),)
            pi, visit  = find_paths(env, robot_pos, obstacles)

            closest_path_child_len = rows * cols
            closest_child_pos = 0, 0
            for x in range(rows):
                for y in range(cols):
                    if isinstance(env[x][y][1], Child) and visit[x][y] < closest_path_dirt_len:
                        closest_path_child_len = visit[x][y]
                        closest_child_pos = x, y
            
            return build_path(robot_pos, closest_child_pos, pi)
        
        def find_playpen(env, robot, children):
            robot_pos = robot.x, robot.y
            rows, cols = len(env), len(env[0])
            obstacles = ((Void, Obstacle, Void), (Void, Playpen, Child))
            pi, visit  = find_paths(env, robot_pos, obstacles)

            closest_path_playpen_len = rows * cols
            closest_playpen_pos = 0, 0
            in_play_pen = children_in_play_pen(env)

            for x in range(rows):
                for y in range(cols):
                    if isinstance(env[x][y][1], Child) and visit[x][y] < closest_path_dirt_len and \
                        (in_play_pen == len(children) - 1 or not creates_a_barrier(env, (x,y))):
                        closest_path_playpen_len = visit[x][y]
                        closest_playpen_pos = x, y
            
            return build_path(robot_pos, closest_playpen_pos, pi)
        
        def find(env, robot, children):
            return not robot.carring_child and find_child(env, robot) or find_playpen(env, robot, children)

        def perform(env, robot):
            robot_pos = robot.x, robot.y
            path = find(env, robot_pos)
            x, y = robot_pos

            if len(path) == 1:
                if not robot.carried_child:
                    robot.move()
                else:
                    robot.drop()
                return

            robot.move(path[1])
        
        return Objective(find, perform, name="bring-children-to-playpen")

    def __init__(self, find_func, perform_func, name=None):
        self.is_in_course = False
        self.find_func = find_func
        self.perform_func = perform_func
        self.name = name

class Agent(EnvironmentElement):
    def __str__(self):
        return ' R '

class MySmartAgent(Agent):

    def __init__(self, x, y, env):
        super(MySmartAgent, self).__init__(x, y, env)
        self.carried_child = None

    @property
    def objectives(self):
        pass
    
    def _carry_child(self, new_pos):
        nx, ny = new_pos
        # Move to new_pos position
        x, y, env = self.x, self.y, self.env
        self.env[self.x][self.y] = (Void(x, y, env), Void(x, y, env), Void(x, y, env))
        self.x, self.y = nx, ny

        _, child_in_pos1, child_in_pos2 = env[nx][ny]

        if isinstance(child_in_pos1, Child):
            env[nx][ny] = (self, child_in_pos1, Void(nx, ny, env))
            self.carried_child = child_in_pos1
        else:
            env[nx][ny] = (self, env[nx][ny][1], child_in_pos2)
            self.carried_child = child_in_pos1

    def move(self, new_pos, children):
        nx, ny = new_pos
        void = ((Void, Void, Void),)

        for child in children:
            child_pos = child.x, child.y
            if child_pos == new_pos:
                if self.carried_child and not isinstance(self.env[nx][y], void):
                    # trigger clear-block objective
                    pass
                else:
                    if self.carried_child:
                        self.carried_child.x, self.carried_child.y = nx, ny
                    self._carry_child(new_pos)
                return
        
        if self.carried_child and not isinstance(self.env[nx][y], void):
            # trigger clear-block objective
            pass
        else:
            if self.carried_child:
                self.carried_child.x, self.carried_child.y = nx, ny
            self._move(new_pos)

    def check_dirty_alert(self, void_cells):
        dirty_cells = count_dirty_cells(self.env)

        return dirty_cells >= 0.55 * (void_cells + dirty_cells)
    
    def clean(self):
        x, y, env = self.x, self.y, self.env
        robot = env[x][y][0]
        env[x][y] = (Void(x, y, env), robot, Void(x, y, env))
    
    def perform_action(self, env_info):
        raise NotImplementedError

class ProactiveAgent(MySmartAgent):
    def perform_action(env_info):
        dirty_cells, void_cells, children = env_info

class ReactiveAgent(MySmartAgent):
    def perform_action(env_info):
        dirty_cells, void_cells, children = env_info