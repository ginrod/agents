from environment import *

class Objective:

    @staticmethod
    def build_dirty_alert_objective():
        def find(objective, env, robot, env_info):
            robot_pos = robot.x, robot.y
            rows, cols = len(env), len(env[0])
            obstacles = ((Void, Obstacle, Void),)
            pi, visit  = find_paths(env, robot_pos, obstacles)

            closest_path_dirt_len = rows * cols
            closest_dirt_pos = -1, -1
            for x in range(rows):
                for y in range(cols):
                    if isinstance(env[x][y][1], Dirt) and visit[x][y] != 0 and visit[x][y] < closest_path_dirt_len:
                        closest_path_dirt_len = visit[x][y]
                        closest_dirt_pos = x, y
            
            if isinstance(env[robot.x][robot.y][1], Dirt):
                closest_dirt_pos = robot.x, robot.y
            
            if closest_dirt_pos == (-1, -1):
                return [robot_pos]

            return build_path(robot_pos, closest_dirt_pos, pi)

        def perform(objective, env, robot, env_info):
            robot_pos = robot.x, robot.y
            path = find(objective, env, robot, env_info)
            x, y = robot_pos

            if len(path) == 1:
                robot.clean(env)
                return
            
            if robot.carried_child: 
                if len(path) > 3:
                    d1 = deterimine_direction(path[0], path[1])
                    d2 = deterimine_direction(path[1], path[2])
                    nx, ny = path[1]
                    if d1 == d2 and isinstance(env[nx][ny][1], Void):
                        robot.move(env, env_info, path, 2)
                        return
                elif len(path) == 2:
                    robot.drop()
                    return

            robot.move(env, env_info, path, 1)
        
        def check_if_completed(objective, env, robot, env_info):
            void_cells, dirty_cells = env_info['void-cells'], env_info['dirty-cells']
            return robot.check_dirty_alert(void_cells, dirty_cells)

        return Objective(find, perform, check_if_completed, name="dirty-alert")

    @staticmethod
    def build_clean_objective():
        def find(objective, env, robot, env_info):
            robot_pos = robot.x, robot.y
            rows, cols = len(env), len(env[0])
            obstacles = ((Void, Obstacle, Void),)
            pi, visit  = find_paths(env, robot_pos, obstacles)

            closest_path_dirt_len = rows * cols
            closest_dirt_pos = -1, -1
            for x in range(rows):
                for y in range(cols):
                    if isinstance(env[x][y][1], Dirt) and visit[x][y] != 0 and visit[x][y] < closest_path_dirt_len:
                        closest_path_dirt_len = visit[x][y]
                        closest_dirt_pos = x, y
            
            if isinstance(env[robot.x][robot.y][1], Dirt):
                closest_dirt_pos = robot.x, robot.y
            
            if closest_dirt_pos == (-1, -1):
                return [robot_pos]
            
            return build_path(robot_pos, closest_dirt_pos, pi)

        def perform(objective, env, robot, env_info):
            robot_pos = robot.x, robot.y
            path = find(objective, env, robot, env_info)
            x, y = robot_pos

            if len(path) == 1:
                robot.clean(env)
                return
            
            if robot.carried_child: 
                if len(path) > 3:
                    d1 = deterimine_direction(path[0], path[1])
                    d2 = deterimine_direction(path[1], path[2])
                    nx, ny = path[1]
                    if d1 == d2 and isinstance(env[nx][ny][1], Void):
                        robot.move(env, env_info, path, 2)
                        return
                elif len(path) == 2:
                    robot.drop()
                    return

            robot.move(env, env_info, path, 1)
        
        def check_if_completed(objective, env, robot, env_info):
            rx, ry = robot.x, robot.y
            if objective.on_dirty_cell:
               objective.on_dirty_cell = False
               return True
            
            objective.on_dirty_cell = isinstance(env[rx][ry][1], Dirt)
            return False

        return Objective(find, perform, check_if_completed, name="clean")
    
    @staticmethod
    def build_bring_children_to_playpen_objective():
        def find_child(env, robot):
            robot_pos = robot.x, robot.y
            rows, cols = len(env), len(env[0])
            obstacles = ((Void, Obstacle, Void),)
            pi, visit  = find_paths(env, robot_pos, obstacles)

            closest_path_child_len = rows * cols
            closest_child_pos = -1, -1
            for x in range(rows):
                for y in range(cols):
                    if isinstance(env[x][y][1], Child) and visit[x][y] != 0 and visit[x][y] < closest_path_child_len:
                        closest_path_child_len = visit[x][y]
                        closest_child_pos = x, y
            
            if isinstance(env[robot.x][robot.y][1], Child):
                closest_child_pos = robot.x, robot.y
            
            if closest_child_pos == (-1, -1):
                return [robot_pos]
            
            return build_path(robot_pos, closest_child_pos, pi)
        
        def find_playpen(env, robot, children):
            robot_pos = robot.x, robot.y
            rows, cols = len(env), len(env[0])
            obstacles = ((Void, Obstacle, Void), (Void, Playpen, Child))
            pi, visit  = find_paths(env, robot_pos, obstacles)

            closest_path_playpen_len = rows * cols
            closest_playpen_pos = -1, -1
            in_play_pen = children_in_play_pen(env)

            for x in range(rows):
                for y in range(cols):
                    if isinstance(env[x][y][1], Playpen) and visit[x][y] != 0 and visit[x][y] < closest_path_playpen_len and \
                        (in_play_pen == len(children) - 1 or not creates_a_barrier(env, (x,y), robot_pos)):
                        closest_path_playpen_len = visit[x][y]
                        closest_playpen_pos = x, y
            
            if isinstance(env[robot.x][robot.y][1], Playpen):
                closest_playpen_pos = robot.x, robot.y
            
            pos = closest_playpen_pos

            if pos == (-1, -1):
                obstacles = ((Void, Obstacle, Void),)
                pi, visit  = find_paths(env, robot_pos, obstacles)

                farthest_path_playpen_len = 0
                farthest_playpen_pos = -1, -1

                target_cells = (Void, Playpen, Void),
                for x in range(rows):
                    for y in range(cols):
                        if match_types(env[x][y], target_cells) and visit[x][y] != 0 and visit[x][y] > farthest_path_playpen_len:
                            farthest_path_playpen_len = visit[x][y]
                            farthest_playpen_pos = x, y
                
                pos = farthest_playpen_pos
            
            return build_path(robot_pos, pos, pi)
        
        def find(objective, env, robot, env_info):
            children = env_info['children']
            return not robot.carried_child and find_child(env, robot) or find_playpen(env, robot, children)

        def perform(objective, env, robot, env_info):
            robot_pos = robot.x, robot.y
            path = find(objective, env, robot, env_info)
            x, y = robot_pos

            if isinstance(env[x][y][1], Playpen) and robot.carried_child:
                robot.drop()
                return
            
            if robot.carried_child and len(path) >= 3:
                d1 = deterimine_direction(path[0], path[1])
                d2 = deterimine_direction(path[1], path[2])
                nx, ny = path[1]
                if d1 == d2 and isinstance(env[nx][ny][1], Void):
                    robot.move(env, env_info, path, 2)
                    return
            
            if len(path) > 1:
                robot.move(env, env_info, path, 1)
        
        def check_if_completed(objective, env, robot, env_info):
            rx, ry = robot.x, robot.y
            return match_types(env[rx][ry], ((Agent, Playpen, Child),)) and not robot.carried_child

        return Objective(find, perform, check_if_completed, name="bring-children-to-playpen")

    @staticmethod
    def build_clear_block_objective():
        def find(objective, env, robot, env_info):
            blocked_pos = env_info['blocked-position']
            robot_pos = robot.x, robot.y
            new_pos = blocked_pos
            if robot_pos == blocked_pos and robot.carried_child:
                obstacles = ((Void, Obstacle, Void), (Void, Playpen, Child))
                for dx, dy in directions:
                    nx, ny = robot.x + dx, robot.y + dy
                    if inside(env, nx, ny) and not match_types(env[nx][ny], obstacles):
                        new_pos = nx, ny
            
            dx, dy = deterimine_direction(new_pos, robot_pos)
            # to leave the direction in unit when target blocked pos is 2 cells from robot
            dx, dy = dx and dx // abs(dx), dy and dy // abs(dy)
            path = []
            curr_x, curr_y = new_pos
            while (curr_x, curr_y) != robot_pos:
                path.append((curr_x, curr_y))
                curr_x, curr_y = curr_x + dx, curr_y + dy
            path.append(robot_pos)
            path.reverse()

            return path

        def perform(objective, env, robot, env_info):
            path = find(objective, env, robot, env_info)
            robot_pos = robot.x, robot.y
            blocked_pos = env_info['blocked-position']
            if robot_pos != blocked_pos and robot.carried_child:
                robot.drop()
            elif len(path) > 1:
                robot.move(env, env_info, path, 1)
            elif robot_pos == blocked_pos and isinstance(env[robot.x][robot.y][1], Dirt):
                robot.clean(env)
            
        def check_if_completed(objective, env, robot, env_info):
            bx, by = env_info['blocked-position']

            return isinstance(env[bx][by][1], (Void, Agent)) or \
                  (isinstance(env[bx][by][1], Playpen) and isinstance(env[bx][by][2], Void))

        return Objective(find, perform, check_if_completed, name="clear-block")
    
    @staticmethod
    def build_move_in_playpen_objective():
        def find(objective, env, robot, env_info):
            return objective.path

        def perform(objective, env, robot, env_info):
            idx, path = objective.idx, objective.path
            robot_pos = robot.x, robot.y
            
            if idx == len(path):
                robot.drop()
            elif robot.carried_child:
                nx, ny = path[idx]
                if isinstance(env[nx][ny][2], Child):
                    robot.drop()
                else:
                    robot.move(env, env_info, path, idx)
                    objective.idx += 1
            else:
                robot.move(env, env_info, path, idx)
                objective.idx += 1
            
        def check_if_completed(objective, env, robot, env_info):
            idx, path = objective.idx, objective.path

            return idx == len(path)

        return Objective(find, perform, check_if_completed, name="move-in-playpen")
    
    def __init__(self, find_func, perform_func, check_if_completed_func, name=None):
        self.is_in_course = False
        self.find = find_func
        self.perform = perform_func
        self.check_if_completed = check_if_completed_func
        self.name = name
        self.on_dirty_cell = False
        self.path = None
        self.idx = 0

class MySmartAgent(Agent):

    def __init__(self, x, y):
        super(MySmartAgent, self).__init__(x, y)
        self.carried_child = None
        dirty_alert = Objective.build_dirty_alert_objective()
        clean = Objective.build_clean_objective()
        bring_children_to_playpen = Objective.build_bring_children_to_playpen_objective()
        clear_block = Objective.build_clear_block_objective()
        move_in_playpen = Objective.build_move_in_playpen_objective()
        self.objectives = { 
            dirty_alert.name: dirty_alert, clear_block.name: clear_block,
            bring_children_to_playpen.name : bring_children_to_playpen, clean.name: clean,
            move_in_playpen.name : move_in_playpen
        }
    
    def _move(self, new_pos, env):
        nx, ny = new_pos
        # Move to new_pos position
        x, y = self.x, self.y
        self.x, self.y = nx, ny
        o1, o2, o3 = env[x][y]
        
        if o1 == self:
            env[x][y] = Void(x, y), o2, o3
        elif o2 == self:
            env[x][y] = Void(x, y), o1, o3
        else:
            env[x][y] = o1, o2, Void(x, y)

        if self.carried_child:
            _, child_in_pos1, child_in_pos2 = env[x][y]
            if isinstance(child_in_pos2, Child):
                env[x][y] = Void(x, y), env[x][y][1], Void(x, y)
            else:
                env[x][y] = Void(x, y), Void(x, y), Void(x, y)

        if isinstance(env[nx][ny][1], Void):
            env[nx][ny] = Void(nx, ny), self, Void(nx, ny)
        else:
            env[nx][ny] = self, env[nx][ny][1], env[nx][ny][2]
        
        if self.carried_child:
            if isinstance(env[nx][ny][1], Playpen):
                env[nx][ny] = self, env[nx][ny][1], self.carried_child
            else:
                env[nx][ny] = self, self.carried_child, Void(nx, ny)
    
    def drop(self):
        if not self.carried_child:
            print('CALL TO DROP ON ROBOT WITH NO CARRIED CHILD')
            return
        
        self.carried_child = None
    
    def _carry_child(self, new_pos, env):
        nx, ny = new_pos
        # Move to new_pos position
        x, y = self.x, self.y
        self.x, self.y = nx, ny
        o1, o2, o3 = env[x][y]
        
        if o1 == self:
            env[x][y] = Void(x, y), o2, o3
        elif o2 == self:
            env[x][y] = Void(x, y), o1, o3
        else:
            env[x][y] = o1, o2, Void(x, y)

        _, child_in_pos1, child_in_pos2 = env[nx][ny]

        if isinstance(child_in_pos1, Child):
            env[nx][ny] = self, child_in_pos1, Void(nx, ny)
            self.carried_child = child_in_pos1
        else:
            env[nx][ny] = self, env[nx][ny][1], child_in_pos2
            self.carried_child = child_in_pos2

    def get_active_objective(self):
        active_objective = None
        for objective in self.objectives.values():
            if objective.is_in_course:
                active_objective = objective
                break
        
        return active_objective

    def trigger_clear_block_objective(self, env, env_info):
        active_objective = self.get_active_objective()
        if active_objective:
            active_objective.is_in_course = False
        active_objective = self.objectives['clear-block']
        active_objective.is_in_course = True
        self.perform_action(env, env_info)
    
    def trigger_move_in_playpen_objective(self, env, env_info, path, idx):
        active_objective = self.get_active_objective()
        if active_objective:
            active_objective.is_in_course = False
        active_objective = self.objectives['move-in-playpen']
        active_objective.is_in_course = True
        active_objective.path = path
        active_objective.idx = idx
        self.perform_action(env, env_info)

    def move(self, env, env_info, path, idx):
        children = env_info['children']
        nx, ny = path[idx]
        availables = ((Void, Void, Void), (Void, Playpen, Void))

        child_in_play_pen = ((Void, Playpen, Child),)
        if self.carried_child and match_types(env[nx][ny], child_in_play_pen):
            # trigger move-in-playpen objective
            self.trigger_move_in_playpen_objective(env, env_info, path, idx)
            return

        for child in children:
            child_pos = child.x, child.y
            if child_pos == path[idx]:
                if self.carried_child and not match_types(env[nx][ny], availables):
                    # trigger clear-block objective
                    env_info['blocked-position'] = nx, ny
                    self.trigger_clear_block_objective(env, env_info)
                else:
                    if self.carried_child:
                        self.carried_child.x, self.carried_child.y = nx, ny
                    self._carry_child(path[idx], env)
                return
        
        if self.carried_child and not match_types(env[nx][ny], availables):
            # trigger clear-block objective
            env_info['blocked-position'] = nx, ny
            self.trigger_clear_block_objective(env, env_info)
        else:
            if self.carried_child:
                self.carried_child.x, self.carried_child.y = nx, ny
            self._move(path[idx], env)

    def check_dirty_alert(self, void_cells, dirty_cells):
        return dirty_cells >= 0.55 * (void_cells + dirty_cells)
    
    def clean(self, env):
        x, y = self.x, self.y
        robot = env[x][y][0]
        env[x][y] = (Void(x, y), robot, Void(x, y))

    def get_closest_objective(self, env, pi, visit, objectives_targets=None):
        robot_pos = self.x, self.y
        rows, cols = len(env), len(env[0])

        closest_path_len = rows * cols
        closest_target_pos = -1, -1
        objectives_targets = objectives_targets or (self.carried_child and \
            ((Void, Playpen, Void), (Void, Dirt, Void)) or ((Void, Child, Void), (Void, Dirt, Void)))

        for x in range(rows):
            for y in range(cols):
                if match_types(env[x][y], objectives_targets) and visit[x][y] != 0 and visit[x][y] < closest_path_len:
                    closest_path_len = visit[x][y]
                    closest_target_pos = x, y
        
        rx, ry = robot_pos
        if isinstance(env[rx][ry][1], Playpen) and self.carried_child or isinstance(env[rx][ry][1], Dirt):
            closest_target_pos = rx, ry
        
        tx, ty = closest_target_pos
        target = env[tx][ty][1]
        objectives_name = isinstance(target, Dirt) and 'clean' or 'bring-children-to-playpen'
        
        return objectives_name, closest_target_pos

    def perform_action(self, env, env_info):
        raise NotImplementedError

class ProactiveAgent(MySmartAgent):
    def __init__(self, x, y, ignored_objectives_limit=20):
        super(ProactiveAgent, self).__init__(x, y)
        self.ignored_objectives = 0
        self.ignored_objectives_limit = ignored_objectives_limit
        self.change_behaviour = False

    def perform_action(self, env, env_info):
        dirty_cells = env_info['dirty-cells']
        void_cells = env_info['void-cells']
        children = env_info['children']
        in_play_pen = env_info['in-play-pen']
        
        active_objective = self.get_active_objective()

        if self.ignored_objectives >= self.ignored_objectives_limit and (not active_objective or not active_objective.on_dirty_cell):
            self.ignored_objectives = 0
            self.change_behaviour = True

        if (not active_objective or active_objective.name != 'clear-block') and self.check_dirty_alert(void_cells, dirty_cells):
            for objective in self.objectives.values():
                objective.is_in_course = False
            
            self.objectives['dirty-alert'].is_in_course = True

        
        robot_pos = self.x, self.y
        obstacles = ((Void, Obstacle, Void),)
        pi, visit = find_paths(env, robot_pos, obstacles)

        if active_objective:
            if active_objective.name not in ['clear-block', 'dirty-alert', 'move-in-playpen']:
                # Search closest objective
                closest_objective_name, closest_target_pos = self.get_closest_objective(env, pi, visit)
                if active_objective.name != closest_objective_name:
                    if not self.change_behaviour:
                        self.ignored_objectives += 1
                    else:
                        active_objective.is_in_course = False
                        active_objective = self.objectives[closest_objective_name]
                        active_objective.is_in_course = True
                        self.change_behaviour = False
            
            active_objective.perform(active_objective, env, self, env_info)
            completed = active_objective.check_if_completed(active_objective, env, self, env_info)

            if completed:
                active_objective.is_in_course = False
                self.ignored_objectives = 0

        else:
            # Search closest objective
            objective_targets = None
            if in_play_pen < len(children):
                objective_targets = self.carried_child and ((Void, Playpen, Void),) or ((Void, Child, Void),)
            else:
                objective_targets = ((Void, Dirt, Void),)

            closest_objective_name, _ = self.get_closest_objective(env, pi, visit, objective_targets)
            active_objective = self.objectives[closest_objective_name]
            active_objective.is_in_course = True
            active_objective.perform(active_objective, env, self, env_info)
            completed = active_objective.check_if_completed(active_objective, env, self, env_info)

            if completed:
                active_objective.is_in_course = False
                self.ignored_objectives = 0

class ReactiveAgent(MySmartAgent):
    def __init__(self, x, y, interrupted_objectives_limit=10):
        super(ReactiveAgent, self).__init__(x, y)
        self.interrupted_objectives = 0
        self.interrupted_objectives_limit = interrupted_objectives_limit
        self.change_behaviour = False
    
    def __name__(self):
        return 'ReactiveAgent'

    def perform_action(self, env, env_info):
        dirty_cells = env_info['dirty-cells']
        void_cells = env_info['void-cells']
        children = env_info['children']

        active_objective = self.get_active_objective()

        if self.interrupted_objectives >= self.interrupted_objectives_limit and (not active_objective or not active_objective.on_dirty_cell):
            self.interrupted_objectives_limit = 0
            self.change_behaviour = True

        if (not active_objective or active_objective.name != 'clear-block') and self.check_dirty_alert(void_cells, dirty_cells):
            for objective in self.objectives.values():
                objective.is_in_course = False
            
            self.objectives['dirty-alert'].is_in_course = True
        
        robot_pos = self.x, self.y
        obstacles = ((Void, Obstacle, Void),)
        pi, visit = find_paths(env, robot_pos, obstacles)

        if active_objective:
            if active_objective.name not in ['clear-block', 'dirty-alert', 'move-in-playpen']:
                # Search closest objective
                closest_objective_name, closest_target_pos = self.get_closest_objective(env, pi, visit)
                if active_objective.name != closest_objective_name:
                    if not self.change_behaviour and not self.carried_child:
                        self.interrupted_objectives += 1
                        active_objective.is_in_course = False
                        active_objective = self.objectives[closest_objective_name]
                        active_objective.is_in_course = True
                    else:
                        self.change_behaviour = False
            
            active_objective.perform(active_objective, env, self, env_info)
            completed = active_objective.check_if_completed(active_objective, env, self, env_info)

            if completed:
                active_objective.is_in_course = False
                self.interrupted_objectives = 0
        else:
            # Search closest objective
            closest_objective_name, _ = self.get_closest_objective(env, pi, visit)
            active_objective = self.objectives[closest_objective_name]
            active_objective.is_in_course = True
            active_objective.perform(active_objective, env, self, env_info)
            completed = active_objective.check_if_completed(active_objective, env, self, env_info)

            if completed:
                active_objective.is_in_course = False
                self.interrupted_objectives = 0