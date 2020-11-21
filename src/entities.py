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

    def __init__(self, x, y, env):
        self.x = x
        self.y = y
        self.env = env
    
    def _move(self, new_pos):
        nx, ny = new_pos
        # Move to new_pos position
        x, y, env = self.x, self.y, self.env
        self.env[self.x][self.y] = (Void(x, y, env), Void(x, y, env), Void(x, y, env))
        self.x, self.y = nx, ny

        if isinstance(env[nx][ny][1], Void):
            self.env[nx][ny] = (Void(nx, ny, env), self, Void(nx, ny, env))
        else:
            self.env[nx][ny] = (self, env[nx][ny][1], env[nx][ny][2])

    def __repr__(self):
        return str(self)

class Void(EnvironmentElement):
    def __str__(self):
        return '   '

class Obstacle(EnvironmentElement):
    def __str__(self):
        return ' O '

    def push(self, direction):
        dx, dy = direction
        nx, ny = self.x + dx, self.y + dy

        if not inside(self.env, nx, ny): return
        
        if isinstance(self.env[nx][ny][1], Void):
            self._move((nx, ny))
        elif isinstance(self.env[nx][ny][1], Obstacle):
            # Try pushing the obstacle
            self.env[nx][ny][1].push((dx, dy))

            # If new pos is now Void the push could be performed
            if isinstance(self.env[nx][ny][1], Void):
                self._move((nx, ny))

class Dirt(EnvironmentElement):
    def __str__(self):
        return ' D '

class Playpen(EnvironmentElement):
    def __str__(self):
        return ' P '

class Child(EnvironmentElement):
    def __str__(self):
        return self.num < 10 and f'C0{self.num}' or f'C{self.num}'

    def react(self):
        inside_directions = [(dx,dy) for dx,dy in directions if inside(self.env, self.x + dx, self.y + dy)]
        idx = random.randint(0, len(inside_directions))
        # Simulating a do nothing with the same probability of move randomly inside env
        if idx == len(inside_directions): return

        dx, dy = inside_directions[idx]
        nx, ny = self.x + dx, self.y + dy

        if isinstance(self.env[nx][ny][1], Void):
            self._move((nx, ny))
        elif isinstance(self.env[nx][ny][1], Obstacle):
            # Try pushing the obstacle
            self.env[nx][ny][1].push((dx, dy))
            
            # If new pos is now Void the push could be performed
            if isinstance(self.env[nx][ny][1], Void):
                self._move((nx, ny))