#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import curses
import random
import string
import subprocess
import glob
import time
import os
from PIL import Image, ImageDraw, ImageFont


def ascii_art(text: str, font_size: int, square_font: bool) -> str:
    font = ImageFont.truetype(
        '/usr/share/fonts/truetype/freefont/FreeSans.ttf', font_size)
    width, height = font.getsize(text)
    if square_font:
        image = Image.new('1', (width, height), 1)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, font=font)
        result = []
        for row in range(height):
            line = ''
            for col in range(width):
                line += ' ' if image.getpixel((col, row)) else '█'
            result.append(line)
        return result
    else:
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
    parser = argparse.ArgumentParser(description='Typing')
    parser.add_argument('--font_size', type=int, default=48)
    parser.add_argument('--square_font', action='store_true')
    parser.add_argument(
        '--charset', default='upper', help='e.g. upper,lower,digits')
    args = parser.parse_args()

    self_dir = os.path.dirname(os.path.realpath(__file__))
    sounds = glob.glob(self_dir + '/sound/*.mp3')
    assert sounds
    scr_height, scr_width = stdscr.getmaxyx()
    proc = None
    character_set = ''
    if 'upper' in args.charset:
        character_set += string.ascii_uppercase
    if 'lower' in args.charset:
        character_set += string.ascii_lowercase
    if 'digits' in args.charset:
        character_set += string.digits
    assert character_set
    while True:
        rand_char = random.choice(character_set)
        # draw char
        curses.curs_set(False)
        stdscr.clear()
        # wait until SPACE
        while True:
            c = stdscr.getch()
            if c == 27:  # ESC
                return
            if c == 32:  # SPACE
                break
        lines = ascii_art(rand_char, args.font_size, args.square_font)
        for i, line in enumerate(lines):
            stdscr.addstr((scr_height - len(lines)) // 2 + i,
                          (scr_width - len(line)) // 2, line)
        start_time = time.time()
        # get input
        while True:
            c = stdscr.getch()
            if c == 27:  # ESC
                return
            if chr(c).upper() == rand_char.upper():
                break
        duration = time.time() - start_time
        stdscr.clear()
        curses.endwin()
        proc = subprocess.Popen(['mplayer', random.choice(sounds)],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if duration < 4:
            subprocess.check_call(['sl', '-F'])
            subprocess.check_call(['sl', '-l', '-F'])
            subprocess.check_call(['sl', '-l', '-F'])
        elif duration < 8:
            subprocess.check_call(['sl'])
            subprocess.check_call(['sl', '-l'])
            subprocess.check_call(['sl', '-l'])
        elif duration < 16:
            subprocess.check_call(['sl'])
            subprocess.check_call(['sl', '-l'])
        else:
            subprocess.check_call(['sl'])
        proc.kill()
        stdscr = curses.initscr()


if __name__ == '__main__':
    curses.wrapper(main)
