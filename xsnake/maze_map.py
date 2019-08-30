#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List
import random


class MazeMap:

    def __init__(self, x_size: int, y_size: int, has_wall: bool) -> None:
        assert x_size >= 2
        assert y_size >= 2
        self._x_size = x_size
        self._y_size = y_size
        self._is_connected_to_next_x = [
            [True] * y_size for i in range(x_size - 1)
        ]
        self._is_connected_to_next_y = [
            [True] * (y_size - 1) for i in range(x_size)
        ]
        if not has_wall:
            return
        is_connected_to_next = (self._is_connected_to_next_x,
                                self._is_connected_to_next_y)
        for i in range((x_size - 1) * (y_size - 1)):
            while True:
                rand_dir = random.randint(0, 1)
                if rand_dir == 0:
                    rand_x = random.randint(0, self._x_size - 2)
                    rand_y = random.randint(0, self._y_size - 1)
                else:
                    rand_x = random.randint(0, self._x_size - 1)
                    rand_y = random.randint(0, self._y_size - 2)
                if not is_connected_to_next[rand_dir][rand_x][rand_y]:
                    continue
                is_connected_to_next[rand_dir][rand_x][rand_y] = False
                if self._is_connected():
                    break
                is_connected_to_next[rand_dir][rand_x][rand_y] = True

    @staticmethod
    def directions() -> List[Tuple[int, int]]:
        return [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def is_connected(self, pos: Tuple[int, int],
                     direction: Tuple[int, int]) -> bool:
        x = pos[0]
        y = pos[1]
        if direction == (1, 0):
            if x + 1 == self._x_size:
                return False
            return self._is_connected_to_next_x[x][y]
        if direction == (-1, 0):
            if x == 0:
                return False
            return self._is_connected_to_next_x[x - 1][y]
        if direction == (0, 1):
            if y + 1 == self._y_size:
                return False
            return self._is_connected_to_next_y[x][y]
        if direction == (0, -1):
            if y == 0:
                return False
            return self._is_connected_to_next_y[x][y - 1]
        assert False

    def x_size(self) -> int:
        return self._x_size

    def y_size(self) -> int:
        return self._y_size

    def _is_connected(self) -> bool:
        visited = [[False] * self._y_size for i in range(self._x_size)]
        self._visit(visited, 0, 0)
        for x in range(self._x_size):
            for y in range(self._y_size):
                if not visited[x][y]:
                    return False
        return True

    def _visit(self, visited, x, y) -> None:
        if visited[x][y]:
            return
        visited[x][y] = True
        for dir in self.directions():
            if self.is_connected((x, y), dir):
                self._visit(visited, x + dir[0], y + dir[1])


def main():
    mm = MazeMap(4, 6, has_wall=True)
    print('*-' * mm.x_size() + '*')
    for y in range(mm.y_size()):
        line = '|'
        for x in range(mm.x_size()):
            line += ' '
            line += ' ' if mm.is_connected((x, y), (1, 0)) else '|'
        print(line)
        line = '*'
        for x in range(mm.x_size()):
            line += ' ' if mm.is_connected((x, y), (0, 1)) else '-'
            line += '*'
        print(line)


if __name__ == '__main__':
    main()
