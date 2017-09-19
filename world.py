from pygame import sprite
from entity import WorldBase
from role import Robot
from map import Edge


class World(WorldBase):
    def __init__(self, surface):
        super(World, self).__init__(surface)
        self.hit_counter = 0
        self.kill_counter = 0
        self.edge = Edge(self)

    def process(self):
        super(World, self).process()

        bs = self.groups.setdefault('robot', sprite.Group())
        if len(bs) < 5:
            if Robot.counter < 100:
                Robot(self)
            if len(bs) == 0:
                return 'win'

        bs = self.groups.setdefault('player', sprite.Group())
        if len(bs) == 0:
            return 'over'

        return None
