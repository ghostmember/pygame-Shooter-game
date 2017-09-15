from pygame import sprite
from entity import WorldBase
from role import Robot


class World(WorldBase):
    def __init__(self, surface):
        super(World, self).__init__(surface)

    @staticmethod
    def collide(bullet, tank):
        # if bullet.name == tank.name:
        #     return False
        return sprite.collide_rect_ratio(0.5)(bullet, tank)

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
