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

class Void(EnvironmentElement):
    pass

class Obstacle(EnvironmentElement):
    pass

class Dirt(EnvironmentElement):
    pass

class Playpen(EnvironmentElement):
    pass

class Child(EnvironmentElement):
    pass