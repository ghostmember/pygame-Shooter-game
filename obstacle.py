from entity import Obstacle
import pygame
from pygame.locals import *
import math


class TileObstacle(Obstacle):
    def __init__(self, world, name, position, image, size, group='obstacle', rc=(1, 1),
                 num=None, angle=0, overlap=(0, False)):
        self.size = size
        super(TileObstacle, self).__init__(world, name, position, image, group, rc, num, angle, overlap)

    def load(self, image, rc, nums):
        image = super(TileObstacle, self).load(image, rc, nums)
        master_image = pygame.Surface(self.size, flags=SRCALPHA, depth=32)
        w, h = image.get_rect().size
        ww, hh = self.size
        x = int(math.ceil(ww / w))
        y = int(math.ceil(hh / h))

        for i in range(x):
            for j in range(y):
                master_image.blit(image, ((i * w), (y * h)))

        return master_image
