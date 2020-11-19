class EnvironmentElement:

    def __init__(self, x, y, environment):
        self.x = x
        self.y = y
        self.environment = environment
    
    def __repr__(self):
        return str(self)

class Void(EnvironmentElement):
    def __str__(self):
        return '   '

class Obstacle(EnvironmentElement):
    def __str__(self):
        return ' O '

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
        pass