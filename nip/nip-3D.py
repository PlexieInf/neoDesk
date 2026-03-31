import curses
import time
import random

ball_char = "o"
paddle_char = "|"

def clamp(v, min_v, max_v):
    return max(min_v, min(max_v, v))

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(30)

    sh, sw = stdscr.getmaxyx()

    paddle_h = 5
    player_x = 2
    ai_x = sw - 3

    player_y = sh // 2
    ai_y = sh // 2

    ball_x = sw // 2
    ball_y = sh // 2
    ball_dx = 1
    ball_dy = 1

    player_score = 0
    ai_score = 0

    while True:
        stdscr.clear()

        sh, sw = stdscr.getmaxyx()

        if sh < 10 or sw < 30:
            stdscr.addstr(0, 0, "terminal too small grow it up")
            stdscr.refresh()
            continue

        key = stdscr.getch()

        if key == curses.KEY_UP:
            player_y -= 1
        elif key == curses.KEY_DOWN:
            player_y += 1

        player_y = clamp(player_y, 1, sh - paddle_h - 1)

        if ball_y < ai_y:
            ai_y -= 1
        elif ball_y > ai_y:
            ai_y += 1

        ai_y = clamp(ai_y, 1, sh - paddle_h - 1)

        ball_x += ball_dx
        ball_y += ball_dy

        if ball_y <= 1 or ball_y >= sh - 2:
            ball_dy *= -1

        if ball_x == player_x + 1:
            if player_y <= ball_y <= player_y + paddle_h:
                ball_dx *= -1

        if ball_x == ai_x - 1:
            if ai_y <= ball_y <= ai_y + paddle_h:
                ball_dx *= -1

        if ball_x <= 0:
            ai_score += 1
            ball_x = sw // 2
            ball_y = sh // 2

        if ball_x >= sw - 1:
            player_score += 1
            ball_x = sw // 2
            ball_y = sh // 2

        for i in range(paddle_h):
            if 0 < player_y + i < sh:
                stdscr.addstr(player_y + i, player_x, paddle_char)
            if 0 < ai_y + i < sh:
                stdscr.addstr(ai_y + i, ai_x, paddle_char)

        if 0 < ball_y < sh and 0 < ball_x < sw:
            stdscr.addstr(ball_y, ball_x, ball_char)

        score_text = f"{player_score} vs {ai_score}"
        stdscr.addstr(0, sw // 2 - len(score_text) // 2, score_text)

        stdscr.refresh()
        time.sleep(0.03)

if __name__ == "__main__":
    curses.wrapper(main)
