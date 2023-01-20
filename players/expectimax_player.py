"""AI player using Expectimax algorithm"""
from copy import deepcopy
from math import sqrt
from random import choice

from grid2048 import helpers
from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class ExpectimaxPlayer(AIPlayer):
    """AI player using Expectimax algorithm""" ""

    depth = 4

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width

    def play(self) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))
        return self.grid.move(move)

    def get_best_move(self, grid):
        best_value = float("-inf")
        best_move = None

        for direction in DIRECTION:
            new_grid = deepcopy(grid)
            move = MoveFactory.create(direction)
            moved = new_grid.move(move, add_tile=True)
            if new_grid.no_moves:
                return direction
            value = self.expectimax(new_grid, self.depth, "ai")
            if not moved:
                continue
            if value > best_value:
                best_value = value
                best_move = direction
        return best_move

    def expectimax(self, grid, depth, player):
        if depth == 0 or grid.no_moves:
            return self.evaluate(grid)
        if player == "ai":
            best_value = float("-inf")
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                # if not moved:
                #     continue
                value = self.expectimax(new_grid, depth - 1, "random")
                best_value = max(best_value, value)
            return best_value
        else:
            # random player
            values = []
            for direction in DIRECTION:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                # if not moved:
                #     continue
                values.append(self.expectimax(new_grid, depth - 1, "ai"))
            return sum(values) / len(values)

    def evaluate(self, grid):
        """Return the score of the grid"""
        maxi = helpers.max_tile(grid)
        move_score = grid.last_move.score
        high_val = (sqrt(maxi) - 3) ** 2 if maxi > 512 else 512

        val = [
            1 * move_score,
            # (0.01 * helpers.shift_score(grid) + 0.001 * grid.score) / 2,
            # 0.1 * helpers.grid_sum(grid),
            1 * grid.score,
            32 * helpers.zeros(grid),
            0.4 * helpers.pairs(grid) * helpers.high_to_low(grid, 8),
            10 * helpers.low_to_high(grid, 64),
            # # 1.25 / (helpers.smoothness(grid) + 1),
            # # 0.01 * helpers.max_tile(grid),
            0.2 * helpers.zero_field(grid) * high_val,
            0.2 * helpers.monotonicity(grid),
            10 * helpers.high_vals_on_edge(grid, high_val),
        ]
        # print(val)
        return sum(val)
