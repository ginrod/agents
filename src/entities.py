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

class Child(EnvironmentElement):
    pass

class Playpen(EnvironmentElement):
    pass