from entity import Obstacle, collide_ratio


class Edge(object):
    def __init__(self, world, size=None, extend=10, ratio=collide_ratio):
        if size is None:
            size = world.width, world.height
        self.size = size
        self.extend = extend
        w, h = size
        x, y = w / 2, h / 2
        w1, h1 = w / ratio, h / ratio
        p = -extend / 2
        extend /= ratio
        self.top = Obstacle(world, 'top', (x, p), (w1, extend), 'edge')
        self.top.image.fill((0, 0, 0))
        self.bottom = Obstacle(world, 'bottom', (x, h - p), (w1, extend), 'edge')
        self.left = Obstacle(world, 'left', (p, y), (extend, h1), 'edge')
        self.right = Obstacle(world, 'top', (w - p, y), (extend, h1), 'edge')
