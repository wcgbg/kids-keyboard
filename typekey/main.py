#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import random
import string
import subprocess
import glob
import os
from PIL import Image, ImageDraw, ImageFont


def ascii_art(text):
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 48)
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
    while True:
        rand_char = random.choice(string.ascii_uppercase)
        # draw char
        curses.curs_set(False)
        stdscr.clear()
        lines = ascii_art(rand_char)
        for i, line in enumerate(lines):
            stdscr.addstr((scr_height-len(lines)) // 2 + i, (scr_width-len(line)) // 2, line)
        # get input
        while True:
            c = stdscr.getch()
            if c == 27:  # ESC
                return
            if chr(c).upper() == rand_char:
                break
        stdscr.clear()
        curses.endwin()
        proc = subprocess.Popen(['mplayer', random.choice(sounds)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call(['sl'])
        subprocess.check_call(['sl','-l'])
        proc.kill()
        stdscr = curses.initscr()


if __name__ == '__main__':
    curses.wrapper(main)
