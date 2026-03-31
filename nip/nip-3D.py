import pygame
import math
import sys
import time

# ===== CONFIG =====
WIDTH = 120
HEIGHT = 40
FOV = math.pi / 3
DEPTH = 150
SPEED = 6.0
ROT_SPEED = 2.0
JUMP_VEL = 5.0
GRAVITY = 12.0

SHADES = " .:-=+*#%@"

MAP = [
    "################",
    "#..............#",
    "#.......##.....#",
    "#..............#",
    "#.....#........#",
    "#..............#",
    "#..............#",
    "################",
]

MAP_W = len(MAP[0])
MAP_H = len(MAP)

px, py = 3.0, 3.0
pa = 0.0
pz = 0.0
vy = 0.0
on_ground = True

entities = [
    {"x": 6.0, "y": 3.0, "hp": 3, "hit": 0},
    {"x": 10.0, "y": 5.0, "hp": 3, "hit": 0},
]

pygame.init()

# tiny window just to capture input focus properly
screen = pygame.display.set_mode((100, 100))
pygame.display.set_caption("nip doom running (dont close me lol)")
clock = pygame.time.Clock()

def cast_ray(angle):
    step = 0.05
    dist = 0.0
    while dist < DEPTH:
        dist += step
        x = int(px + math.cos(angle) * dist)
        y = int(py + math.sin(angle) * dist)

        if x < 0 or x >= MAP_W or y < 0 or y >= MAP_H:
            return DEPTH
        if MAP[y][x] == "#":
            return dist
    return DEPTH

def render():
    output = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for x in range(WIDTH):
        ray_angle = (pa - FOV / 2.0) + (x / WIDTH) * FOV
        dist = cast_ray(ray_angle)

        ceiling = int(HEIGHT / 2 - HEIGHT / dist - pz * 5)
        floor = int(HEIGHT - ceiling)

        for y in range(HEIGHT):
            if y < ceiling:
                output[y][x] = "\033[38;5;235m \033[0m"

            elif y > floor:
                b = 1.0 - ((y - HEIGHT/2) / (HEIGHT/2))
                col = int(94 + b * 30)
                output[y][x] = f"\033[38;5;{col}m.\033[0m"

            else:
                shade_index = int((1 - min(dist / DEPTH, 1)) * (len(SHADES)-1))
                col = int(17 + (1 - min(dist / DEPTH, 1)) * 20)
                output[y][x] = f"\033[38;5;{col}m{SHADES[shade_index]}\033[0m"

    return "\n".join("".join(row) for row in output)

def punch():
    for e in entities:
        dx = e["x"] - px
        dy = e["y"] - py
        dist = math.hypot(dx, dy)

        angle = math.atan2(dy, dx) - pa
        if abs(angle) < 0.3 and dist < 2:
            e["hp"] -= 1
            e["hit"] = time.time() + 0.2

def main():
    global px, py, pa, pz, vy, on_ground

    sys.stdout.write("\x1b[2J")
    sys.stdout.write("\x1b[?25l")

    w = a = s = d = False
    left = right = False
    running = True

    while running:
        dt = clock.tick(30) / 1000.0

        # EVENTS (this replaces key.get_pressed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w: w = True
                if event.key == pygame.K_a: a = True
                if event.key == pygame.K_s: s = True
                if event.key == pygame.K_d: d = True
                if event.key == pygame.K_LEFT: left = True
                if event.key == pygame.K_RIGHT: right = True
                if event.key == pygame.K_SPACE and on_ground:
                    vy = JUMP_VEL
                    on_ground = False
                if event.key == pygame.K_e:
                    punch()
                if event.key == pygame.K_q:
                    running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w: w = False
                if event.key == pygame.K_a: a = False
                if event.key == pygame.K_s: s = False
                if event.key == pygame.K_d: d = False
                if event.key == pygame.K_LEFT: left = False
                if event.key == pygame.K_RIGHT: right = False

        # movement
        if w:
            nx = px + math.cos(pa) * SPEED * dt
            ny = py + math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny

        if s:
            nx = px - math.cos(pa) * SPEED * dt
            ny = py - math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny

        if a: pa -= ROT_SPEED * dt
        if d: pa += ROT_SPEED * dt
        if left: pa -= ROT_SPEED * dt
        if right: pa += ROT_SPEED * dt

        # gravity
        vy -= GRAVITY * dt
        pz += vy * dt
        if pz <= 0:
            pz = 0
            vy = 0
            on_ground = True

        # render terminal
        sys.stdout.write("\x1b[H")
        sys.stdout.write(render())
        sys.stdout.flush()

    pygame.quit()
    sys.stdout.write("\x1b[?25h")

if __name__ == "__main__":
    main()
