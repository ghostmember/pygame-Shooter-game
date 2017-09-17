import pygame
from pygame.locals import *
from entity import Role
import random
from bullet import *


class Robot(Role):
    counter = 0

    def __init__(self, world):
        w = world.width
        h = int(world.height * 0.3)
        position = (random.randint(0, w), random.randint(0, h))
        super(Robot, self).__init__(world, 'Robot', 'robot', position, (0, -1), 50, 'media/hero-0.png',
                                    (4, 4), (25, 12.5), hp_color=(255, 0, 0))
        Robot.counter += 1
        self.move_counter = 0
        self.next_time = 0
        self.add_bullet('bounce', BounceBullet)
        self.add_bullet('spirals', SpiralsBullet)

    def update(self, time_passed):
        self.move_counter += 1
        if self.move_counter > (self.next_time / time_passed):
            self.next_time = 5 * random.random()
            self.move_counter = 0
            move = random.choice('udlr')
            if move == 's':
                self.stop()
            else:
                self.move(move)
        super(Robot, self).update(time_passed)
        if random.random() < 0.03:
            bullet = random.choice(list(self.bullet.keys()))
            self.fire(bullet)

    def hit(self, de):
        if super(Robot, self).hit(de) <= 0:
            self.world.kill_counter += 1

    def fire(self, bullet, heading=None):
        current_time = pygame.time.get_ticks() / 1000
        angle = current_time * math.pi * 2
        heading = Vector2(math.cos(angle), math.sin(angle))
        super(Robot, self).fire(bullet, heading)


class Player(Role):
    def __init__(self, world):
        super(Player, self).__init__(world, 'player', 'player', (400, 300), (0, -1), 50, 'media/hero-1.png',
                                     (4, 4), (25, 12.5), hp_color=(0, 255, 0))
        self.frame_row = 3
        self.add_bullet('bounce', BounceBullet)
        self.add_bullet('spirals', SpiralsBullet)

    def control(self, pressed_keys):
        if pressed_keys[K_SPACE]:
            self.fire('spirals')

        if pressed_keys[K_LEFT] or pressed_keys[K_RIGHT] or pressed_keys[K_UP] or pressed_keys[K_DOWN]:
            direction = ''
            if pressed_keys[K_LEFT]:
                direction += 'l'
            if pressed_keys[K_RIGHT]:
                direction += 'r'
            if pressed_keys[K_UP]:
                direction += 'u'
            if pressed_keys[K_DOWN]:
                direction += 'd'
            if direction != '':
                self.move(direction)
        else:
            self.stop()
