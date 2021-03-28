import math
import sys
import time
from dataclasses import dataclass
from random import randint

import pygame as pg
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

path = []
grnd_path = []

pg.init()

screen = pg.display.set_mode((1792, 896), pg.RESIZABLE)

pg.display.set_caption('killer')

running = True
start_time = time.time() - 0.5
moves = 0

mouse = False
mx, my = 0, 0
runs = 0

guards = []

pos = (0, 0)

def renderer(grnd, killer):
    if grnd_path:
        killer.grnd_x = grnd_path[0][0]
        killer.grnd_y = grnd_path[0][1]

    for i in guards:
        if i.grnd_path:
            i.grnd_x = i.grnd_path[0][0]
            i.grnd_y = i.grnd_path[0][1]
        if i.rots:
            i.rotation = i.rots[0]

    grnd.print_ground(killer)

    surface = pg.Surface((320, 640), pg.SRCALPHA)
    for i in range(1, len(path)):
        pg.draw.line(surface, (0, 255, 0), (grnd.blocks[path[i][1]][path[i][0]].get_grnd_x() + 15, grnd.blocks[path[i][1]][path[i][0]].get_grnd_y() + 15),
                     (grnd.blocks[path[i - 1][1]][path[i - 1][0]].get_grnd_x() + 15, grnd.blocks[path[i - 1][1]][path[i - 1][0]].get_grnd_y() + 15), 10)

    for i in guards:
        fill_block(screen, ((0, 0, 255), ((int(i.grnd_x + 10 + grnd.get_ground_start_x(killer)), int(i.grnd_y + 10 + grnd.get_ground_start_y(killer))), (20, 20))))
        if i.speed == 20:
            fill_block(screen, ((0, 255, 0), ((int(i.grnd_x + 12 + grnd.get_ground_start_x(killer)), int(i.grnd_y + 12 + grnd.get_ground_start_y(killer))), (10, 10))))

        pg.draw.line(surface, (255, 0, 0), (i.grnd_x + 15, i.grnd_y + 15), get_line_end_from_angle((i.grnd_x + 15, i.grnd_y + 15), i.rotation, 64), 5)

    killer.print(grnd)

    screen.blit(surface, ((grnd.get_ground_start_x(killer), grnd.get_ground_start_y(killer)), (grnd.get_ground_start_x(killer) + 320, grnd.get_ground_start_y(killer) + 640)))
    pg.display.update()

def dbg_label(Input, Print=True):
    myfont = pg.font.SysFont("monospace", 30)
    label = myfont.render(f"{Input}", True, (255, 255, 255))
    fill_block(screen, ((0, 0, 0), ((0, 0), (screen.get_width(), 30))))
    screen.blit(label, (0, 0))
    if Print:
        print(Input)

def fill_block(frame, Input):
    (r, g, b), ((x, y), (i, j)) = Input
    if x < 0:
        i -= 0 - x
    if y < 0:
        j -= 0 - y
    frame.fill((r, g, b), ((x, y), (i, j)))

def get_angle(pos_a, pos_b):
    return math.degrees(math.atan2(pos_b[1] - pos_a[1], pos_b[0] - pos_b[0]))

def raw_path(start, end, grnd, get_runs=False):
    grid = Grid(matrix=grnd.walls)

    start = grid.node(start[0], start[1])
    end = grid.node(end[0], end[1])

    finder = AStarFinder(diagonal_movement=DiagonalMovement.only_when_no_obstacle)
    path, runs = finder.find_path(start, end, grid)
    if get_runs:
        return runs
    out = []
    for i in path:
        out.append((i[0], i[1]))
    return out

def get_walk_cooldown():
    return randint(100, 600)

def get_line_end_from_angle(pos, angle, radius):
    angle *= 2
    x2 = pos[0] + math.cos(math.radians(angle)) * radius
    y2 = pos[1] + math.sin(math.radians(angle)) * radius
    return x2, y2

    # return radius * math.cos(angle) + x1, radius * math.sin(angle) + y1

class killer:

    def __init__(self):
        self.x = 4
        self.y = 18
        self.grnd_x = self.x * 32
        self.grnd_y = self.y * 32
        self.centre_x = 0
        self.centre_y = 0
        self.speed = 20

    def print(self, grnd):
        fill_block(screen, ((255, 0, 0), ((int(self.grnd_x + 10 + grnd.get_ground_start_x(self)), int(self.grnd_y + 10 + grnd.get_ground_start_y(self))), (20, 20))))

    def get_grnd_x(self):
        return self.x * 32

    def get_grnd_y(self):
        return self.y * 32

    def get_path(self, goal, grnd, get_runs=False):
        return raw_path([self.x, self.y],
                        [goal.x, goal.y],
                        grnd, get_runs)

class guard(killer):

    def __init__(self, grnd, killer):
        super().__init__()
        self.speed = 30
        self.x, self.y = grnd.find_free_spawn(killer)
        self.grnd_x = self.x * 32
        self.grnd_y = self.y * 32
        self.path = []
        self.grnd_path = []
        self.rots = []
        self.walk_cooldown = get_walk_cooldown()
        self.do_rot = False
        self.rotation = 0

    def print_g(self, grnd, killer, surface):
        fill_block(screen, ((0, 0, 255), ((int(self.grnd_x + 10 + grnd.get_ground_start_x(killer)), int(self.grnd_y + 10 + grnd.get_ground_start_y(killer))), (20, 20))))
        if self.speed == 20:
            fill_block(screen, ((0, 255, 0), ((int(self.grnd_x + 12 + grnd.get_ground_start_x(killer)), int(self.grnd_y + 12 + grnd.get_ground_start_y(killer))), (10, 10))))

        dbg_label((self.rotation, self.rots))
        pg.draw.line(surface, (255, 0, 0), (self.grnd_x + 15, self.grnd_y + 15), get_line_end_from_angle((self.grnd_x + 15, self.grnd_y + 15), self.rotation, 64), 5)

    @staticmethod
    def get_facing(path):
        return [path[1][0] - path[0][0], path[1][1] - path[0][1]]

    @staticmethod
    def get_rot(facing):
        return math.degrees(math.atan2(facing[1], facing[0]))

class ground:

    def __init__(self):
        self.width = 10
        self.height = self.width * 2
        self.walls = [
            [1, 1, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 0, 0, 1, 1, 0],
            [1, 1, 0, 1, 1, 0, 0, 1, 0, 0],
            [1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
            [1, 0, 1, 0, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 0, 1, 0, 1, 1],
            [0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 1, 0, 0, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
            [0, 1, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 0, 0, 0, 1, 1, 1, 1, 0, 0]
        ]
        self.rows = 20
        self.cols = 10

        self.blocks = []
        for y in range(20):
            temp = []
            for x in range(10):
                temp.append(Block(self.walls[y][x] == 1, (y, x)))
            self.blocks.append(temp)

    def print_ground(self, killer):
        fill_block(screen, ((0, 0, 0), ((self.get_ground_start_x(killer) - 10, self.get_ground_start_y(killer) - 10), (320 + 20, 640 + 20))))
        fill_block(screen, ((200, 200, 200), ((self.get_ground_start_x(killer), self.get_ground_start_y(killer)), (320, 640))))
        for y in range(20):
            for x in range(10):
                if self.walls[y][x] == 0:
                    fill_block(screen, ((100, 100, 100), ((self.get_ground_start_x(killer) + (x * 32), self.get_ground_start_y(killer) + (y * 32)), (32, 32))))

    @staticmethod
    def get_ground_start_x(killer):
        border = 96
        if killer.grnd_x > border + killer.centre_x:
            killer.centre_x = killer.grnd_x - border
        if killer.grnd_x < -border + killer.centre_x:
            killer.centre_x = killer.grnd_x + border
        return screen.get_width() / 2 - killer.centre_x

    @staticmethod
    def get_ground_start_y(killer):
        border = 96
        if killer.grnd_y > border + killer.centre_y:
            killer.centre_y = killer.grnd_y - border
        if killer.grnd_y < -border + killer.centre_y:
            killer.centre_y = killer.grnd_y + border
        return screen.get_height() / 2 - killer.centre_y

    def getLine(self, line):
        return self.blocks[line * 10:((line * 10) + 10)]

    @staticmethod
    def get_raw_from_block(block, killer, grnd):
        return [block.x * 32 + grnd.get_ground_start_x(killer), block.y * 32 + grnd.get_ground_start_y(killer)]

    def get_block_from_raw(self, raw, killer, grnd):
        x, y = raw
        if not self.in_ground(raw, killer):
            return None
        else:
            return grnd.blocks[int((y - self.get_ground_start_y(killer)) / 32)][int((x - self.get_ground_start_x(killer)) / 32)]

    def in_ground(self, raw, killer):
        x, y = raw
        if x <= self.get_ground_start_x(killer) + 2:
            return False
        elif x > self.get_ground_start_x(killer) + 320 - 2:
            return False
        elif y <= self.get_ground_start_y(killer) + 2:
            return False
        elif y > self.get_ground_start_y(killer) + 640 - 2:
            return False
        else:
            return True

    def find_free_Block(self):
        while True:
            spawn_pos = [randint(0, 9), randint(0, 19)]
            if self.walls[spawn_pos[1]][spawn_pos[0]] == 1:
                return spawn_pos

    def find_free_spawn(self, killer):
        while True:
            spawn_pos = [randint(0, 9), randint(0, 19)]
            if self.walls[spawn_pos[1]][spawn_pos[0]] == 1 and raw_path(spawn_pos, [killer.x, killer.y], self, True) > 4:
                return spawn_pos

@dataclass
class Block:
    def __init__(self, wall, pos):
        self.y, self.x = pos
        self.free: bool = wall
        self.parent: tuple = (0, 0)
        self.g: int = sys.maxsize  # Cost var
        self.h: int = 0  # Heuristic var
        self.f: int = 0  # Combined g + h

    def get_grnd_x(self):
        return self.x * 32

    def get_grnd_y(self):
        return self.y * 32

g1 = ground()
k1 = killer()

while running:
    current_time = time.time()
    elapsed_time = current_time - start_time

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEBUTTONDOWN:
            mouse = True

        if event.type == pg.MOUSEBUTTONUP:
            mouse = False

        if mouse:
            (mx, my) = pg.mouse.get_pos()

        if event.type == pg.KEYDOWN:

            if event.key == pg.K_ESCAPE:
                running = False

    if elapsed_time > 0.1:
        runs += 1

        if mouse:
            if g1.in_ground((mx, my), k1):
                if g1.get_block_from_raw((mx, my), k1, g1).free:
                    path = k1.get_path(g1.get_block_from_raw([mx, my], k1, g1), g1, False)

        if runs % k1.speed == 0:

            if not guards:
                for i in range(1):
                    guards.append(guard(g1, k1))

            if len(path) > 1:

                path.pop(0)
                k1.x = path[0][0]
                k1.y = path[0][1]

                grnd_path = []
                for i in range(1, k1.speed + 1):
                    grnd_path.append(((path[0][0] * 32 - k1.grnd_x) * (1 / k1.speed * i) + k1.grnd_x, (path[0][1] * 32 - k1.grnd_y) * (1 / k1.speed * i) + k1.grnd_y))

        for i in guards:
            if (k1.x, k1.y) == (i.x, i.y):
                guards.remove(i)
                for t in guards:
                    if k1.x + 5 >= t.x >= k1.x - 5 and k1.y + 5 >= t.y >= k1.y - 5:
                        t.speed = 20
                        t.path = raw_path([t.x, t.y], [k1.x, k1.y], g1, False)

            if runs % 600 == i.walk_cooldown and not i.path:
                i.walk_cooldown = get_walk_cooldown()
                i.path = raw_path([i.x, i.y], g1.find_free_Block(), g1, False)

            if runs % i.speed == 0:
                # if i.do_rot:
                #     i.do_rot = False
                #     if len(i.path) > 1:
                #         i.rots = []
                #         if len(i.path) > 1 or not i.get_facing(i.path) == i.get_facing(i.path.pop(0)):
                #             goal_rot = i.get_rot(i.get_facing(i.path))
                #             for t in range(1, i.speed + 1):
                #                 i.rots.append((goal_rot - i.rotation) * (1 / i.speed * t) + i.rotation)
                #             dbg_label((i.rotation, goal_rot, i.rots))

                if len(i.path) > 1:
                    # i.do_rot = True
                    i.rots = []
                    if len(i.path) > 1 or not i.get_facing(i.path) == i.get_facing(i.path.pop(0)):
                        goal_rot = i.get_rot(i.get_facing(i.path))
                        for t in range(1, i.speed + 1):
                            i.rots.append((goal_rot - i.rotation) * (1 / i.speed * t) + i.rotation)
                        dbg_label((i.rotation, goal_rot, i.rots))

                if len(i.path) > 1:
                    i.path.pop(0)
                    i.x = i.path[0][0]
                    i.y = i.path[0][1]

                    i.grnd_path = []
                    for t in range(1, i.speed + 1):
                        i.grnd_path.append(((i.path[0][0] * 32 - i.grnd_x) * (1 / i.speed * t) + i.grnd_x, (i.path[0][1] * 32 - i.grnd_y) * (1 / i.speed * t) + i.grnd_y))

                    if len(i.path) == 1:
                        i.path.pop(0)

            if len(i.rots) > 0:
                i.rots.pop(0)

        if len(grnd_path) > 0:
            grnd_path = grnd_path[1:]

        for i in guards:
            if len(i.grnd_path) > 0:
                i.grnd_path.pop(0)

        renderer(g1, k1)
        start_time = time.time() - 0.5
