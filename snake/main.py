#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import curses
import _curses


def main(stdscr):
    curses.curs_set(False)
    height, width = stdscr.getmaxyx()
    snake = [(height // 2, width // 2)] * 3
    while True:
        # paint
        stdscr.clear()
        for i, pos in reversed(list(enumerate(snake))):
            if i == 0:
                ch = '@'
            else:
                ch = 'o'
            try:
                stdscr.addch(pos[0], pos[1], ch)
            except _curses.error as e:
                pass
        # get input
        c = stdscr.getch()
        delta = None
        if c == ord('q'):
            break
        elif c == curses.KEY_LEFT:
            delta = (0, -1)
        elif c == curses.KEY_RIGHT:
            delta = (0, 1)
        elif c == curses.KEY_UP:
            delta = (-1, 0)
        elif c == curses.KEY_DOWN:
            delta = (1, 0)
        if delta is None:
            continue
        new_row = snake[0][0] + delta[0]
        if new_row < 0 or new_row >= height:
            continue
        new_col = snake[0][1] + delta[1]
        if new_col < 0 or new_col >= width:
            continue
        for i in range(len(snake) - 1, 0, -1):
            snake[i] = snake[i - 1]
        snake[0] = (new_row, new_col)


if __name__ == '__main__':
    curses.wrapper(main)
