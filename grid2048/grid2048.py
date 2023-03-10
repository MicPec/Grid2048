import itertools
from copy import deepcopy
from enum import Enum
from random import choice, choices
from typing import Callable, TypeVar

STATE = Enum("STATE", "IDLE RUNNING")
DIRECTION = Enum("DIRECTION", "UP DOWN LEFT RIGHT")

Grid2048 = TypeVar("Grid2048")
Move = TypeVar("Move")


class Grid2048:
    """2048 grid class"""

    def __init__(self, width=4, height=4):
        self.state = STATE.IDLE
        self._last_move = None
        self.width = width
        self.height = height
        self.reset()

    def __str__(self):
        # Find the length of the longest number
        val = 0
        for row in self._grid:
            val = max(row) if max(row) > val else val
        # Create the string
        l = len(str(val))
        s = "\n" + "-" * (l + 1) * self.width + "-\n"
        for row in self._grid:
            s += "|"
            for col in row:
                strcol = str(col).center(l) if col > 0 else " "
                s += f"{strcol:{l}}|"
            s += "\n" + "-" * (l + 1) * self.width + "-\n"
        return s

    def __repr__(self):
        return f"Grid2048({self.width}, {self.height}): {self._grid}"

    def __getitem__(self, key):
        return self._grid[key]

    def __setitem__(self, key, value):
        self._grid[key] = value

    def __eq__(self, other):
        return self._grid == other._grid

    @property
    def data(self) -> list[list[int]]:
        return self._grid

    @property
    def last_move(self) -> Move:
        if self._last_move is None:
            raise ValueError("No move has been made yet")
        return self._last_move

    @data.setter
    def data(self, value: list[list[int]]) -> None:
        if not all(isinstance(row, list) for row in value):
            raise TypeError("Grid data must be a list of lists of integers")
        if len(value) != self.height or len(value[0]) != self.width:
            raise ValueError(
                f"Invalid grid dimensions:{self.width}x{self.height} != {len(value)}x{len(value[0])}"
            )
        self._grid = value

    def reset(self) -> None:
        """Reset the grid"""
        self._grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.moves = 0
        self.add_random_tile(self.get_empty_fields())
        self.state = STATE.IDLE

    def get_empty_fields(self) -> list[tuple[int, int]]:
        """Return a list of tuples containing the coordinates of empty fields"""
        return [
            (row, col)
            for row, col in itertools.product(range(self.height), range(self.width))
            if self._grid[row][col] == 0
        ]

    def add_random_tile(self, empty_fields: list) -> None:
        """Add a random tile to the grid"""
        if empty_fields:
            row, col = choice(empty_fields)
            self._grid[row][col] = choices([2, 4], [0.9, 0.1])[0]

    @property
    def no_moves(self) -> bool:
        """Check if there are any moves left"""
        for col, row in itertools.product(range(self.width), range(self.height)):
            if self._grid[row][col] == 0:
                return False
            if (
                row < self.height - 1
                and self._grid[row][col] == self._grid[row + 1][col]
            ):
                return False
            if (
                col < self.width - 1
                and self._grid[row][col] == self._grid[row][col + 1]
            ):
                return False
        return True

    def move(self, move: Move, add_tile: bool = True) -> bool:
        """Execute a move and return True if the move is valid."""
        if self.state == STATE.RUNNING or self.no_moves:
            return False
        self.state = STATE.RUNNING
        move(self)
        self._last_move = move
        self.score += move.score
        if move.is_valid:
            self.moves += 1
            if add_tile:
                self.add_random_tile(self.get_empty_fields())
        self.state = STATE.IDLE
        return move.is_valid


class Move:
    """Move class. Makes a move in a given direction."""

    def __init__(self, direction, dir_fn: Callable):
        self._direction = direction
        self.score = 0
        self.dir_fn = dir_fn
        self._called = False
        self._is_valid = False

    def __call__(self, grid: Grid2048) -> Grid2048:
        """Execute the move"""
        cmp = deepcopy(grid.data)
        self.dir_fn(self, grid)
        self._called = True
        # It`s done this way, because I could not find a better/faster way to do it.
        self._is_valid = grid.data != cmp
        return grid

    @property
    def direction(self) -> DIRECTION:
        """Return the direction of the move"""
        return self._direction

    @property
    def is_valid(self) -> bool:
        """Return True if the move is valid. Call after the move has been executed."""
        if not self._called:
            raise ValueError("Move has not been called yet")
        return self._is_valid

    def shift_up(self, grid: Grid2048) -> Grid2048:
        """Shift the grid up combining tiles"""
        matrix = grid.data
        for col in range(len(matrix[0])):
            # Create a temporary list to store the non-zero tiles
            temp = [
                matrix[row][col] for row in range(len(matrix)) if matrix[row][col] != 0
            ]
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the column
            for i in range(len(matrix)):
                matrix[i][col] = 0
            j = 0
            for row in range(len(matrix)):
                if j < len(temp) and temp[j] != 0:
                    matrix[row][col] = temp[j]
                    j += 1
        return grid

    def shift_down(self, grid: Grid2048) -> Grid2048:
        """Shift the grid down combining tiles"""
        matrix = grid.data
        for col in range(len(matrix[0])):
            # Create a temporary list to store the non-zero tiles
            temp = [
                matrix[row][col]
                for row in range(len(matrix) - 1, -1, -1)
                if matrix[row][col] != 0
            ]
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the column
            for k in range(len(matrix)):
                matrix[k][col] = 0
            j = 0
            for row in range(len(matrix) - 1, -1, -1):
                if j < len(temp) and temp[j] != 0:
                    matrix[row][col] = temp[j]
                    j += 1
        return grid

    def shift_left(self, grid: Grid2048) -> Grid2048:
        """Shift the grid left combining tiles"""
        matrix = grid.data
        for row in range(len(matrix)):
            # Create a temporary list to store the non-zero tiles
            temp = [
                matrix[row][col]
                for col in range(len(matrix[0]))
                if matrix[row][col] != 0
            ]
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the row
            for k in range(len(matrix[0])):
                matrix[row][k] = 0
            j = 0
            for col in range(len(matrix[0])):
                if j < len(temp) and temp[j] != 0:
                    matrix[row][col] = temp[j]
                    j += 1
        return grid

    def shift_right(self, grid: Grid2048) -> Grid2048:
        """Shift the grid right combining tiles"""
        matrix = grid.data
        for row in range(len(matrix)):
            # Create a temporary list to store the non-zero tiles
            temp = [
                matrix[row][col]
                for col in range(len(matrix[0]) - 1, -1, -1)
                if matrix[row][col] != 0
            ]
            # Combine the tiles
            self.score += self.combine_tiles(temp)
            # Rebuild the row
            for k in range(len(matrix[0])):
                matrix[row][k] = 0
            j = 0
            for col in range(len(matrix[0]) - 1, -1, -1):
                if j < len(temp) and temp[j] != 0:
                    matrix[row][col] = temp[j]
                    j += 1
        return grid

    def combine_tiles(self, temp: list[int]) -> int:
        """Combine the tiles and count the score"""
        i = 0
        score = 0
        while i < len(temp) - 1:
            if temp[i] == temp[i + 1]:
                temp[i] *= 2
                temp.pop(i + 1)
                score += temp[i]
            i += 1
        return score


class MoveFactory:
    """Factory class for creating Move objects"""

    move_directions = {
        "UP": Move.shift_up,
        "DOWN": Move.shift_down,
        "LEFT": Move.shift_left,
        "RIGHT": Move.shift_right,
    }

    def __init__(self, grid):
        self.grid = grid.data

    @classmethod
    def create(cls, direction: DIRECTION):
        try:
            return Move(direction, cls.move_directions[direction.name])
        except KeyError:
            raise ValueError("Invalid direction")
        except Exception as e:
            raise e
