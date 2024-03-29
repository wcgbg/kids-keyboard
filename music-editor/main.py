#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import argparse
import curses
import simpleaudio
import os
import time


def normalize(args, i, j):
    if j == -1:
        j = args.num_cols - 1
        i -= 1
    if j == args.num_cols:
        j = 0
        i += 1
    if i == -1:
        i = args.num_rows - 1
    if i == args.num_rows:
        i = 0
    return i, j


def main(stdscr):
    parser = argparse.ArgumentParser(description='Music Toy Editor')
    parser.add_argument('num_rows', type=int)
    parser.add_argument('num_cols', type=int)
    args = parser.parse_args()

    self_dir = os.path.dirname(os.path.realpath(__file__))
    key_to_wave = {}
    for key, filename in [('-', 'silence.wav'), ('D', 'note060-do.wav'),
                          ('R', 'note062-re.wav'), ('M', 'note064-mi.wav'),
                          ('F', 'note065-fa.wav'), ('S', 'note067-so.wav'),
                          ('L', 'note069-la.wav'), ('T', 'note071-ti.wav'),
                          ('d', 'note072-do.wav')]:
        key_to_wave[key] = simpleaudio.WaveObject.from_wave_file(
            self_dir + '/samples/katy/' + filename)

    scr_height, scr_width = stdscr.getmaxyx()
    music = [list('-' * args.num_cols) for i in range(args.num_rows)]
    cursor_i = 0
    cursor_j = 0
    tempos_bpms = [30, 36, 45, 60, 72, 90, 120, 144, 180]
    tempo_idx = 4
    is_playing = False
    player = None
    assert scr_height >= args.num_rows + 2
    assert scr_width >= args.num_cols + 2
    i0 = (scr_height - args.num_rows) // 2
    j0 = (scr_width - args.num_cols) // 2
    border = stdscr.derwin(args.num_rows + 2, args.num_cols + 2, i0 - 1,
                           j0 - 1)
    win = border.derwin(1, 1)

    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    while True:
        stdscr.clear()
        border.box()
        stdscr.addstr(i0 + args.num_rows + 1, j0, 'TEMPO:{}'.format(
            tempos_bpms[tempo_idx]))
        for i in range(args.num_rows):
            win.addstr(i, 0, ''.join(music[i]))
        if is_playing:
            win.addch(cursor_i, cursor_j, music[cursor_i][cursor_j],
                      curses.A_REVERSE)
        curses.curs_set(not is_playing)
        stdscr.move(i0 + cursor_i, j0 + cursor_j)
        stdscr.refresh()

        stdscr.nodelay(is_playing)
        if is_playing:
            if music[cursor_i][cursor_j] != '-':
                if player:
                    player.stop()
                player = key_to_wave[music[cursor_i][cursor_j]].play()
            time.sleep(60.0 / tempos_bpms[tempo_idx])
            c = stdscr.getch()
            if c == 27:  # ESC
                is_playing = False
                if player:
                    player.stop()
                player = None
                return
            if c == ord(' '):
                is_playing = False
                if player:
                    player.stop()
                player = None
                continue
            cursor_j += 1
            cursor_i, cursor_j = normalize(args, cursor_i, cursor_j)
        else:
            while True:
                c = stdscr.getch()
                if c == 27:  # ESC
                    return
                if c == curses.KEY_HOME:
                    cursor_j = 0
                    break
                if c == curses.KEY_END:
                    cursor_j = args.num_cols - 1
                    break
                if c == curses.KEY_LEFT:
                    cursor_j -= 1
                    cursor_i, cursor_j = normalize(args, cursor_i, cursor_j)
                    break
                if c == curses.KEY_BACKSPACE:
                    cursor_j -= 1
                    cursor_i, cursor_j = normalize(args, cursor_i, cursor_j)
                    music[cursor_i][cursor_j] = '-'
                    break
                if c == curses.KEY_RIGHT:
                    cursor_j += 1
                    cursor_i, cursor_j = normalize(args, cursor_i, cursor_j)
                    break
                if c == curses.KEY_UP:
                    cursor_i -= 1
                    cursor_i, cursor_j = normalize(args, cursor_i, cursor_j)
                    break
                if c == curses.KEY_DOWN:
                    cursor_i += 1
                    cursor_i, cursor_j = normalize(args, cursor_i, cursor_j)
                    break
                if c > 0 and c < 128 and chr(c) in key_to_wave:
                    music[cursor_i][cursor_j] = chr(c)
                    cursor_j += 1
                    cursor_i, cursor_j = normalize(args, cursor_i, cursor_j)
                    break
                if c == ord(' '):
                    is_playing = True
                    break
                if c == ord('['):
                    tempo_idx = max(0, tempo_idx - 1)
                    break
                if c == ord(']'):
                    tempo_idx = min(len(tempos_bpms) - 1, tempo_idx + 1)
                    break


if __name__ == '__main__':
    curses.wrapper(main)
