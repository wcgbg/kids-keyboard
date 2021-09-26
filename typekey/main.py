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


def ascii_art(text: str, prefex_length: int, font_size: int, square_font: bool,
              max_width: int) -> (str, int):
    ''' Returns the ascii chars and the prefix width'''
    while True:
        font = ImageFont.truetype(
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf', font_size)
        width, height = font.getsize(text)
        if width <= max_width:
            break
        font_size -= 1
    assert prefex_length >= 0
    assert prefex_length < len(text)
    prefix_width, _ = font.getsize(text[:prefex_length])
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
        return result, prefix_width
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
        return result, prefix_width


def main(stdscr):
    parser = argparse.ArgumentParser(description='Typing')
    parser.add_argument('--font_size', type=int, default=48)
    parser.add_argument('--square_font', action='store_true')
    parser.add_argument(
        '--charset', default='upper', help='e.g. upper,lower,digits,jeremy')
    args = parser.parse_args()

    random.seed()
    self_dir = os.path.dirname(os.path.realpath(__file__))
    sounds = glob.glob(self_dir + '/sound/*.mp3')
    assert sounds
    scr_height, scr_width = stdscr.getmaxyx()
    proc = None
    words = []
    if 'upper' in args.charset:
        words += list(string.ascii_uppercase)
    if 'lower' in args.charset:
        words += list(string.ascii_lowercase)
    if 'digits' in args.charset:
        words += list(string.digits)
    if 'jeremy' in args.charset:
        words += list('QWETYUIOPSDFJKZXCVBM')
    if 'word' in args.charset:
        words += ['Joseph', 'Jeremy', 'mom', 'dad']
        words += [
            'the', 'be', 'and', 'a', 'of', 'to', 'in', 'I', 'you', 'it',
            'have', 'to', 'that', 'for', 'do', 'he', 'with', 'on', 'this',
            'we', 'that', 'not', 'but', 'they', 'say', 'at', 'what', 'his',
            'from', 'go', 'or', 'by', 'get', 'she', 'my', 'can', 'as', 'know',
            'if', 'me', 'your', 'all', 'who', 'will', 'so', 'make', 'just',
            'up', 'time', 'see', 'her', 'as', 'out', 'one', 'come', 'take',
            'year', 'him', 'them', 'some', 'want', 'how', 'when', 'now',
            'like', 'our', 'into', 'here', 'then', 'than', 'look', 'way',
            'more', 'no', 'yes', 'well', 'also', 'two', 'use', 'tell', 'good',
            'man', 'day', 'find', 'give', 'more', 'new'
        ]
        words += [word.upper() for word in words]
    assert words
    while True:
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.curs_set(False)
        stdscr.clear()
        while True:
            c = stdscr.getch()
            if c == 27:  # ESC
                return
            if c == 32:  # SPACE
                break
        word = random.choice(words)
        done_length = 0
        word_start_time = time.time()
        while done_length < len(word):
            stdscr.clear()
            # draw
            lines, done_width = ascii_art(word, done_length, args.font_size,
                                          args.square_font, scr_width)
            for i, line in enumerate(lines):
                stdscr.addstr((scr_height - len(lines)) // 2 + i,
                              (scr_width - len(line)) // 2, line[:done_width],
                              curses.color_pair(2))
                stdscr.addstr((scr_height - len(lines)) // 2 + i,
                              (scr_width - len(line)) // 2 + done_width,
                              line[done_width:], curses.color_pair(3))
            # get input
            c = stdscr.getch()
            if c == 27:  # ESC
                return
            if chr(c).upper() == word[done_length].upper():
                done_length += 1
            else:
                stdscr.clear()
                stdscr.refresh()
                time.sleep(2)
                curses.flushinp()
        duration = time.time() - word_start_time
        stdscr.clear()
        curses.endwin()
        proc = subprocess.Popen(
            ['mplayer', random.choice(sounds)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        if duration < 1 * len(word):
            subprocess.check_call(['sl', '-F'])
            subprocess.check_call(['sl', '-l', '-F'])
            subprocess.check_call(['sl', '-l', '-F'])
        elif duration < 2 * len(word):
            subprocess.check_call(['sl'])
            subprocess.check_call(['sl', '-l'])
            subprocess.check_call(['sl', '-l'])
        elif duration < 3 * len(word):
            subprocess.check_call(['sl'])
            subprocess.check_call(['sl', '-l'])
        else:
            subprocess.check_call(['sl'])
        proc.kill()
        stdscr = curses.initscr()
        curses.start_color()


if __name__ == '__main__':
    curses.wrapper(main)
