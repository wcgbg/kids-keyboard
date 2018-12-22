#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import glob
import curses
import hashlib
import subprocess
from gtts import gTTS
import os
from tendo import singleton
import time


class Player:
    _music_process = None
    _is_playing = False
    _music_files = None
    _music_index = 0

    def __init__(self, music_dir):
        self._music_files = glob.glob(music_dir + '/*.mp3')
        assert len(self._music_files) != 0

    def speak(self, text, lang, slow=False, block=False):
        self.pause_music()
        cache_dir = os.path.expanduser('~/.cache/kids-keyboard')
        os.makedirs(cache_dir, exist_ok=True)
        sha1 = hashlib.sha1()
        sha1.update(text.encode('utf-8'))
        sha1.update(b'\x00')
        sha1.update(lang.encode('utf-8'))
        if slow:
            sha1.update(b'\x01')
        else:
            sha1.update(b'\x00')
        mp3_path = os.path.join(cache_dir, sha1.hexdigest() + '.mp3')
        if not os.path.exists(mp3_path):
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(mp3_path)
        p = subprocess.Popen(['mplayer', mp3_path],
                             stderr=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL)
        if block:
            p.wait()

    def _music_path(self):
        return self._music_files[self._music_index]

    def music_name(self):
        return os.path.splitext(os.path.basename(self._music_path()))[0].replace('_', ' ')

    def play_music(self):
        if self._music_process:
            self._music_process.stdin.write(b'P')
            self._music_process.stdin.flush()
        else:
            self._music_process = subprocess.Popen(
                ['mplayer', '-loop', '0', self._music_path()],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
        self._is_playing = True

    def pause_music(self):
        if not self._is_playing:
            return
        if self._music_process:
            self._music_process.stdin.write(b' ')
            self._music_process.stdin.flush()
        self._is_playing = False

    def next_music(self):
        self._music_index = (self._music_index + 1) % len(self._music_files)
        if self._music_process:
            self._music_process.stdin.write(b'q')
            self._music_process.stdin.flush()
            self._music_process.wait()
            self._music_process = None

    def is_playing(self):
        return self._is_playing


def _get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--music_dir')
    args = parser.parse_args()
    assert args.music_dir
    assert os.path.isdir(args.music_dir)
    return args


def main(stdscr):
    args = _get_args()
    try:
        single_instance = singleton.SingleInstance()
    except singleton.SingleInstanceException:
        return
    subprocess.call(['killall', 'mplayer'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    player = Player(args.music_dir)
    lang = 'en'
    while True:
        c = stdscr.getch()
        stdscr.clear()
        stdscr.addstr(0, 0, str(c))
        if c >= ord('0') and c <= ord('9'):
            player.speak(chr(c), lang)
        elif c == ord('-'):
            if lang == 'en':
                lang = 'zh-cn'
                player.speak('中文', lang)
            else:
                lang = 'en'
                player.speak('English', lang)
        elif c == 10:  # ENTER
            if player.is_playing():
                player.next_music()
                player.speak('Play the next song.', 'en', block=True)
            else:
                player.speak('Play', 'en', block=True)
            time.sleep(0.05)
            player.speak(player.music_name(), 'en', block=True)
            time.sleep(0.05)
            player.play_music()
        elif c == 43:  # +
            player.speak('Stop', 'en')
            player.pause_music()
        elif c == ord('q'):
            break
        stdscr.refresh()


if __name__ == '__main__':
    curses.wrapper(main)
