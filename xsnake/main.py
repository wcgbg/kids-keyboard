#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import glob
import os
import pygame
import random

MIN_MARGIN = 64


def gen_food_pos(snake_pos, map_size):
    while True:
        food_pos = (random.randint(0, map_size - 1),
                    random.randint(0, map_size - 1))
        if food_pos not in snake_pos:
            return food_pos


def load_food_imgs(size):
    self_dir = os.path.dirname(os.path.realpath(__file__))
    img_files = glob.glob(self_dir + '/food_img/*.png')
    assert img_files
    imgs = []
    for img_file in img_files:
        imgs.append(
            pygame.transform.scale(pygame.image.load(img_file), (size, size)))
    return imgs


def load_ending_img(size):
    self_dir = os.path.dirname(os.path.realpath(__file__))
    img_file = self_dir + '/ending.png'
    return pygame.transform.scale(pygame.image.load(img_file), (size, size))


def main():
    parser = argparse.ArgumentParser(description='Snake')
    parser.add_argument('--map_size', type=int, default=6)
    args = parser.parse_args()

    pygame.init()
    pygame.display.set_caption("Snake")
    pygame.mouse.set_visible(False)
    surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    surface_width, surface_height = surface.get_size()
    grid_size = (
        min(surface_width, surface_height) - MIN_MARGIN * 2) // args.map_size
    if grid_size % 2 == 0:
        grid_size -= 1  # make sure grid_size is odd
    assert grid_size > 0
    left = (surface_width - args.map_size * grid_size) // 2
    top = (surface_height - args.map_size * grid_size) // 2
    grid_color = pygame.Color(255, 255, 255)
    head_color = pygame.Color(100, 255, 100)
    body_color = pygame.Color(100, 200, 100)
    food_imgs = load_food_imgs(grid_size)
    ending_img = load_ending_img(min(surface_width, surface_height))
    snake_pos = [(args.map_size // 2, args.map_size // 2)] * 5
    food_pos = gen_food_pos(snake_pos, args.map_size)
    food_img = random.choice(food_imgs)
    is_ended = False
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            break
        delta = None
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_CTRL and event.key == pygame.K_q:
                break
            if event.key == pygame.K_LEFT:
                delta = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                delta = (1, 0)
            elif event.key == pygame.K_UP:
                delta = (0, -1)
            elif event.key == pygame.K_DOWN:
                delta = (0, 1)
        if is_ended:
            continue
        if delta:
            new_head_pos = (snake_pos[0][0] + delta[0],
                            snake_pos[0][1] + delta[1])
            if new_head_pos[0] < 0 or new_head_pos[0] >= args.map_size:
                continue
            if new_head_pos[1] < 0 or new_head_pos[1] >= args.map_size:
                continue
            for i in range(len(snake_pos) - 1, 0, -1):
                snake_pos[i] = snake_pos[i - 1]
            snake_pos[0] = new_head_pos
            if snake_pos[0] == food_pos:
                snake_pos.append(snake_pos[-1])
                if len(snake_pos) >= args.map_size * args.map_size // 2:
                    is_ended = True
                else:
                    food_pos = gen_food_pos(snake_pos, args.map_size)
                    food_img = random.choice(food_imgs)

        surface.fill(pygame.Color(0, 0, 0))

        if is_ended:
            assert surface_width >= surface_height
            surface.blit(ending_img, ((surface_width - surface_height) // 2, 0))
        else:
            pygame.draw.rect(
                surface, grid_color,
                pygame.Rect(left, top, args.map_size * grid_size + 1,
                            args.map_size * grid_size + 1), 4)
            for i in range(args.map_size + 1):
                pygame.draw.line(
                    surface, grid_color, (left + i * grid_size, top),
                    (left + i * grid_size, top + args.map_size * grid_size))
                pygame.draw.line(
                    surface, grid_color, (left, top + i * grid_size),
                    (left + args.map_size * grid_size, top + i * grid_size))

            for i, pos in reversed(list(enumerate(snake_pos))):
                if i == 0:  # head
                    radius = int(grid_size * 0.45)
                    color = head_color
                else:
                    radius = int(grid_size * 0.3)
                    color = body_color
                pygame.draw.circle(
                    surface, color,
                    (left + pos[0] * grid_size + grid_size // 2 + 1,
                     top + pos[1] * grid_size + grid_size // 2 + 1), radius)
            surface.blit(
                food_img,
                (left + food_pos[0] * grid_size, top + food_pos[1] * grid_size))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
