import pygame
from pygame.locals import *
from pygame import sprite
from gameobjects.vector2 import Vector2
import math

collide_ratio = 0.7


def rect_edge(heading, size):
    """
    以矩形中心为原点，计算射线于矩形边沿的交点
    :param heading: 射线的方向
    :param size: 矩形的尺寸 (长, 宽)
    :return: 交点
    """
    heading = Vector2(heading)
    if heading.get_length() == 0:
        return heading
    size = Vector2(size) / 2.0
    if size.get_length() == 0:
        return size
    x, y = heading.normalise()
    w, h = size
    x1, y1 = size.get_normalised()
    if abs(x) >= x1:
        if x == 0:
            scale = h / abs(y)
        else:
            scale = w / abs(x)
    else:
        scale = h / abs(y)
    return heading * scale


def not_overlap(rect, over):
    """
    计算非覆盖区域
    :param rect: 整个矩形
    :param over: 覆盖区的高度比例
    :return: 非覆盖区域矩形
    """
    rect = Rect(rect)
    c = rect.center
    rect.w *= collide_ratio
    rect.h *= collide_ratio
    rect.center = c
    x, y, w, h = rect
    if over > 0:
        y += h * over
    h *= (1 - abs(over))
    return Rect(x, y, w, h)


def not_overlap_collide(velocity1, rect1, velocity2, rect2):
    """
    根据运动速度和矩形计算回退的位移
    :param velocity1: 矩形 1 的速度
    :param rect1: 矩形 1
    :param velocity2: 矩形 2 的速度
    :param rect2: 矩形 2
    :return: 两个位移
    """
    v1 = Vector2(velocity1)
    v2 = Vector2(velocity2)
    r1 = Rect(rect1)
    c1 = r1.center
    cr = collide_ratio
    r1.w *= cr
    r1.h *= cr
    r1.center = c1
    r2 = Rect(rect2)
    c2 = r2.center
    r2.w *= cr
    r2.h *= cr
    r2.center = c2
    r = r1.clip(r2)
    size = r.size
    p = Vector2(c1) - c2
    x1 = Vector2()
    x2 = Vector2(1, 1)
    if v1.get_length() > 0:
        delta_x, delta_y = rect_edge(v1, size)
        x, y = p * v1
        if x < 0:
            x1.x = delta_x
        else:
            x2.x = 2
        if y < 0:
            x1.y = delta_y
        else:
            x2.y = 2
    else:
        x2 *= 2
    if v2.get_length() == 0:
        x2 = Vector2()
        x1 *= 2
    else:
        delta_x, delta_y = rect_edge(v2, size)
        x, y = p * v2
        if x > 0:
            x2.x *= delta_x
        else:
            x1.x *= 2
            x2.x = 0
        if y > 0:
            x2.y *= delta_y
        else:
            x1.y *= 2
            x2.y = 0
    return x1, x2


def can_move(v, p, s):
    """
    计算x, y分量方向是否可以移动
    :param v: 速度
    :param p: 两点之间的位移
    :param s: 矩形交集的长宽
    :return: x, y分量上是否可以移动
    """
    if v.get_length() > 0:
        x, y = v * p
        w, h = s
        if w == h:
            r1, r2 = True, True
        elif w > h:
            r1, r2 = True, False
        else:
            r1, r2 = False, True
        return r1 if x > 0 else True, r2 if y > 0 else True
    else:
        return False, False


def collide_can_move_xy(velocity1, rect1, velocity2, rect2):
    """
    计算是否可以在x, y方向移动
    :param velocity1: 矩形1的速度
    :param rect1: 矩形1
    :param velocity2: 矩形2的速度
    :param rect2: 矩形2
    :return: 两矩形在x, y上是否可以移动；True: 可移动，False: 不可移动
    """
    v1 = Vector2(velocity1)
    v2 = Vector2(velocity2)
    r1 = Rect(rect1)
    c1 = r1.center
    cr = collide_ratio
    r2 = Rect(rect2)
    c2 = r2.center
    r = r1.clip(r2)
    s = r.size
    p = Vector2(c1) - c2
    a = can_move(v1, -p, s)
    b = can_move(v2, p, s)
    return a, b


class Entity(sprite.Sprite):
    def __init__(self, world, name, group, position, heading, speed, image, rc=(1, 1), nums=None, angle=0,
                 overlap=(0, False)):
        """
        类的构造函数
        :param world: 所在的世界，都是世界的错，西园寺小姐真是很辛苦呢
        :param name: 创建实例的名称
        :param group: 创建实例的所属的组别
        :param position: 实例所在的位置
        :param heading: 实例的朝向
        :param speed: 实例的速度 像素/秒
        :param image: 实例的图片路径或图像对象，或者透明图像的尺寸
        :param rc: 一个元组(m, n)，表示图片是m*n帧的
        :param nums: 一个元组(m, n)，用于缩放；表示实例图像大小相对于世界大小的数量，
        即摆满屏幕横着可以放m列，竖着可以放n行；可为 None，表示不进行缩放
        :param angle: 图像初始旋转的角度
        :param overlap: 图像覆盖区域参数，用于碰撞检测和绘画时排序，第一个参数表示高度比例，正值表示从顶部开始计算，负值表示从底部开始计算
        第二个参数，True: 置于底部，被覆盖；False: 至顶部，覆盖其他图像
        """
        # 调用父类的构造函数
        super(Entity, self).__init__()
        self.world = world
        self.name = name
        self.group = self.add_groups(group)
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
        self.heading = Vector2(heading)  # 朝向
        self.init_angle = angle
        self.overlap = overlap
        self.collide_entity = {}

    def add_groups(self, group):
        """
        将实例添加到world中对用的精灵组中
        :param group: 精灵组
        :return:
        """
        if group is None:
            group = ('__anonymous__',)
        elif isinstance(group, (tuple, list, dict)):
            pass
        else:
            group = (group,)
        for g in group:
            self.world.add(g, self)
        return group

    def load(self, image, rc, nums):
        """
        加载图像
        :param image: 图片路径或surface对象或图像尺寸
        :param rc: 一个元组(m, n)，表示图片是m*n帧的
        :param nums: 太长了，算了
        :return: surface 对象
        """
        if isinstance(image, str):
            master_image = pygame.image.load(image).convert_alpha()  # 载入图片
        elif isinstance(image, pygame.Surface):
            master_image = image
        elif isinstance(image, (tuple, list)):
            master_image = pygame.Surface(image, flags=SRCALPHA, depth=32)
        else:
            master_image = pygame.Surface((1, 1), flags=SRCALPHA, depth=32)
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
        """
        更新实例的函数
        :param time_passed: 距离上次更新的时间间隔
        :return: None
        """
        self.movement(time_passed)  # 调用约束函数，计算位置
        self.load_frame()  # 加载动画帧
        self.rect.center = self.position  # 更新位置
        # 如果速度为 0，则跳过帧计算
        if self.speed != 0:
            self.action_counter += time_passed  # 更新时间统计
            if self.action_counter > (1 / 10.0):  # 是否到达更新帧号的时间
                self.frame_col = (self.frame_col + 1) % self.col_num
                self.action_counter = 0

    def movement(self, time_passed):
        """
        用于计算和约束位置的函数，由各个继承的子类自行定义
        :param time_passed: 时间间隔
        :return: None
        """
        if self.speed != 0 and self.heading.get_length() > 0:
            x = self.heading.get_normalised() * self.speed * time_passed  # 计算此段时间内移动位移
            self.position += x
        self.collide_process(time_passed)  # 处理之前的碰撞造成的位置影响
        self.collide_entity.clear()  # 清除与之发生碰撞的物体

    def get_heading(self):
        """
        获取朝向函数
        :return: 当前朝向的角度，角度制
        """
        return math.atan2(-self.heading.y, self.heading.x) / math.pi * 180

    def set_heading(self, heading):
        """
        设置当前朝向
        :param heading: 要设置的朝向
        :return: 旋转的角度，角度制
        """
        self.heading = heading
        angle = self.get_heading() - self.init_angle
        return angle

    def rotate(self, angle):
        """
        用来旋转图像
        :param angle: 旋转的角度
        :return: None
        """
        self.image = pygame.transform.rotate(self.image, angle)
        position = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = position

    def load_frame(self):
        """
        加载当前帧
        :return: surface 对象
        """
        # 计算当前帧在图片起始位置
        x = self.frame_col * self.frame_width
        y = self.frame_row * self.frame_height
        rect = (x, y, self.frame_width, self.frame_height)
        self.image = self.master_image.subsurface(rect)  # 更新图像为当前帧
        self.rotate(self.init_angle)
        return self.image

    def collide_callback(self, group_name, entity):
        """
        碰撞时的回调函数
        :param group_name: 与之发生碰撞的事物所属的组名
        :param entity: 与之发生碰撞的事物
        :return:
        """
        self.collide_entity.setdefault(group_name, dict())[entity] = None

    def collide_process(self, time_passed):
        """
        处理之前的碰撞造成的位置影响
        :param time_passed: 时间间隔
        :return:
        """
        velocity = self.speed * self.heading
        if velocity.get_length() > 0:
            rect1 = not_overlap(self.rect, self.overlap[0])
            x, y = self.rect.center
            for sprites in self.collide_entity.values():
                for sp, cm in sprites.items():
                    if cm is None:
                        rect2 = not_overlap(sp.rect, sp.overlap[0])
                        cm, x2 = collide_can_move_xy(velocity, rect1, sp.heading * sp.speed, rect2)
                        sp.set_collide_entity_position(self.group, self, x2)
                    if not cm[0]:
                        self.position.x = x
                    if not cm[1]:
                        self.position.y = y

    def set_collide_entity_position(self, group, entity, position):
        """
        设置对发生碰撞的事物位置的影响
        :param group: 精灵组名
        :param entity: 影响的实例
        :param position: 对位置的影响
        :return: None
        """
        if not isinstance(group, (tuple, list, dict)):
            return
        for g in group:
            if g in self.collide_entity:
                self.collide_entity[g][entity] = position

    def set_position(self, position):
        """
        设置位置信息
        :param position: 位置
        :return: None
        """
        self.position = position


class Bullet(Entity):
    cold_down = 300

    def __init__(self, world, name, parent, position, heading, speed, image, damage=1, rc=(20, 24), angle=0):
        """
        子弹类的工作函数
        :param world: 世界
        :param name: 名字
        :param parent: 所属，是谁发出的子弹
        :param position: 位置
        :param heading: 朝向
        :param speed: 移动速度
        :param image: 图像路径
        :param damage: 伤害
        :param rc: 一个元组(m, n)，表示图片是m*n帧的
        :param angle: 图像初始旋转的角度
        """
        super(Bullet, self).__init__(world, name, 'bullets', position, heading, speed, image, (1, 1), rc, angle)
        self.parent = parent
        self.damage = damage
        self.adjust_angle()
        self.adjust_position()

    def update(self, time_passed):
        super(Bullet, self).update(time_passed)
        self.adjust_angle()

    def collide_callback(self, group_name, entity):
        if group_name == 'bullets':
            return
        self.kill()

    def adjust_angle(self):
        angle = self.get_heading() - self.init_angle
        self.rotate(angle)

    def get_damage(self, entity):
        """
        获取对实例产生的伤害
        :param entity: 受到伤害的实例
        :return: 伤害值
        """
        return self.damage

    def adjust_position(self):
        """
        计算子弹生成的位置
        :return: 无
        """
        self.position += rect_edge(self.heading, self.rect.size)
        self.position += rect_edge(self.heading, self.parent.rect.size)
        self.rect.center = self.position


class Role(Entity):
    def __init__(self, world, name, group, position, heading, speed, image, rc=(4, 4), nums=None, hp=100, hp_color=None,
                 angle=0, overlap=(0.8, False)):
        """
        人物类构造函数
        :param world: 又是世界，西园寺小姐好忙啊
        :param name: 名字
        :param group: 组别
        :param position: 位置
        :param heading: 朝向
        :param speed: 速度
        :param image: 图片路径
        :param rc:
        :param nums:
        :param hp: 血量
        :param hp_color: 血条颜色
        :param angle: 图像旋转的角度
        :param overlap: 覆盖区域
        """
        super(Role, self).__init__(world, name, group, position, heading, 0, image, rc, nums, angle, overlap)
        self.hp = hp
        self.max_hp = hp
        self.hp_color = hp_color
        self.bullet = {}
        self.move_speed = speed

    def move(self, direction):
        """
        移动，设置朝向
        :param direction: 方向
        :return:
        """
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
        """
        停止移动
        :return:
        """
        self.frame_col = 0
        self.speed = 0

    def fire(self, bullet, heading=None):
        """
        开火
        :param bullet: 子弹类型
        :param heading: 子弹发射的方向
        :return:
        """
        if bullet not in self.bullet:
            return
        current_time = pygame.time.get_ticks()
        if self.bullet[bullet]['num'] == 0:
            return
        if current_time > self.bullet[bullet]['last_time'] + self.bullet[bullet]['cd_time']:
            if heading is None:
                heading = self.heading
            self.bullet[bullet]['bullet'](self.world, self, self.position, heading)
            self.bullet[bullet]['last_time'] = current_time
            self.bullet[bullet]['num'] -= 1

    def hit(self, damage):
        """
        被击中后的计算
        :param damage: 受到的伤害
        :return: 血量
        """
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
        self.rect.center = self.position

    def collide_callback(self, group_name, entity):
        if group_name == 'bullets':
            self.hit(entity.get_damage(self))
        else:
            super(Role, self).collide_callback(group_name, entity)

    def add_bullet(self, name, bullet, num=-1):
        """
        添加子弹
        :param name: 子弹的名字
        :param bullet: 子弹的类
        :param num: 子弹的数量，如果小于 0 表示无限，为 0 时，表示清除无限状态，将数量设为 0
        :return: None
        """
        self.bullet.setdefault(name, dict())['bullet'] = bullet
        n = self.bullet.setdefault(name, dict()).setdefault('num', 0)
        if num < 1:
            self.bullet[name]['num'] = num
        else:
            n += num
            self.bullet[name]['num'] = n
        self.bullet[name]['last_time'] = 0
        self.bullet[name]['cd_time'] = bullet.cold_down

    def remove_bullet(self, name):
        """
        移除子弹
        :param name: 子弹类型名称
        :return:
        """
        if name in self.bullet:
            self.bullet.pop(name)


class Obstacle(Entity):
    def __init__(self, world, name, position, image, group='obstacle', rc=(1, 1),
                 num=None, angle=0, overlap=(0, False)):
        super(Obstacle, self).__init__(world, name, group, position, (0, 0), 0, image, rc, num, angle, overlap)


class ListGroup(sprite.Group):
    def __init__(self, *sprites):
        super(ListGroup, self).__init__(*sprites)
        self.sort = None

    def sprites(self):
        """
        重写此方法，会返回一个进行排序后的列表
        :return: 精灵列表
        """
        sprites = list(self.spritedict)
        if callable(self.sort):
            sprites.sort(key=self.sort)
        return sprites


class WorldBase(object):
    def __init__(self, surface):
        """
        世界基类的构造函数
        :param surface: 窗口图像对象
        """
        self.surface = surface
        self.all_sprite = ListGroup()
        self.all_sprite.sort = self.sort
        self.groups = {}
        self.width, self.height = self.surface.get_size()

    def add(self, group_name, *sprites):
        """
        向精灵组中添加精灵
        :param group_name: 组名
        :param sprites: 精灵
        :return:
        """
        self.all_sprite.add(*sprites)
        self.groups.setdefault(group_name, sprite.Group()).add(*sprites)

    def remove(self, group_name, *sprites):
        """
        从精灵组中移除精灵
        :param group_name: 组名
        :param sprites: 精灵
        :return:
        """
        self.all_sprite.remove(*sprites)
        if group_name in self.groups:
            self.groups[group_name].remove(*sprites)

    def group(self, group_name=None):
        """
        返回指定的精灵组
        :param group_name: 组名，None: 返回 all_sprite
        :return: 精灵组
        """
        if group_name is None:
            return self.all_sprite
        return self.groups.setdefault(group_name, sprite.Group())

    def get_groups(self):
        """
        获取所有精灵组
        :return: 所有精灵组
        """
        return self.groups.items()

    @staticmethod
    def collide(a, b):
        """
        碰撞计算
        :param a: 精灵a
        :param b: 精灵b
        :return: 是否发生碰撞
        """
        if a == b:
            return False
        return sprite.collide_rect_ratio(collide_ratio)(a, b)

    @staticmethod
    def sort(sp):
        """
        排序
        :param sp: 精灵
        :return: 序列值
        """
        over, lap = sp.overlap
        if over > 1:
            over = 1
        elif over < -1:
            over = -1
        x, y = sp.rect.center
        w, h = sp.rect.size
        y += h * over - h / 2
        if lap:
            y = -y
        return y

    def process(self):
        """
        处理函数，进行精灵碰撞等计算
        :return:
        """
        groups = list(self.groups.items())
        for group in groups:
            name1, group1 = group
            for name2, group2 in groups:
                g = sprite.groupcollide(group1, group2, False, False, self.collide)
                for a, bs in g.items():
                    for b in bs:
                        a.collide_callback(name2, b)
                        b.collide_callback(name1, a)
            groups.remove(group)
        return None

    def update(self, time_pass_second):
        """
        更新，精灵信息并绘画
        :param time_pass_second: 距离上次更新的时间间隔
        :return:
        """
        self.all_sprite.update(time_pass_second)
        self.all_sprite.draw(self.surface)
