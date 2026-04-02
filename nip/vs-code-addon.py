import os
import curses
import subprocess

# ===== FIND VS CODE =====
def find_vscode():
    possible_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Microsoft VS Code\Code.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft VS Code\Code.exe"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


menu = ["OPEN VS CODE", "EXIT"]

def draw_menu(stdscr, selected):
    stdscr.clear()

    ascii_title = [
        "██╗   ██╗███████╗     ██████╗ ██████╗ ██████╗ ███████╗",
        "██║   ██║██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝",
        "██║   ██║███████╗    ██║     ██║   ██║██║  ██║█████╗  ",
        "╚██╗ ██╔╝╚════██║    ██║     ██║   ██║██║  ██║██╔══╝  ",
        " ╚████╔╝ ███████║    ╚██████╗╚██████╔╝██████╔╝███████╗",
        "  ╚═══╝  ╚══════╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝",
    ]

    h, w = stdscr.getmaxyx()

    for i, line in enumerate(ascii_title):
        x = w//2 - len(line)//2
        y = i + 2
        stdscr.addstr(y, x, line)

    for idx, item in enumerate(menu):
        x = w//2 - len(item)//2
        y = len(ascii_title) + 5 + idx

        if idx == selected:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(y, x, f"> {item}")
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, f"  {item}")

    hint = "! use up and down arrows to navigate | press q to quit"
    stdscr.addstr(h-2, w//2 - len(hint)//2, hint)

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    selected = 0

    while True:
        draw_menu(stdscr, selected)
        key = stdscr.getch()

        # PANIC BUTTON
        if key in [ord('q'), ord('Q')]:
            break

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(menu)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu)
        elif key == 10:
            if selected == 0:
                vscode_path = find_vscode()
                if vscode_path:
                    subprocess.Popen([vscode_path])
                else:
                    stdscr.clear()
                    stdscr.addstr(0, 0, "VS Code not found.")
                    stdscr.getch()
            elif selected == 1:
                break


if __name__ == "__main__":
    curses.wrapper(main)
