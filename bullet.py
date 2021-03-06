from entity import Bullet
from gameobjects.vector2 import Vector2
import math


class BounceBullet(Bullet):
    cold_down = 500

    def __init__(self, world, parent, position, heading):
        super(BounceBullet, self).__init__(world, 'bounce', parent, position, heading,
                                           52, 'media/bullet-png-39228.png', 10)

    def collide_callback(self, group_name, entity):
        if group_name == 'edge':
            edge = entity.name
            x, y = self.heading
            if (edge == 'left' and x < 0) or (edge == 'right' and x > 0):
                self.heading *= (-1, 1)
            if (edge == 'top' and y < 0) or (edge == 'bottom' and y > 0):
                self.heading *= (1, -1)
            return
        super(BounceBullet, self).collide_callback(group_name, entity)


class SpiralsBullet(Bullet):
    cold_down = 500

    def __init__(self, world, parent, position, heading):
        super(SpiralsBullet, self).__init__(world, 'spirals', parent, position, heading, 52, 'media/spirals.png', 10)
        self.action_angle = math.pi * 0.3
        self.origin_point = Vector2(position)

    def movement(self, time_passed):
        r = self.position.get_distance_to(self.origin_point)
        if r > max(self.world.width, self.world.height):
            self.kill()
        coe = 1
        if r > 50:
            coe = self.speed / r
        self.action_angle += math.pi * time_passed * coe
        c = self.action_angle
        a = 0
        b = 20
        x = (a + b * c) * math.cos(c)
        y = (a + b * c) * math.sin(c)
        position = Vector2(x, y) + self.origin_point
        self.heading = position - self.position
        self.position = position
        
    def set_position(self, position):
        self.origin_point = position
        super(SpiralsBullet, self).set_position(position)
    
    def get_damage(self, entity):
        if self.parent == entity:
            if self.position.get_distance_to(self.origin_point) < 100:
                return 0
        return super(SpiralsBullet, self).get_damage(entity)

    def collide_callback(self, group_name, entity):
        if entity == self.parent:
            if self.position.get_distance_to(self.origin_point) < 100:
                return
        if group_name == 'edge':
            return
        super(SpiralsBullet, self).collide_callback(group_name, entity)

    def adjust_position(self):
        pass
