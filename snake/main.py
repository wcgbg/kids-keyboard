#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import curses
import _curses


def main(stdscr):
    curses.curs_set(False)
    height, width = stdscr.getmaxyx()
    snake = [(height // 2, width // 2)] * 5
    food = (random.randint(0, height - 1), random.randint(0, width - 1))
    head_color = 1
    body_color = 2
    food_color = 3
    curses.init_pair(head_color, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(body_color, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(food_color, curses.COLOR_GREEN, curses.COLOR_BLACK)
    while True:
        # paint
        stdscr.clear()
        for i, pos in reversed(list(enumerate(snake))):
            # TODO: try unicode '⬤⚫●'
            try:
                if i == 0:
                    stdscr.addch(pos[0], pos[1], '@', curses.A_BOLD | curses.color_pair(head_color))
                else:
                    stdscr.addch(pos[0], pos[1], 'o', curses.color_pair(body_color))
            except _curses.error as e:
                pass
        try:
            stdscr.addch(food[0], food[1], '$', curses.A_BLINK | curses.A_BOLD | curses.color_pair(food_color))
        except _curses.error as e:
            pass
        stdscr.refresh()
        # time.sleep(1)
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
        if snake[0] == food:
            food = (random.randint(0, height - 1), random.randint(
                0, width - 1))
            snake.append(snake[-1])


if __name__ == '__main__':
    curses.wrapper(main)
