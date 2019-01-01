#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import random
import subprocess
import glob
import os
from PIL import Image, ImageDraw, ImageFont


def ascii_art(text):
    font = ImageFont.truetype('FreeSans.ttf', 48)
    width, height = font.getsize(text)
    # round up to even
    height += height % 2
    image = Image.new('1', (width, height), 1)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font)
    result = []
    for half_row in range(height // 2):
        line = ''
        for col in range(width):
            top = image.getpixel((col, half_row * 2))
            bottom = image.getpixel((col, half_row * 2 + 1))
            if top:
                if bottom:
                    line += ' '
                else:
                    line += '▄'
            else:
                if bottom:
                    line += '▀'
                else:
                    line += '█'
        result.append(line)
    return result


def main(stdscr):
    self_dir = os.path.dirname(os.path.realpath(__file__))
    sounds = glob.glob(self_dir + '/sound/*.mp3')
    assert sounds
    scr_height, scr_width = stdscr.getmaxyx()
    char_idx = random.randint(0, 25)
    while True:
        curses.curs_set(False)
        stdscr.clear()
        lines = ascii_art(chr(ord('A') + char_idx))
        for i, line in enumerate(lines):
            stdscr.addstr((scr_height-len(lines)) // 2 + i, (scr_width-len(line)) // 2, line)
        # get input
        c = stdscr.getch()
        if c == 27:  # ESC
            break
        elif c == ord('a') + char_idx or c == ord('A') + char_idx:
            stdscr.clear()
            curses.endwin()
            proc = subprocess.Popen(['mplayer', random.choice(sounds)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.check_call(['sl'])
            proc.kill()
            stdscr = curses.initscr()
            char_idx = random.randint(0, 25)


if __name__ == '__main__':
    curses.wrapper(main)
