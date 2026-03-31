import os
import sys
import time
import random
import msvcrt

WIDTH = 60
HEIGHT = 20

ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_dx = 1
ball_dy = 1

player_y = HEIGHT // 2
ai_y = HEIGHT // 2

score_player = 0
score_ai = 0

def clear():
    print("\033[2J\033[H", end="")

def draw():
    clear()

    # top border
    print("#" * WIDTH)

    for y in range(HEIGHT):
        line = ""

        for x in range(WIDTH):

            # player paddle (left)
            if x == 2 and abs(y - player_y) <= 2:
                line += "|"

            # ai paddle (right)
            elif x == WIDTH - 3 and abs(y - ai_y) <= 2:
                line += "|"

            # ball
            elif x == ball_x and y == ball_y:
                line += "O"

            else:
                line += " "

        print(line)

    print("#" * WIDTH)
    print(f"Player: {score_player}   AI: {score_ai}")
    print("W/S to move | Q to quit")

def update_ball():
    global ball_x, ball_y, ball_dx, ball_dy, score_player, score_ai

    ball_x += ball_dx
    ball_y += ball_dy

    # top bottom bounce
    if ball_y <= 0 or ball_y >= HEIGHT - 1:
        ball_dy *= -1

    # player paddle collision
    if ball_x == 3 and abs(ball_y - player_y) <= 2:
        ball_dx *= -1

    # ai paddle collision
    if ball_x == WIDTH - 4 and abs(ball_y - ai_y) <= 2:
        ball_dx *= -1

    # scoring
    if ball_x <= 0:
        score_ai += 1
        reset_ball()

    if ball_x >= WIDTH - 1:
        score_player += 1
        reset_ball()

def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy

    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_dx = random.choice([-1, 1])
    ball_dy = random.choice([-1, 1])

def update_ai():
    global ai_y

    reaction_delay = 0.6  # higher = worse ai

    # only react sometimes
    if random.random() < reaction_delay:
        return

    # add imperfection
    offset = random.randint(-2, 2)

    target = ball_y + offset

    if target > ai_y:
        ai_y += 1
    elif target < ai_y:
        ai_y -= 1

    # stop it from teleporting outside bounds
    if ai_y < 2:
        ai_y = 2
    if ai_y > HEIGHT - 3:
        ai_y = HEIGHT - 3

def input_player():
    global player_y

    if msvcrt.kbhit():
        key = msvcrt.getch()

        if key == b'w' and player_y > 2:
            player_y -= 1
        elif key == b's' and player_y < HEIGHT - 3:
            player_y += 1
        elif key == b'q':
            return False

    return True

def main():
    running = True

    while running:
        draw()
        running = input_player()
        update_ball()
        update_ai()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
