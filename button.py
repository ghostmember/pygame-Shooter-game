import pygame
from pygame.locals import *
from pygame.sprite import *


class Button(Sprite):
    def __init__(self, image_surface, position, size=None, name=None, call_back=None, args=None):
        super(Button, self).__init__()
        self.name = name
        self.call_back = call_back
        self.args = args
        self.image = image_surface
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.position = position
        if size is not None:
            w, h = size
            self.image = pygame.transform.scale(self.image, (int(w), int(h)))
        self.w, self.h = self.image.get_size()

    def render(self, surface):
        x, y = self.position
        x -= self.w / 2
        y -= self.h / 2
        surface.blit(self.image, (x, y))

    def is_over(self, pos):
        px, py = pos
        x, y = self.position
        x -= self.w / 2
        y -= self.h / 2

        in_x = x <= px <= x + self.w
        in_y = y <= py <= y + self.h
        if in_x and in_y:
            if self.call_back is not None:
                if self.args is None:
                    self.call_back(self)
                else:
                    self.call_back((self, self.args))
            return True
        else:
            return False


class TextButton(Button):
    def __init__(self, text, position, size=None, font=None, color=(0, 0, 0), bg=None, name=None, call_back=None, args=None):
        self.text = text
        self.image = None
        fs = font
        if font is None:
            fs = pygame.font.Font('font/simfang.ttf', 25)
        elif isinstance(font, (float, int)):
            fs = pygame.font.Font('font/simfang.ttf', font)
        elif isinstance(font, str):
            fs = pygame.font.Font(font, 25)
        elif isinstance(font, tuple):
            fs = pygame.font.Font(font[0], font[1])
        if isinstance(bg, str):
            self.image = pygame.image.load(bg).convert_alpha()
        else:
            if size is None:
                sz = fs.render(text, True, color).get_size()
            else:
                sz = size
            self.image = pygame.Surface(sz, flags=SRCALPHA, depth=32)

        super(TextButton, self).__init__(self.image, position, size, name, call_back, args)
        if isinstance(bg, (tuple, list)):
            self.image.fill(bg)
        iw, ih = self.image.get_size()
        t = fs.render(text, True, color)
        tw, th = t.get_size()
        x = (iw - tw) / 2
        y = (ih - th) / 2
        self.image.blit(t, (x, y))


class ButtonGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super(ButtonGroup, self).__init__(*sprites)

    def clicked(self, pos):
        cl = []
        for x in self:
            if x.is_over(pos):
                cl.append(x)
        return cl


if __name__ == '__main__':
    print(isinstance('ss', str))
