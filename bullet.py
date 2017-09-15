from entity import Bullet
from gameobjects.vector2 import Vector2
import math


class BounceBullet(Bullet):
    cold_down = 500

    def __init__(self, world, parent, position, heading):
        super(BounceBullet, self).__init__(world, 'bounce', parent, position, heading, 52, 'media/bullet-png-39228.png', 10)

    def movement(self, time_passed):
        super(BounceBullet, self).movement(time_passed)
        x, y = self.position
        if x <= self.frame_width / 2:
            self.position.x = self.frame_width / 2
            self.heading *= (-1, 1)
        elif x >= self.world.width - self.frame_width / 2:
            self.position.x = self.world.width - self.frame_width / 2
            self.heading *= (-1, 1)
        if y <= self.frame_height / 2:
            self.heading *= (1, -1)
            self.position.y = self.frame_height / 2
        elif y >= self.world.height - self.frame_height / 2:
            self.heading *= (1, -1)
            self.position.y = self.world.height - self.frame_height / 2


class SpiralsBullet(Bullet):
    cold_down = 500

    def __init__(self, world, parent, position, heading):
        super(SpiralsBullet, self).__init__(world, 'spirals', parent, position, heading, 52, 'media/bullet-png.png', 10)
        self.action_angle = 0
        self.origin_point = position

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
        b = 10
        x = (a + b * c) * math.cos(c)
        y = (a + b * c) * math.sin(c)
        position = Vector2(x, y) + self.origin_point
        self.heading = position - self.position
        self.position = position
