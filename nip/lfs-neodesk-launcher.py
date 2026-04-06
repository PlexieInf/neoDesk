import os
import curses
import subprocess

# ===== FIND LFS =====
def find_lfs():
    possible_paths = [
        r"C:\LFS\LFS.exe",
        os.path.expandvars(r"%USERPROFILE%\Desktop\LFS\LFS.exe"),
        os.path.expandvars(r"%USERPROFILE%\Desktop\LFS.exe"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # fallback search on desktop
    desktop = os.path.expandvars(r"%USERPROFILE%\Desktop")
    for root, dirs, files in os.walk(desktop):
        if "LFS.exe" in files:
            return os.path.join(root, "LFS.exe")

    return None


menu = ["LAUNCH LFS", "EXIT"]

def draw_ui(stdscr, selected):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # colors
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    # title
    title = [
        "██╗     ███████╗███████╗",
        "██║     ██╔════╝██╔════╝",
        "██║     █████╗  ███████╗",
        "██║     ██╔══╝  ╚════██║",
        "███████╗██║     ███████║",
        "╚══════╝╚═╝     ╚══════╝",
        "     Live For Speed Launcher"
    ]

    for i, line in enumerate(title):
        x = w//2 - len(line)//2
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(i + 2, x, line)
        stdscr.attroff(curses.color_pair(1))

    # menu
    for i, item in enumerate(menu):
        x = w//2 - len(item)//2
        y = len(title) + 6 + i

        if i == selected:
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(y, x, f"  {item}  ")
            stdscr.attroff(curses.color_pair(2))
        else:
            stdscr.addstr(y, x, f"  {item}  ")

    # footer
    footer = "arrow keys to move enter to select | q to quit"
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(h-2, w//2 - len(footer)//2, footer)
    stdscr.attroff(curses.color_pair(3))

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()

    selected = 0

    while True:
        draw_ui(stdscr, selected)
        key = stdscr.getch()

        if key in [ord('q'), ord('Q')]:
            break

        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(menu)

        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu)

        elif key == 10:
            if selected == 0:
                lfs_path = find_lfs()

                if lfs_path:
                    subprocess.Popen([lfs_path], cwd=os.path.dirname(lfs_path))
                else:
                    stdscr.clear()
                    msg = "LFS.exe not found on your system"
                    stdscr.addstr(0, 0, msg)
                    stdscr.getch()

            elif selected == 1:
                break


if __name__ == "__main__":
    curses.wrapper(main)
