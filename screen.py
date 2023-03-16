import curses

from curses.textpad import Textbox
from collections import deque

class Screen:
    def __init__(self):
        self._stdscr = curses.initscr()

        self._n_lines = 0
        self._max_lines = self._stdscr.getmaxyx()[0]
        self._msg_cache = deque(maxlen=self._max_lines-2)

    def __enter__(self):
        # Do not echo keys back to the client.
        curses.noecho()

        # Non-blocking or cbreak mode... do not wait for Enter key to be pressed.
        curses.cbreak()

        # Enable color if we can...
        if curses.has_colors():
            curses.start_color()

        # Create 3 ncurses color pair objects.
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

        # The variables below will correspond roughly to the X, Y coordinates of the 
        # of each window.
        window1 = []
        window2 = []

        # Window 1 will be on the top, Windows 2 and 3 will be on the bottom.
        window1Width = curses.COLS
        window1Height = curses.LINES - 1

        window1 = [0, 0, window1Width, window1Height]

        window2Width = curses.COLS
        window2Height = curses.LINES - window1Height
        window2 = [0, window1Height, window2Width, window2Height]

        win1 = curses.newwin(window1[3], window1[2], window1[1], window1[0])
        win1.bkgd(' ', curses.color_pair(1))
        win1.refresh()

        win2 = curses.newwin(window2[3], window2[2], window2[1], window2[0])
        win2.bkgd(' ', curses.color_pair(2))
        win2.addstr(0, 0, ">>> ", curses.color_pair(2))
        win2.refresh()

        self._windows = [win1, win2]

        return self
    
    def set_text(self, text: str, col=0) -> None:
        self._msg_cache.append(text)

        if self._n_lines < self._max_lines - 1:
            self._windows[0].addstr(self._n_lines, col, text, curses.color_pair(1))
            self._windows[0].refresh()
            self._n_lines += 1

        if len(self._msg_cache) != self._max_lines - 2:
            return

        self._windows[0].clear()
        for i, msg in enumerate(self._msg_cache):
            self._windows[0].addstr(i, col, msg, curses.color_pair(1))
        self._windows[0].refresh()

    
    def get_text(self) -> str:
        w = self._windows[1]
        box = Textbox(w)
        t = box.edit()

        w.clear()
        w.addstr(0, 0, ">>> ", curses.color_pair(2))
        w.refresh()

        return t[4:]

    def clear(self):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def __exit__(self, *args):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

