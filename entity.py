import pygame
from pygame.locals import *
from pygame.sprite import Sprite
from gameobjects.vector2 import Vector2
from gameobjects.color import Color
import math


class Entity(Sprite):
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
        :param angle: 图像旋转的角度
        '''
        # 调用父类的构造函数
        super(Entity, self).__init__()
        self.world = world
        self.name = name
        self.speed = speed
        self.position = Vector2(position)
        self.master_image = self.load(image, rc, nums, angle)  # 加载图片
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

    def load(self, image, rc, nums, angle):
        '''
        加载图
        :param image: 图片路径
        :param rc: 一个元组(m, n)，表示图片是m*n帧的
        :param nums: 太长了，算了
        :param angle: 旋转角度
        :return: surface 对象
        '''
        master_image = pygame.image.load(image).convert_alpha() # 载入图片
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
        return pygame.transform.rotozoom(master_image, angle, scale)

    def update(self, time_passed):
        '''
        更新实例的函数
        :param time_passed: 距离上次更新的时间间隔
        :return: None
        '''
        x = self.heading.get_normalised() * self.speed * time_passed  # 计算此段时间内移动位移
        self.confines(x)  # 调用约束函数，计算位置
        self.rect.center = self.position  # 更新位置
        # 计算当前帧在图片起始位置
        x = self.frame_col * self.frame_width
        y = self.frame_row * self.frame_height
        rect = (x, y, self.frame_width, self.frame_height)
        self.image = self.master_image.subsurface(rect)  # 更新图像为当前帧

        # 如果速度为 0，则跳过帧计算
        if self.speed == 0:
            return
        self.action_counter += time_passed  # 更新时间统计
        if self.action_counter > (1 / 10.0):  # 是否到达更新帧号的时间
            self.frame_col = (self.frame_col + 1) % self.col_num
            self.action_counter = 0

    def confines(self, x):
        '''
        用于计算和约束位置的函数，由各个子类自行定义
        :param x: 位移
        :return: None
        '''
        pass

    def get_heading(self):
        '''
        获取朝向函数
        :return: 当前朝向的角度，弧度制
        '''
        # self.heading.normalise()
        return math.atan2(-self.heading.y, self.heading.x)

    def set_heading(self, heading):
        '''
        设置当前朝向
        :param heading: 要设置的朝向
        :return: 旋转的角度，弧度制
        '''
        # heading.normalised()
        angle = math.atan2(-heading.y, heading.x) - self.get_heading()
        self.heading = heading
        return angle
