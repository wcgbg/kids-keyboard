#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import glob
import os
import pygame
import random
import subprocess
import time

import maze_map

MIN_MARGIN = 32
PROGRESS_BAR_HEIGHT = 8
SELF_DIR = os.path.dirname(os.path.realpath(__file__))


class Game:

    def __init__(self, map_size: int, maze: bool, video_ending: bool, surface):
        self._map_size = map_size
        self._surface = surface
        self._video_ending = video_ending

        self._is_maze = maze
        self._maze_map = maze_map.MazeMap(map_size, map_size, maze)

        surface_width, surface_height = surface.get_size()
        assert surface_width >= surface_height
        self._grid_size = (
            surface_height - MIN_MARGIN * 2 - PROGRESS_BAR_HEIGHT) // map_size
        if self._grid_size % 2 == 0:
            self._grid_size -= 1  # make sure self._grid_size is odd
        assert self._grid_size > 0
        self._left = (surface_width - map_size * self._grid_size) // 2
        self._top = (surface_height -
                     map_size * self._grid_size) // 2 + PROGRESS_BAR_HEIGHT
        self._food_imgs = self._load_food_imgs()
        self._ending_img = self._load_ending_img()
        self._arrows_img = self._load_arrows_img()
        self._mplayer_proc = None
        self._snake_pos = [(map_size // 2, map_size // 2)] * 2
        self._food_pos = self._gen_food_pos()
        self._food_img = random.choice(self._food_imgs)
        self._is_ended = False
        self._ending_length = min(
            self._maze_map.x_size() * 2,
            self._maze_map.x_size() * self._maze_map.y_size() // 2)

        self._background_songs = glob.glob(SELF_DIR + '/bgmusic/*.mp3')
        assert self._background_songs
        random.shuffle(self._background_songs)
        self._play_background_music()

    def __del__(self):
        if self._mplayer_proc:
            self._mplayer_proc.kill()

    def _gen_food_pos(self):
        while True:
            food_pos = (random.randint(0,
                                       self._maze_map.x_size() - 1),
                        random.randint(0,
                                       self._maze_map.y_size() - 1))
            if food_pos not in self._snake_pos:
                return food_pos

    def _load_food_imgs(self):
        img_files = glob.glob(SELF_DIR + '/food_img/*.png')
        assert img_files
        imgs = []
        for img_file in img_files:
            imgs.append(
                pygame.transform.scale(
                    pygame.image.load(img_file),
                    (self._grid_size, self._grid_size)))
        return imgs

    def _load_ending_img(self):
        img_size = min(self._surface.get_size())
        return pygame.transform.scale(
            pygame.image.load(SELF_DIR + '/ending.png'), (img_size, img_size))

    def _load_arrows_img(self):
        return pygame.transform.scale(
            pygame.image.load(SELF_DIR + '/arrows.png'), (self._grid_size * 2, self._grid_size * 2))

    def _play_background_music(self):
        if self._is_ended:
            pygame.mixer.music.load(SELF_DIR + '/ending.mp3')
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.load(self._background_songs[0])
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
            self._background_songs = self._background_songs[1:] + [
                self._background_songs[0]
            ]

    def update(self, direction):
        if self._is_ended:
            return

        if direction:
            assert direction in self._maze_map.directions()

            if not self._maze_map.is_connected(self._snake_pos[0], direction):
                return
            new_head_pos = (self._snake_pos[0][0] + direction[0],
                            self._snake_pos[0][1] + direction[1])
            if new_head_pos == self._food_pos:
                self._snake_pos = [new_head_pos] + self._snake_pos
                if len(self._snake_pos) >= self._ending_length:
                    self._is_ended = True
                    if self._video_ending:
                        pygame.mixer.music.stop()
                        self._mplayer_proc = subprocess.Popen(
                            ['vlc', '-f', SELF_DIR + '/ending.mp4'])
                    else:
                        self._play_background_music()
                else:
                    self._food_pos = self._gen_food_pos()
                    self._food_img = random.choice(self._food_imgs)
                    self._play_background_music()
            else:
                self._snake_pos = [new_head_pos] + self._snake_pos[:-1]

        self._surface.fill(pygame.Color(0, 0, 0))

        if self._is_ended:
            surface_width, surface_height = self._surface.get_size()
            assert surface_width >= surface_height
            self._surface.blit(self._ending_img,
                               ((surface_width - surface_height) // 2, 0))
        else:
            grid_color = pygame.Color(
                20, 20, 20) if self._is_maze else pygame.Color(70, 70, 70)
            wall_color = pygame.Color(255, 255, 255)
            body_color = pygame.Color(
                80, 160, 80) if self._is_maze else pygame.Color(30, 60, 30)

            # progress bar
            progress_bar_length = self._surface.get_width() * len(
                self._snake_pos) // self._ending_length
            self._surface.fill(pygame.Color(100, 255, 100),
                               pygame.Rect(0, 0, progress_bar_length, PROGRESS_BAR_HEIGHT))

            for x in range(self._map_size + 1):
                pygame.draw.line(self._surface, grid_color,
                                 (self._left + x * self._grid_size, self._top),
                                 (self._left + x * self._grid_size,
                                  self._top + self._map_size * self._grid_size))
            for y in range(self._map_size + 1):
                pygame.draw.line(self._surface, grid_color,
                                 (self._left, self._top + y * self._grid_size),
                                 (self._left + self._map_size * self._grid_size,
                                  self._top + y * self._grid_size))
            for x in range(self._map_size + 1):
                for y in range(self._map_size):
                    if x == self._map_size or not self._maze_map.is_connected(
                            (x, y), (-1, 0)):
                        pygame.draw.line(
                            self._surface, wall_color,
                            (self._left + x * self._grid_size,
                             self._top + y * self._grid_size),
                            (self._left + x * self._grid_size,
                             self._top + (y + 1) * self._grid_size), 3)
            for y in range(self._map_size + 1):
                for x in range(self._map_size):
                    if y == self._map_size or not self._maze_map.is_connected(
                            (x, y), (0, -1)):
                        pygame.draw.line(
                            self._surface, wall_color,
                            (self._left + x * self._grid_size,
                             self._top + y * self._grid_size),
                            (self._left + (x + 1) * self._grid_size,
                             self._top + y * self._grid_size), 3)

            for i, pos in reversed(list(enumerate(self._snake_pos[1:]))):
                radius = int(self._grid_size * 0.3)
                pygame.draw.circle(
                    self._surface, body_color,
                    (self._left + pos[0] * self._grid_size +
                     self._grid_size // 2 + 1, self._top +
                     pos[1] * self._grid_size + self._grid_size // 2 + 1),
                    radius)

            self._surface.blit(
                self._food_img,
                (self._left + self._food_pos[0] * self._grid_size,
                 self._top + self._food_pos[1] * self._grid_size))

            self._surface.blit(
                self._arrows_img,
                (self._left + (self._snake_pos[0][0] - 0.5) * self._grid_size,
                 self._top + (self._snake_pos[0][1] - 0.5) * self._grid_size))

        pygame.display.flip()

    def is_ended(self) -> bool:
        return self._is_ended


def main():
    parser = argparse.ArgumentParser(description='Snake')
    parser.add_argument('--map_size', type=int, default=6)
    parser.add_argument('--maze', action='store_true')
    parser.add_argument('--video_ending', action='store_true')
    args = parser.parse_args()

    pygame.init()
    pygame.display.set_caption("Snake")
    pygame.mouse.set_visible(False)
    surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    game = Game(args.map_size, args.maze, args.video_ending, surface)

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            break
        direction = None
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_CTRL and event.key == pygame.K_q:
                break
            if event.key == pygame.K_SPACE and game.is_ended():
                del game
                args.map_size += 1
                game = Game(args.map_size, args.maze, args.video_ending,
                            surface)
                continue
            if event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
                direction = (-1, 0)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
                direction = (1, 0)
            elif event.key == pygame.K_UP or event.key == pygame.K_KP8:
                direction = (0, -1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                direction = (0, 1)
        game.update(direction)

    pygame.quit()


if __name__ == '__main__':
    main()
