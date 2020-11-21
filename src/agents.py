from environment import *

class Objective:

    @staticmethod
    def build_dirty_alert_objective():
        def find(env, robot, env_info):
            robot_pos = robot.x, robot.y
            rows, cols = len(env), len(env[0])
            obstacles = ((Void, Obstacle, Void),)
            pi, visit  = find_paths(env, robot_pos, obstacles)

            closest_path_dirt_len = rows * cols
            closest_dirt_pos = -1, -1
            for x in range(rows):
                for y in range(cols):
                    if isinstance(env[x][y][1], Dirt) and visit[x][y] < closest_path_dirt_len:
                        closest_path_dirt_len = visit[x][y]
                        closest_dirt_pos = x, y
            
            if closest_dirt_pos == (-1, -1):
                return [robot_pos]

            return build_path(robot_pos, closest_dirt_pos, pi)

        def perform(env, robot, env_info):
            robot_pos = robot.x, robot.y
            path = find(env, robot_pos)
            x, y = robot_pos

            if len(path) == 1:
                robot.clean()
                return

            robot.move(path[1])
        
        def check_if_completed(objective, env, robot, env_info):
            void_cells, dirty_cells = env_info['void-cells'], env_info['dirty_cells']
            return robot.check_dirty_alert(void_cells, dirty_cells)

        return Objective(find, perform, check_if_completed, name="dirty-alert")

    @staticmethod
    def build_clean_objective():
        def find(env, robot, env_info):
            robot_pos = robot.x, robot.y
            rows, cols = len(env), len(env[0])
            obstacles = ((Void, Obstacle, Void),)
            pi, visit  = find_paths(env, robot_pos, obstacles)

            closest_path_dirt_len = rows * cols
            closest_dirt_pos = -1, -1
            for x in range(rows):
                for y in range(cols):
                    if isinstance(env[x][y][1], Dirt) and visit[x][y] < closest_path_dirt_len:
                        closest_path_dirt_len = visit[x][y]
                        closest_dirt_pos = x, y
            
            if closest_dirt_pos == (-1, -1):
                return [robot_pos]
            
            return build_path(robot_pos, closest_dirt_pos, pi)

        def perform(env, robot, env_info):
            robot_pos = robot.x, robot.y
            path = find(env, robot_pos)
            x, y = robot_pos

            if len(path) == 1:
                robot.clean()
                return

            robot.move(path[1])
        
        def check_if_completed(objective, env, robot, env_info):
            rx, ry = robot.x, robot.y
            if objective.on_dirty_cell:
               objective.on_dirty_cell = False
               return True
            
            objective.on_dirty_cell = isinstance(env[rx][ry][1], Dirt)
            return False

        return Objective(find, perform, check_if_completed, name="clean")
    
    @staticmethod
    def build_bring_children_to_playpen_objective(env, robot, env_info):
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
            
            if closest_dirt_pos == (-1, -1):
                return [robot_pos]
            
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
        
        def find(env, robot, env_info):
            children = env_info['children']
            return not robot.carring_child and find_child(env, robot) or find_playpen(env, robot, children)

        def perform(env, robot, env_info):
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
        
        def check_if_completed(objective, env, robot, env_info):
            rx, ry = robot.x, robot.y
            return isinstance(env[rx][ry], ((Agent, Playpen, Child),)) and not robot.carried_child

        return Objective(find, perform, check_if_completed, name="bring-children-to-playpen")

    @staticmethod
    def build_clear_block_objective(env, robot, env_info):
        def find(env, robot, env_info):
            blocked_pos = env_info['blocked-pos']
            robot_pos = robot.x, robot.y
            if robot_pos == blocked_pos and robot.carried_child:
                obstacles = ((Void, Obstacle, Void), (Void, Playpen, Child))
                for dx, dy in directions:
                    nx, ny = robot.x + dx, robot.y + dy
                    if inside(env, nx, ny) and not isinstance(env[nx][ny], obstacles):
                        return nx, ny
            
            return blocked_pos

        def perform(env, robot, env_info):
            blocked_pos = env_info['blocked-pos']
            pos = find(env, robot, blocked_pos)
            robot_pos = robot.x, robot.y
            if robot_pos != blocked_pos and robot.carried_child:
                robot.drop()
            elif robot_pos != blocked_pos:
                robot.move(pos)
            else:
                robot.clean(pos)
        
        def check_if_completed(objective, env, robot, env_info):
            bx, by = env_info['blocked-pos']

            return isinstance(env[bx][by][1], Void) or \
                  (isinstance(env[bx][by][1], Playpen) and isinstance(env[bx][by][2], Void))

        return Objective(find, perform, check_if_completed. name="clear-block")
    
    def __init__(self, find_func, perform_func, check_if_completed_func, name=None):
        self.is_in_course = False
        self.find = find_func
        self.perform = perform_func
        self.check_if_completed = check_if_completed_func
        self.name = name
        self.on_dirty_cell = False
    
class Agent(EnvironmentElement):
    def __str__(self):
        return ' R '

class MySmartAgent(Agent):

    def __init__(self, x, y, env)
        super(MySmartAgent, self).__init__(x, y, env)
        self.carried_child = None
        dirty_alert = Objective.build_dirty_alert_objective()
        clean = Objective.build_clean_objective()
        bring_children_to_playpen = Objective.build_bring_children_to_playpen_objective()
        clear_block = Objective.build_clear_block_objective()
        self.objectives = { 
            dirty_alert.name: dirty_alert, clear_block.name: clear_block,
            bring_children_to_playpen.name : bring_children_to_playpen, clean.name: clean
        }
    
    def drop(self):
        if not self.carried_child:
            print('CALL TO DROP ON ROBOT WITH NO CARRIED CHILD')
            return
        
        self.carried_child = None
    
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

    def check_dirty_alert(self, void_cells, dirty_cells):
        return dirty_cells >= 0.55 * (void_cells + dirty_cells)
    
    def clean(self):
        x, y, env = self.x, self.y, self.env
        robot = env[x][y][0]
        env[x][y] = (Void(x, y, env), robot, Void(x, y, env))

    def get_closest_objective(self, pi, visit):
        robot_pos, env = (self.x, self.y), self.env
        rows, cols = len(env), len(env[0])

        closest_path_len = rows * cols
        closest_target_pos = -1, -1
        objectives_targets = self.carried_child and ((Void, Playpen, Void), (Void, Dirt, Void)) or \
                             ((Void, Child, Void), (Void, Dirt, Void))

        for x in range(rows):
            for y in range(cols):
                if isinstance(env[x][y], objectives_targets) and visit[x][y] < closest_path_len:
                    closest_path_len = visit[x][y]
                    closest_target_pos = x, y
        
        tx, ty = closest_target_pos
        target = env[tx][ty][1]
        objectives_name = isinstance(target, Dirt) and 'clean' or 'bring-children-to-playpen'
        
        return objectives_name, closest_target_pos

    def perform_action(self, env_info):
        raise NotImplementedError

class ProactiveAgent(MySmartAgent):
    def __init__(self, x, y, env, ignored_objectives_limit=20)
        super(ProactiveAgent, self).__init__(x, y, env)
        self.ignored_objectives = 0
        self.ignored_objectives_limit = ignored_objectives_limit
        self.change_behaviour = Falseinterrupted_objectives_limit

    def perform_action(self, env_info):
        dirty_cells = env_info['dirty-cells']
        void_cells =  env_info['void_cells']
        children = env_info['children']

        if self.ignored_objectives >= self.ignored_objectives_limit:
            self.ignored_objectives = 0
            self.change_behaviour = True

        if self.check_dirty_alert(void_cells, dirty_cells):
            for objective in self.objectives.values():
                objective.is_in_course = False
            
            self.objectives['dirty-alert'].is_in_course = True

        active_objective = None
        for objective in self.objectives.values():
            if objective.is_in_course:
                active_objective = objective
                break
        
        robot_pos, env = (self.x, self.y), self.env
        obstacles = ((Void, Obstacle, Void),)
        pi, visit = find_paths(env, robot_pos, obstacles)

        if active_objective:
            if active_objective.name not in ['clear-block', 'dirty-alert']:
                # Search closest objective
                closest_objective_name, closest_target_pos = self.get_closest_objective(pi, visit)
                if active_objective.name != closest_objective_name:
                    if not self.change_behaviour:
                        self.ignored_objectives += 1
                    else:
                        active_objective.is_in_course = False
                        active_objective = self.objectives[closest_objective_name]
                        active_objective.is_in_course = True
                        self.change_behaviour = False

            active_objective.perform()
            active_objective.check_if_completed(active_objective, env, self, env_info)

        else:
            # Search closest objective
            closest_objective_name, closest_target_pos = self.get_closest_objective(pi, visit)

class ReactiveAgent(MySmartAgent):
    def __init__(self, x, y, env, interrupted_objectives_limit=10)
        super(ReactiveAgent, self).__init__(x, y, env)
        self.interrupted_objectives = 0
        self.interrupted_objectives_limit = interrupted_objectives_limit
        self.change_behaviour = Falseinterrupted_objectives_limit

    def perform_action(self, env_info):
        dirty_cells = env_info['dirty-cells']
        void_cells =  env_info['void_cells']
        children = env_info['children']

        if self.interrupted_objectives >= self.interrupted_objectives_limit:
            self.interrupted_objectives_limit = 0
            self.change_behaviour = True

        if self.check_dirty_alert(void_cells, dirty_cells):
            for objective in self.objectives.values():
                objective.is_in_course = False
            
            self.objectives['dirty-alert'].is_in_course = True

        active_objective = None
        for objective in self.objectives.values():
            if objective.is_in_course:
                active_objective = objective
                break
        
        robot_pos, env = (self.x, self.y), self.env
        obstacles = ((Void, Obstacle, Void),)
        pi, visit = find_paths(env, robot_pos, obstacles)

        if active_objective:
            if active_objective.name not in ['clear-block', 'dirty-alert']:
                # Search closest objective
                closest_objective_name, closest_target_pos = self.get_closest_objective(pi, visit)
                if active_objective.name != closest_objective_name:
                    if not self.change_behaviour:
                        self.interrupted_objectives += 1
                        active_objective.is_in_course = False
                        active_objective = self.objectives[closest_objective_name]
                        active_objective.is_in_course = True
                    else:
                        self.change_behaviour = False

            active_objective.perform()
            active_objective.check_if_completed(active_objective, env, self, env_info)

        else:
            # Search closest objective
            closest_objective_name, closest_target_pos = self.get_closest_objective(pi, visit)