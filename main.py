from button import *
from gameobjects.color import Color
from role import Player
from world import World

ss = (800, 600)


def end_interface(jg, hit_counter, kill_counter):
    font = pygame.font.Font('font/simfang.ttf', 50)
    jz = font.render(u"击中：" + str(hit_counter), True, (255, 0, 0))
    js = font.render(u"击杀：" + str(kill_counter), True, (255, 0, 0))
    jz_x = (ss[0] - jz.get_width()) / 2
    jz_y = ss[1] / 4 - jz.get_height() / 2
    js_x = jz_x
    js_y = jz_y + jz.get_height()

    b1x = ss[0] / 4
    b2x = ss[0] * 3 / 4
    bw = ss[0] * 3 / 8
    bh = 80
    by = js_y + js.get_height() * 5
    bg = ButtonGroup()
    bg.add(TextButton('重新开始', (b1x, by), (bw, bh), font, Color.from_palette('black').rgba8,
                      Color.from_palette('green').rgba8, call_back=run))
    bg.add(TextButton('退出', (b2x, by), (bw, bh), font, Color.from_palette('black').rgba8,
                      Color.from_palette('green').rgba8, call_back=exit))

    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                exit()
            if e.type == MOUSEBUTTONDOWN:
                if len(bg.clicked(e.pos)) > 0:
                    return
        clock.tick(5)
        sc.fill((0, 0, 0))
        sc.blit(jz, (jz_x, jz_y))
        sc.blit(js, (js_x, js_y))
        bg.update()
        bg.draw(sc)
        pygame.display.update()


def run(button):
    wd = World(sc)
    hero = Player(wd)
    font = pygame.font.Font('font/simfang.ttf', 25)
    bg = pygame.image.load('media/bg.png').convert()
    pygame.transform.scale(bg, (wd.width, wd.height))
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                exit()

        pk = pygame.key.get_pressed()

        hero.control(pk)
        jg = wd.process()
        if jg is not None:
            end_interface(jg, wd.hit_counter, wd.kill_counter)
            return

        tps = clock.tick(30) / 1000
        # sc.fill((255, 255, 255))
        sc.blit(bg, (0, 0))

        wd.update(tps)

        ts = font.render(u"击中：" + str(wd.hit_counter), True, Color.from_palette('red').rgba8)
        sc.blit(ts, (0, 0))
        pygame.display.update()


def start_interface():
    bg = ButtonGroup()
    position = (ss[0] / 2, ss[1] / 2)
    size = (ss[0], 80)
    ks = TextButton('开始', position, size, 50, color=Color.from_palette('blue').rgb8,
                    bg=Color.from_palette('black').rgba8, call_back=run)
    bg.add(ks)

    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                exit()
            if e.type == MOUSEBUTTONDOWN:
                if len(bg.clicked(e.pos)) > 0:
                    return

        clock.tick(3)
        sc.fill((255, 255, 255))
        bg.update()
        bg.draw(sc)
        pygame.display.update()


if __name__ == '__main__':
    pygame.init()
    sc = pygame.display.set_mode(ss, 0, 32)
    pygame.display.set_caption("坦克大战")
    clock = pygame.time.Clock()
    start_interface()
