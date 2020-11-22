import random

class Direction:

    @staticmethod
    def north():
        return -1, 0
    
    @staticmethod
    def north_east():
        return -1, 1
    
    @staticmethod
    def east():
        return 0, 1
    
    @staticmethod
    def south_east():
        return 1, 1
    
    @staticmethod
    def south():
        return 1, 0
    
    @staticmethod
    def south_west():
        return 1, -1
    
    @staticmethod
    def west():
        return 0, -1
    
    @staticmethod
    def north_west():
        return -1, -1

directions = [Direction.north(), Direction.north_east(), Direction.east(), Direction.south_east(), 
              Direction.south(), Direction.south_west(), Direction.west(), Direction.north_west()]

def inside(env, x, y):
    rows, cols = len(env), len(env[0])
    return 0 <= x < rows and 0 <= y < cols

class EnvironmentElement:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def clone(self):
        return EnvironmentElement(self.x, self.y)

    def _move(self, new_pos, env):
        nx, ny = new_pos
        # Move to new_pos position
        x, y = self.x, self.y
        env[x][y] = Void(x, y), Void(x, y), Void(x, y)
        self.x, self.y = nx, ny

        if isinstance(env[nx][ny][1], Void):
            env[nx][ny] = Void(nx, ny), self, Void(nx, ny)
        else:
            env[nx][ny] = self, env[nx][ny][1], env[nx][ny][2]

    def __repr__(self):
        return str(self)

class Agent(EnvironmentElement):
    def __str__(self):
        return ' R '

class Void(EnvironmentElement):
    def __str__(self):
        return '   '
    
    def clone(self):
        return Void(self.x, self.y)

class Obstacle(EnvironmentElement):
    def __str__(self):
        return ' O '
    
    def clone(self):
        return Obstacle(self.x, self.y)

    def push(self, direction, env):
        dx, dy = direction
        nx, ny = self.x + dx, self.y + dy

        for x in range(len(env)):
            for y in range(len(env[0])):
                if env[x][y][1] == self:
                    foo = 0

        if not inside(env, nx, ny): return
        
        if isinstance(env[nx][ny][1], Void):
            self._move((nx, ny), env)
        elif isinstance(env[nx][ny][1], Obstacle):
            # Try pushing the obstacle
            env[nx][ny][1].push((dx, dy), env)

            # If new pos is now Void the push could be performed
            if isinstance(env[nx][ny][1], Void):
                self._move((nx, ny), env)

class Dirt(EnvironmentElement):
    def __str__(self):
        return ' D '
    
    def clone(self):
        return Dirt(self.x, self.y)

class Playpen(EnvironmentElement):
    def __str__(self):
        return ' P '
    
    def clone(self):
        return Playpen(self.x, self.y)

class Child(EnvironmentElement):
    def __init__(self, x, y, num=None):
        super(Child, self).__init__(x, y)
        self.num = num
    
    def clone(self):
        return Child(self.x, self.y, self.num)

    def __str__(self):
        return self.num < 10 and f'C0{self.num}' or f'C{self.num}'

    def react(self, env):
        inside_directions = [(dx,dy) for dx,dy in directions if inside(env, self.x + dx, self.y + dy)]
        idx = random.randint(0, len(inside_directions))
        # Simulating a do nothing with the same probability of move randomly inside env
        if idx == len(inside_directions): return

        dx, dy = inside_directions[idx]
        nx, ny = self.x + dx, self.y + dy

        if isinstance(env[nx][ny][1], Void):
            self._move((nx, ny), env)
        elif isinstance(env[nx][ny][1], Obstacle):
            # Try pushing the obstacle
            env[nx][ny][1].push((dx, dy), env)
            
            # If new pos is now Void the push could be performed
            if isinstance(env[nx][ny][1], Void):
                self._move((nx, ny), env)
    
    def get_3x3_grids_containing_child(self, env):
        x, y = self.x, self.y
        result = set() # left corner of the 3x3 grid

        # If child is carried by the robot or in the playpen return no grids 
        if isinstance(env[x][y][0], Agent) or isinstance(env[x][y][1], Playpen):
            return result

        # Checking that the coords can be a left corner of a 3x3 grid
        if inside(env, x + 2, y + 2):
            result.add((x, y))

        left_most_directions = [Direction.west(), Direction.north_west(), Direction.north()]
        for dx1, dy1 in left_most_directions:
            nx, ny = x + dx1, y + dy1
            if inside(env, nx, ny) and inside(env, nx + 2, ny + 2):
                result.add((nx, ny))
            
            for dx2, dy2 in left_most_directions:
                nx, ny = x + dx1 + dx2, y + dy1 + dy2
                if inside(env, nx, ny) and inside(env, nx + 2, ny + 2):
                    result.add((nx, ny))
        
        return result