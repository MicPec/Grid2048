"""AI player using Expectimax algorithm"""
import math
from copy import deepcopy

from grid2048 import DIRECTION, Grid2048, Move, MoveFactory, helpers
from players import AIPlayer


class ExpectimaxPlayer(AIPlayer):
    """AI player using Expectimax algorithm""" ""

    depth = 4

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))  # type: ignore
        return self.grid.move(move)

    def get_best_move(self, grid):
        best_value = -math.inf
        best_move = None

        for direction in DIRECTION:
            new_grid = deepcopy(grid)
            move = MoveFactory.create(direction)
            moved = new_grid.move(move, add_tile=False)
            if not moved:
                continue
            value = self.expectimax(new_grid, self.depth, False)
            if value > best_value:
                best_value = value
                best_move = direction
        return best_move

    def expectimax(self, grid, depth, maximize):
        if depth == 0 or grid.no_moves:
            return self.evaluate(grid)
        if maximize is True:
            best_value = -math.inf
            # iterate over all possible moves
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                if new_grid.move(move, add_tile=False):
                    value = self.expectimax(new_grid, depth - 1, False)
                else:
                    continue
                best_value = max(best_value, value)
            return best_value
        else:
            # iterate over all empty fields and add a random tile
            values = []
            for _ in grid.get_empty_fields():
                grid.add_random_tile(grid.get_empty_fields())
                values.append(self.expectimax(grid, depth - 1, True))
            return sum(values) / len(values) if values else 0

    def evaluate(self, grid, move: Move | None = None):
        """Return the score of the grid"""
        zeros = helpers.zeros(grid) / (self.height * self.width)
        max_tile = helpers.max_tile(grid)
        high_on_edge = helpers.high_vals_on_edge(grid, max_tile // 2)
        val = [
            0.95 * math.log(high_on_edge if high_on_edge > 0 else 1),
            0.51 * helpers.monotonicity(grid),
            0.05 * helpers.smoothness(grid),
            zeros * math.log2(max_tile),
            grid.score / grid.moves if grid.moves > 0 else 0,
        ]
        # print(val)
        return sum(val)
