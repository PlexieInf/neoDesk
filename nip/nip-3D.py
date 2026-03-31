import curses
import math
import time

# ===== CONFIG =====
WIDTH = 120
HEIGHT = 40
FOV = math.pi / 3
DEPTH = 20.0
SPEED = 4.0
ROT_SPEED = 2.5
JUMP_VEL = 6.0
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

def cast_ray(px, py, angle):
    dist = 0.0
    step = 0.05

    while dist < DEPTH:
        dist += step
        x = int(px + math.cos(angle) * dist)
        y = int(py + math.sin(angle) * dist)

        if x < 0 or x >= MAP_W or y < 0 or y >= MAP_H:
            return DEPTH

        if MAP[y][x] == "#":
            return dist

    return DEPTH

def clamp(v, a, b):
    return max(a, min(b, v))

def render(stdscr):
    global px, py, pa

    screen = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for x in range(WIDTH):
        ray_angle = (pa - FOV / 2) + (x / WIDTH) * FOV
        dist = cast_ray(px, py, ray_angle)

        ceiling = int(HEIGHT / 2 - HEIGHT / dist - pz * 4)
        floor = int(HEIGHT - ceiling)

        for y in range(HEIGHT):
            if y < ceiling:
                screen[y][x] = " "
            elif y > floor:
                shade = "."
                screen[y][x] = shade
            else:
                idx = int((1 - min(dist / DEPTH, 1)) * (len(SHADES) - 1))
                screen[y][x] = SHADES[idx]

    # entities
    for e in entities:
        dx = e["x"] - px
        dy = e["y"] - py
        dist = math.hypot(dx, dy)

        angle = math.atan2(dy, dx) - pa

        if abs(angle) < FOV / 2 and dist > 0.5:
            sx = int((angle + FOV / 2) / FOV * WIDTH)
            size = int(HEIGHT / dist)

            for y in range(-size // 2, size // 2):
                sy = int(HEIGHT / 2 + y - pz * 4)
                if 0 <= sy < HEIGHT and 0 <= sx < WIDTH:
                    char = "@" if e["hit"] > time.time() else "#"
                    screen[sy][sx] = char

    for y in range(HEIGHT):
        stdscr.addstr(y, 0, "".join(screen[y])[:WIDTH])

def punch():
    global entities
    for e in entities:
        dx = e["x"] - px
        dy = e["y"] - py
        dist = math.hypot(dx, dy)
        ang = math.atan2(dy, dx) - pa

        if abs(ang) < 0.4 and dist < 2:
            e["hp"] -= 1
            e["hit"] = time.time() + 0.2

def main(stdscr):
    global px, py, pa, pz, vy, on_ground

    curses.curs_set(0)
    stdscr.nodelay(True)

    last = time.time()

    while True:
        now = time.time()
        dt = now - last
        last = now

        key = stdscr.getch()

        # exit
        if key == ord("q"):
            break

        # movement
        if key == ord("w"):
            nx = px + math.cos(pa) * SPEED * dt
            ny = py + math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny

        if key == ord("s"):
            nx = px - math.cos(pa) * SPEED * dt
            ny = py - math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny

        if key == ord("a"):
            pa -= ROT_SPEED * dt
        if key == ord("d"):
            pa += ROT_SPEED * dt

        # jump
        if key == ord(" " ) and on_ground:
            vy = JUMP_VEL
            on_ground = False

        # gravity
        vy -= GRAVITY * dt
        pz += vy * dt

        if pz <= 0:
            pz = 0
            vy = 0
            on_ground = True

        # punch
        if key == ord("e"):
            punch()

        stdscr.clear()
        render(stdscr)
        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
