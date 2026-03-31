import curses
import math
import time

# ================== SETTINGS ==================
FOV = math.pi / 3
DEPTH = 20.0
SPEED = 12.0          # Much faster movement
ROT_SPEED = 6.0       # Much faster turning
JUMP_VEL = 8.0
GRAVITY = 18.0

# Color shades for walls and floor
WALL_SHADES = " .:-=+*#%@"
FLOOR_COLOR = curses.COLOR_BLUE
CEILING_COLOR = curses.COLOR_BLACK

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

# Player state
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
    step = 0.03
    while dist < DEPTH:
        dist += step
        x = int(px + math.cos(angle) * dist)
        y = int(py + math.sin(angle) * dist)
        if x < 0 or x >= MAP_W or y < 0 or y >= MAP_H:
            return DEPTH, True  # hit edge
        if MAP[y][x] == "#":
            return dist, False
    return DEPTH, True

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

def render(stdscr, w, h):
    for x in range(w):
        ray_angle = (pa - FOV / 2) + (x / w) * FOV
        dist, edge = cast_ray(px, py, ray_angle)

        # Wall height
        wall_height = int(h / max(dist, 0.0001))
        ceiling = max(0, (h - wall_height) // 2 - int(pz * 5))
        floor_start = h - ceiling

        shade_idx = int((1 - min(dist / DEPTH, 1)) * (len(WALL_SHADES) - 1))
        wall_char = WALL_SHADES[shade_idx]

        for y in range(h):
            if y < ceiling:
                # Ceiling
                stdscr.addch(y, x, ' ', curses.color_pair(1))
            elif y < floor_start:
                # Wall
                color_pair = 3 if edge else 2
                stdscr.addch(y, x, wall_char, curses.color_pair(color_pair))
            else:
                # Floor with perspective shading
                floor_dist = (y - h / 2) / (h / 2)
                if floor_dist < 0.3:
                    stdscr.addch(y, x, '.', curses.color_pair(4))
                else:
                    stdscr.addch(y, x, '#', curses.color_pair(5))

    # Draw entities (simple sprites)
    for e in entities:
        dx = e["x"] - px
        dy = e["y"] - py
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx) - pa

        if abs(angle) < FOV / 2 and dist > 0.4:
            sx = int((angle + FOV / 2) / FOV * w)
            size = max(2, int(h / max(dist, 0.1)))

            char = '@' if e["hit"] > time.time() else 'E'
            color = curses.color_pair(6) if e["hit"] > time.time() else curses.color_pair(7)

            for dy_offset in range(-size//2, size//2 + 1):
                sy = int(h / 2 + dy_offset - pz * 5)
                if 0 <= sy < h and 0 <= sx < w:
                    try:
                        stdscr.addch(sy, sx, char, color)
                    except:
                        pass

def main(stdscr):
    global px, py, pa, pz, vy, on_ground

    # Setup colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Ceiling
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Normal wall
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Edge wall
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Close floor
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Far floor
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)       # Hit enemy
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Normal enemy

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    stdscr.keypad(True)

    last = time.time()

    while True:
        h, w = stdscr.getmaxyx()
        if h < 15 or w < 40:
            stdscr.addstr(0, 0, "Window too small! Resize and press any key.")
            stdscr.refresh()
            stdscr.getch()
            continue

        now = time.time()
        dt = now - last
        last = now

        # Multi-key input handling
        keys_pressed = set()
        while True:
            key = stdscr.getch()
            if key == -1:
                break
            keys_pressed.add(key)

        # Movement
        moved = False
        if ord('w') in keys_pressed or curses.KEY_UP in keys_pressed:
            nx = px + math.cos(pa) * SPEED * dt
            ny = py + math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny
                moved = True

        if ord('s') in keys_pressed or curses.KEY_DOWN in keys_pressed:
            nx = px - math.cos(pa) * SPEED * dt
            ny = py - math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny
                moved = True

        if ord('a') in keys_pressed or curses.KEY_LEFT in keys_pressed:
            pa -= ROT_SPEED * dt

        if ord('d') in keys_pressed or curses.KEY_RIGHT in keys_pressed:
            pa += ROT_SPEED * dt

        # Jumping
        if (ord(' ') in keys_pressed or ord('\n') in keys_pressed) and on_ground:
            vy = JUMP_VEL
            on_ground = False

        # Physics
        vy -= GRAVITY * dt
        pz += vy * dt
        if pz <= 0:
            pz = 0
            vy = 0
            on_ground = True

        # Punch
        if ord('e') in keys_pressed:
            punch()

        # Quit
        if ord('q') in keys_pressed:
            break

        stdscr.clear()
        render(stdscr, w, h)

        # HUD
        stdscr.addstr(0, 0, f"X:{px:.1f} Y:{py:.1f} A:{math.degrees(pa):.0f}°  HP:100", curses.color_pair(2))
        stdscr.addstr(h-1, 0, "WASD/Move  Mouse not supported  E=Punch  SPACE=Jump  Q=Quit", curses.color_pair(1))

        stdscr.refresh()
        time.sleep(0.016)  # ~60 FPS cap

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Error: {e}")
