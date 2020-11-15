class Direction:

    @staticmethod
    def north():
        return 1, 0
    
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

class EnvironmentElement:

    def __init__(self, x, y, environment):
        self.x = x
        self.y = y
        self.environment = environment
    
    def __repr__(self):
        return str(self)

class Void(EnvironmentElement):
    def __str__(self):
        return '     '

class Obstacle(EnvironmentElement):
    def __str__(self):
        return '  O  '

class Dirt(EnvironmentElement):
    def __str__(self):
        return '  D  '

class Playpen(EnvironmentElement):
    def __str__(self):
        return '  P  '

class Child(EnvironmentElement):
    def __str__(self):
        return self.num < 10 and f' C0{self.num} ' or f' C{self.num} '