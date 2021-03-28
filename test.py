import math

import pygame as pg

pg.init()
screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)
surface = pg.Surface((1920, 1080), pg.SRCALPHA)

mx, my = 0, 0

def get_line_end_from_angle(pos, angle, radius):
    angle -= 90
    x1, y1 = pos
    return radius * math.cos(angle) + x1, radius * math.sin(angle) + y1

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if pg.mouse:
            (mx, my) = pg.mouse.get_pos()

        if event.type == pg.KEYDOWN:

            if event.key == pg.K_ESCAPE:
                running = False

    surface.fill((0, 0, 0))
    for i in range(720):
        pg.draw.line(surface, (i // 3, i // 6, i // 9), (mx, my), get_line_end_from_angle((mx, my), i, 2000), 1)
    screen.blit(surface, ((0, 0), (mx, my)))
    pg.display.update()