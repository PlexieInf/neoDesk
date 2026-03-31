import curses
import math
import time

# ================== SETTINGS ==================
FOV = math.pi / 3
DEPTH = 20.0
SPEED = 12.0
ROT_SPEED = 6.0
JUMP_VEL = 8.0
GRAVITY = 18.0

WALL_SHADES = " .:-=+*#%@"

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

# Player
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
    step = 0.04
    while dist < DEPTH:
        dist += step
        x = int(px + math.cos(angle) * dist)
        y = int(py + math.sin(angle) * dist)
        if x < 0 or x >= MAP_W or y < 0 or y >= MAP_H:
            return dist
        if MAP[y][x] == "#":
            return dist
    return DEPTH

def punch():
    global entities
    for e in entities:
        dx = e["x"] - px
        dy = e["y"] - py
        dist = math.hypot(dx, dy)
        ang = math.atan2(dy, dx) - pa
        if abs(ang) < 0.5 and dist < 2.5:
            e["hp"] -= 1
            e["hit"] = time.time() + 0.25

def safe_addch(stdscr, y, x, ch, color=0):
    """Ultra-safe draw - never write to bottom-right corner"""
    h, w = stdscr.getmaxyx()
    if y < 0 or y >= h - 1 or x < 0 or x >= w - 1:   # avoid bottom-right
        return
    try:
        stdscr.addch(y, x, ch, curses.color_pair(color))
    except:
        pass

def render(stdscr, w, h):
    for x in range(w):
        ray_angle = (pa - FOV / 2) + (x / w) * FOV
        dist = cast_ray(px, py, ray_angle)

        wall_height = int(h / max(dist, 0.1))
        ceiling = max(0, (h - wall_height) // 2 - int(pz * 4))
        floor_start = h - ceiling

        shade_idx = int((1 - min(dist / DEPTH, 1)) * (len(WALL_SHADES) - 1))
        wall_char = WALL_SHADES[shade_idx]

        for y in range(h):
            if y < ceiling:
                safe_addch(stdscr, y, x, ' ', 1)          # Ceiling
            elif y < floor_start:
                safe_addch(stdscr, y, x, wall_char, 2)    # Wall
            else:
                # Floor
                floor_char = '#' if (y - h // 2) > h * 0.25 else '.'
                safe_addch(stdscr, y, x, floor_char, 3)

    # Entities
    for e in entities:
        dx = e["x"] - px
        dy = e["y"] - py
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx) - pa

        if abs(angle) < FOV / 2 and dist > 0.4:
            sx = int((angle + FOV / 2) / FOV * w)
            size = max(1, int(h / max(dist, 0.5)))

            char = '@' if e["hit"] > time.time() else 'E'
            color = 4 if e["hit"] > time.time() else 5

            for offset in range(-size//2, size//2 + 1):
                sy = int(h / 2 + offset - pz * 4)
                if 0 <= sy < h:
                    safe_addch(stdscr, sy, sx, char, color)

def main(stdscr):
    global px, py, pa, pz, vy, on_ground

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)      # Ceiling
    curses.init_pair(2, curses.COLOR_WHITE, -1)     # Wall
    curses.init_pair(3, curses.COLOR_BLUE, -1)      # Floor
    curses.init_pair(4, curses.COLOR_RED, -1)       # Hit enemy
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)   # Enemy

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    stdscr.keypad(True)

    last = time.time()

    while True:
        h, w = stdscr.getmaxyx()
        if h < 15 or w < 40:
            stdscr.clear()
            stdscr.addstr(2, 2, "Please make the terminal window larger!")
            stdscr.refresh()
            if stdscr.getch() != -1:
                break
            time.sleep(0.2)
            continue

        dt = time.time() - last
        last = time.time()

        # Multi-key input
        keys = set()
        while True:
            key = stdscr.getch()
            if key == -1:
                break
            keys.add(key)

        # Movement
        if ord('w') in keys or curses.KEY_UP in keys:
            nx = px + math.cos(pa) * SPEED * dt
            ny = py + math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny

        if ord('s') in keys or curses.KEY_DOWN in keys:
            nx = px - math.cos(pa) * SPEED * dt
            ny = py - math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny

        if ord('a') in keys or curses.KEY_LEFT in keys:
            pa -= ROT_SPEED * dt
        if ord('d') in keys or curses.KEY_RIGHT in keys:
            pa += ROT_SPEED * dt

        # Jump
        if (ord(' ') in keys) and on_ground:
            vy = JUMP_VEL
            on_ground = False

        vy -= GRAVITY * dt
        pz += vy * dt
        if pz <= 0:
            pz = 0
            vy = 0
            on_ground = True

        if ord('e') in keys:
            punch()

        if ord('q') in keys:
            break

        stdscr.clear()
        render(stdscr, w, h)

        # HUD (safe position)
        try:
            stdscr.addstr(0, 0, f"X:{px:.1f} Y:{py:.1f} A:{math.degrees(pa):.0f}°", curses.color_pair(2))
            stdscr.addstr(h-2, 0, "WASD/Arrows = Move   E = Punch   Space = Jump   Q = Quit", curses.color_pair(1))
        except:
            pass

        stdscr.refresh()
        time.sleep(0.016)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
