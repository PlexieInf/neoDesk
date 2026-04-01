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
    "#..#...........#",
    "#..#....##.....#",
    "#..#........#..#",
    "#..#..#........#",
    "#..#######..#..#",
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
running = True

entities = [
    {"x": 6.0, "y": 3.0, "hp": 3, "hit": 0},
    {"x": 10.0, "y": 5.0, "hp": 3, "hit": 0},
]

pygame.init()
screen = pygame.display.set_mode((200, 200))
pygame.display.set_caption("nip doom input window dont touch")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 24)

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

    # entities
    for e in entities:
        dx = e["x"] - px
        dy = e["y"] - py
        dist = math.hypot(dx, dy)

        angle = math.atan2(dy, dx) - pa
        while angle < -math.pi: angle += 2*math.pi
        while angle > math.pi: angle -= 2*math.pi

        if abs(angle) < FOV/2 and dist > 0.5:
            sx = int((angle + FOV/2) / FOV * WIDTH)
            size = int(HEIGHT / dist)

            for y in range(-size//2, size//2):
                sy = int(HEIGHT/2 + y - pz*5)
                if 0 <= sy < HEIGHT and 0 <= sx < WIDTH:
                    col = 196 if e["hit"] > time.time() else 46
                    output[sy][sx] = f"\033[38;5;{col}m@\033[0m"

    return "\n".join("".join(row) for row in output)

def draw_key(label, pressed, x, y):
    color = (0, 255, 0) if pressed else (100, 100, 100)
    text = font.render(label, True, color)
    screen.blit(text, (x, y))

def punch():
    for e in entities:
        dx = e["x"] - px
        dy = e["y"] - py
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx) - pa

        if abs(angle) < 0.3 and dist < 2:
            e["hp"] -= 1
            e["hit"] = time.time() + 0.2

def stop():
    global running
    running = False
    pygame.quit()
    sys.stdout.write("\x1b[?25h")
    sys.exit()

def main():
    global px, py, pa, pz, vy, on_ground, running

    sys.stdout.write("\x1b[2J")
    sys.stdout.write("\x1b[?25l")

    while running:
        dt = clock.tick(30) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop()

        keys = pygame.key.get_pressed()

        # 🔴 EMERGENCY EXIT KEY
        if keys[pygame.K_q]:
            stop()

        if keys[pygame.K_w]:
            nx = px + math.cos(pa) * SPEED * dt
            ny = py + math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny

        if keys[pygame.K_s]:
            nx = px - math.cos(pa) * SPEED * dt
            ny = py - math.sin(pa) * SPEED * dt
            if MAP[int(ny)][int(nx)] != "#":
                px, py = nx, ny

        if keys[pygame.K_a]: pa -= ROT_SPEED * dt
        if keys[pygame.K_d]: pa += ROT_SPEED * dt
        if keys[pygame.K_LEFT]: pa -= ROT_SPEED * dt
        if keys[pygame.K_RIGHT]: pa += ROT_SPEED * dt

        if keys[pygame.K_SPACE] and on_ground:
            vy = JUMP_VEL
            on_ground = False

        vy -= GRAVITY * dt
        pz += vy * dt

        if pz <= 0:
            pz = 0
            vy = 0
            on_ground = True

        if keys[pygame.K_e]:
            punch()

        screen.fill((20,20,20))

        draw_key("W", keys[pygame.K_w], 80, 20)
        draw_key("A", keys[pygame.K_a], 40, 60)
        draw_key("S", keys[pygame.K_s], 80, 60)
        draw_key("D", keys[pygame.K_d], 120, 60)
        draw_key("E", keys[pygame.K_e], 80, 90)
        draw_key("Q", keys[pygame.K_q], 120, 90)

        pygame.display.flip()

        sys.stdout.write("\x1b[H")
        sys.stdout.write(render())
        sys.stdout.flush()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop()
