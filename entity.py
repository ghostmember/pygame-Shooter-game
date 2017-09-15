import pygame
from pygame.locals import *
from pygame import sprite
from gameobjects.vector2 import Vector2
import math
import random


class Entity(sprite.Sprite):
    def __init__(self, world, name, position, heading, speed, image, rc, nums=None, angle=0):
        '''
        类的构造函数
        :param world: 所在的世界，都是世界的错，西园寺小姐真是很辛苦呢
        :param name: 创建实例的名称
        :param position: 实例所在的位置
        :param heading: 实例的朝向
        :param speed: 实例的速度 像素/秒
        :param image: 实例的图片路径
        :param rc: 一个元组(m, n)，表示图片是m*n帧的
        :param nums: 一个元组(m, n)，用于缩放；表示实例图像大小相对于世界大小的数量，
        即摆满屏幕横着可以放m列，竖着可以放n行；可为 None，表示不进行缩放
        :param angle: 图像初始旋转的角度
        '''
        # 调用父类的构造函数
        super(Entity, self).__init__()
        self.world = world
        self.name = name
        self.speed = speed
        self.position = Vector2(position)
        self.master_image = self.load(image, rc, nums)  # 加载图片
        self.frame_row = 0  # 帧的行号
        self.frame_col = 0  # 真的列号
        self.row_num = rc[0]  # 每行的帧数
        self.col_num = rc[1]  # 每列的帧数
        w, h = self.master_image.get_size()  # 获取图片的尺寸
        self.frame_width = w / rc[0]  # 计算每帧的宽度
        self.frame_height = h / rc[1]  # 计算每帧的高度
        self.rect = Rect(0, 0, self.frame_width, self.frame_height)  # 显示的区域大小
        self.image = self.master_image.subsurface(self.rect)  # 创建显示的区域大小的图像对象
        self.action_counter = 0  # 用于控制移动时动画帧率的时间间隔统计
        self.heading = Vector2(heading).normalise()  # 朝向，归一化，即向量长度为 1
        self.init_angle = angle

    def load(self, image, rc, nums):
        '''
        加载图
        :param image: 图片路径
        :param rc: 一个元组(m, n)，表示图片是m*n帧的
        :param nums: 太长了，算了
        :return: surface 对象
        '''
        master_image = pygame.image.load(image).convert_alpha()  # 载入图片
        w, h = master_image.get_size()  # 获取图片尺寸
        scale = 1  # 初始化缩放比例为 1
        if nums is not None:  # 判断 nums 是为None
            sx = (self.world.width * rc[0]) / (nums[0] * w)  # 按每行的个数计算缩放比例
            sy = (self.world.height * rc[1]) / (nums[1] * h)  # 按每列的个数计算缩放比例
            # 为了好看，按照原图的长宽比进行缩放，取缩放量小的比例，颜值即是正义
            if abs(sx - 1) > abs(sy - 1):
                scale = sy
            else:
                scale = sx
        # 返回缩放和旋转后的图像
        return pygame.transform.rotozoom(master_image, 0, scale)

    def update(self, time_passed):
        '''
        更新实例的函数
        :param time_passed: 距离上次更新的时间间隔
        :return: None
        '''
        self.load_frame()  # 加载动画帧
        self.movement(time_passed)  # 调用约束函数，计算位置
        try:
            self.rect.center = self.position  # 更新位置
        except Exception as e:
            print(e)
            print(self.position)
            print(self.rect)
            exit()
        # 如果速度为 0，则跳过帧计算
        if self.speed == 0:
            return
        self.action_counter += time_passed  # 更新时间统计
        if self.action_counter > (1 / 10.0):  # 是否到达更新帧号的时间
            self.frame_col = (self.frame_col + 1) % self.col_num
            self.action_counter = 0

    def movement(self, time_passed):
        '''
        用于计算和约束位置的函数，由各个继承的子类自行定义
        :param time_passed: 时间间隔
        :return: None
        '''
        x = self.heading.get_normalised() * self.speed * time_passed  # 计算此段时间内移动位移
        self.position += x
        pass

    def get_heading(self):
        '''
        获取朝向函数
        :return: 当前朝向的角度，角度制
        '''
        return math.atan2(-self.heading.y, self.heading.x) / math.pi * 180

    def set_heading(self, heading):
        '''
        设置当前朝向
        :param heading: 要设置的朝向
        :return: 旋转的角度，角度制
        '''
        self.heading = heading
        angle = self.get_heading() - self.init_angle
        return angle

    def rotate(self, angle):
        '''
        用来旋转图像
        :param angle: 旋转的角度
        :return: None
        '''
        self.image = pygame.transform.rotate(self.image, angle)
        position = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = position

    def load_frame(self):
        '''
        加载当前帧
        :return: surface 对象
        '''
        # 计算当前帧在图片起始位置
        x = self.frame_col * self.frame_width
        y = self.frame_row * self.frame_height
        rect = (x, y, self.frame_width, self.frame_height)
        self.image = self.master_image.subsurface(rect)  # 更新图像为当前帧
        self.rotate(self.init_angle)
        return self.image

    def collide_callback(self, entity):
        '''
        碰撞时的回调函数
        :param entity: 与之发生碰撞的事物
        :return:
        '''
        pass


class Bullet(Entity):
    cold_down = 300

    def __init__(self, world, name, parent, position, heading, speed, image, damage=1, rc=(20, 24), angle=0):
        '''
        子弹类的工作函数
        :param world: 世界
        :param name: 名字
        :param parent: 所属，是谁发出的子弹
        :param position: 位置
        :param heading: 朝向
        :param speed: 移动速度
        :param image: 图像路径
        :param damage: 伤害
        :param cold_down: 冷却时间
        :param rc: 一个元组(m, n)，表示图片是m*n帧的
        :param angle: 图像初始旋转的角度
        '''
        super(Bullet, self).__init__(world, name, position, heading, speed, image, (1, 1), rc, angle)
        self.parent = parent
        self.damage = damage
        self.add(self.world.group('bullets'))

    def update(self, time_passed):
        super(Bullet, self).update(time_passed)
        angle = self.get_heading() - self.init_angle
        self.rotate(angle)


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


class Role(Entity):
    def __init__(self, world, name, position, heading, speed, image, rc, nums=None, hp=100, hp_color=None, angle=0):
        '''
        人物类构造函数
        :param world: 又是世界，西园寺小姐好忙啊
        :param name: 名字
        :param position: 位置
        :param heading: 朝向
        :param speed: 速度
        :param image: 图片路径
        :param rc:
        :param nums:
        :param hp: 血量
        :param hp_color: 血条颜色
        :param angle: 图像旋转的角度
        '''
        super(Role, self).__init__(world, name, position, heading, 0, image, rc, nums, angle)
        self.hp = hp
        self.max_hp = hp
        self.hp_color = hp_color
        self.bullet = {'bounce': [BounceBullet, 0], 'spirals': [SpiralsBullet, 0]}
        self.move_speed = speed
        # self.world.tanks.add(self)

    def move(self, direction):
        v = Vector2()
        if 'l' in direction:
            self.frame_row = 1
            v.x -= 1
        if 'r' in direction:
            self.frame_row = 2
            v.x += 1
        if 'u' in direction:
            self.frame_row = 3
            v.y -= 1
        if 'd' in direction:
            self.frame_row = 0
            v.y += 1
        if v.get_length() == 0:
            self.stop()
            return
        self.heading = v

        self.speed = self.move_speed

    def stop(self):
        self.frame_col = 0
        self.speed = 0

    def fire(self, bullet):
        if bullet not in self.bullet:
            return
        current_time = pygame.time.get_ticks()
        if current_time > self.bullet[bullet][1] + self.bullet[bullet][0].cold_down:
            angle = math.radians(self.get_heading())
            w, h = self.rect.size
            angle2 = math.atan2(h, w)
            angle3 = math.pi - angle2
            if -angle2 <= angle < angle2 or angle > angle3 or angle < -angle3:
                x = w
                y = w / math.cos(angle) * math.sin(angle)
            else:
                x = h / math.sin(angle) * math.cos(angle)
                y = h
            position = self.position + Vector2(x, y).length * self.heading.get_normalised()
            self.bullet[bullet][0](self.world, self, position, self.heading)
            self.bullet[bullet][1] = current_time

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
        return self.hp

    def update(self, time_passed):
        super(Role, self).update(time_passed)
        if self.hp_color is None:
            return
        surface = pygame.Surface((self.rect.width, self.rect.height), flags=SRCALPHA, depth=32)
        self.rect.height *= 1.1
        h = self.rect.height - self.frame_height
        surface.fill((255, 255, 255), (0, 0, self.rect.width, h))
        surface.fill(self.hp_color, (0, 0, int(self.rect.width * self.hp / self.max_hp), h))
        surface.blit(self.image, (0, h))
        self.image = surface

    def movement(self, time_passed):
        super(Role, self).movement(time_passed)
        position = ''
        if self.position.get_x() <= self.frame_width / 2.0:
            self.position.set_x(self.frame_width / 2.0)
            position += 'left'
        elif self.position.get_x() >= self.world.width - self.frame_width / 2:
            self.position.set_x(self.world.width - self.frame_width / 2)
            position += 'right'
        if self.position.get_y() <= self.frame_height / 2:
            self.position.set_y(self.frame_height / 2)
            position += 'up'
        elif self.position.get_y() >= self.world.height - self.frame_height / 2:
            self.position.set_y(self.world.height - self.frame_height / 2)
            position += 'bottom'
        if position == '':
            position = None
        return position


class Player(Role):
    def __init__(self, world):
        super(Player, self).__init__(world, 'player', (400, 300), (0, -1), 50, 'media/hero-1.png', (4, 4), (25, 12.5),
                                     hp_color=(0, 255, 0))
        self.world.add('player', self)
        self.frame_row = 3

    def control(self, pressed_keys):
        if pressed_keys[K_SPACE]:
            self.fire('bounce')

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


class Robot(Role):
    counter = 0

    def __init__(self, world):
        w = world.width
        h = int(world.height * 0.3)
        position = (random.randint(0, w), random.randint(0, h))
        super(Robot, self).__init__(world, 'Robot', position, (0, -1), 50, 'media/hero-0.png',
                                    (4, 4), (25, 12.5), hp_color=(255, 0, 0))
        Robot.counter += 1
        self.move_counter = 0
        self.next_time = 0
        self.add(self.world.group('robot'))

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
            bullet = random.choice(['bounce', 'spirals'])
            self.fire(bullet)

    def hit(self, de):
        if super(Robot, self).hit(de) <= 0:
            self.world.kill_counter += 1

    def fire(self, bullet):
        heading = self.heading
        current_time = pygame.time.get_ticks() / 1000
        angle = current_time * math.pi * 2
        self.heading = Vector2(math.cos(angle), math.sin(angle))
        super(Robot, self).fire(bullet)
        self.heading = heading


class World(object):
    def __init__(self, surface):
        self.surface = surface
        # self.all_sprites = sprite.Group()
        self.groups = {}
        self.width, self.height = self.surface.get_size()
        self.hit_counter = 0
        self.kill_counter = 0

    def add(self, group_name, *sprites):
        if group_name not in self.groups:
            self.groups[group_name] = sprite.Group(*sprites)
        else:
            self.groups[group_name].add(*sprites)

    def remove(self, group_name, *sprites):
        if group_name in self.groups:
            self.groups[group_name].remove(*sprites)

    def group(self, group_name):
        return self.groups.setdefault(group_name, sprite.Group())

    @staticmethod
    def collide(bullet, tank):
        # if bullet.name == tank.name:
        #     return False
        return sprite.collide_rect_ratio(0.5)(bullet, tank)

    def process(self):
        bs = self.groups.setdefault('bullets', sprite.Group())
        if len(bs):
            for name, group in self.groups.items():
                if name == 'bullets':
                    continue
                g = sprite.groupcollide(bs, group, True, False, self.collide)
                for b, p in g.items():
                    p[0].hit(b.damage)
                    if name == 'robot':
                        self.hit_counter += 1

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

    def update(self, time_pass_second):
        for group in self.groups.values():
            group.update(time_pass_second)
            group.draw(self.surface)


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
