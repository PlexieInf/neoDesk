import curses
import math
import time

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

def safe_draw(stdscr, y, x, ch):
    try:
        if y < 0 or x < 0:
            return
        stdscr.addch(y, x, ch)
    except:
        pass

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

def render(stdscr, w, h):
    screen = [[" " for _ in range(w)] for _ in range(h)]

    for x in range(w):
        ray_angle = (pa - FOV / 2) + (x / w) * FOV
        dist = cast_ray(px, py, ray_angle)

        ceiling = int(h / 2 - h / max(dist, 0.0001) - pz * 4)
        floor = int(h - ceiling)

        for y in range(h):
            if y < 0 or y >= h or x < 0 or x >= w:
                continue

            if y < ceiling:
                continue
            elif y > floor:
                screen[y][x] = "."
            else:
                idx = int((1 - min(dist / DEPTH, 1)) * (len(SHADES) - 1))
                screen[y][x] = SHADES[idx]

    for e in entities:
        dx = e["x"] - px
        dy = e["y"] - py
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx) - pa

        if abs(angle) < FOV / 2 and dist > 0.5:
            sx = int((angle + FOV / 2) / FOV * w)
            size = max(1, int(h / max(dist, 0.1)))

            for y in range(-size // 2, size // 2):
                sy = int(h / 2 + y - pz * 4)
                if 0 <= sy < h and 0 <= sx < w:
                    screen[sy][sx] = "@" if e["hit"] > time.time() else "#"

    for y in range(h):
        line = "".join(screen[y])
        try:
            stdscr.addstr(y, 0, line[:w])
        except:
            continue

def main(stdscr):
    global px, py, pa, pz, vy, on_ground

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    last = time.time()

    while True:
        h, w = stdscr.getmaxyx()

        h = max(10, h)
        w = max(20, w)

        now = time.time()
        dt = now - last
        last = now

        key = stdscr.getch()

        if key == ord("q"):
            break

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

        if key == ord(" " ) and on_ground:
            vy = JUMP_VEL
            on_ground = False

        vy -= GRAVITY * dt
        pz += vy * dt

        if pz <= 0:
            pz = 0
            vy = 0
            on_ground = True

        if key == ord("e"):
            punch()

        stdscr.clear()
        render(stdscr, w, h)
        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
