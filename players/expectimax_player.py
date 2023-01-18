"""AI player using Expectimax algorithm"""
from copy import deepcopy
from random import choice, shuffle

from grid2048 import helpers
from grid2048.grid2048 import MOVES, Grid2048, MoveFactory
from players.player import AIPlayer


class ExpectimaxPlayer(AIPlayer):
    """AI player using Expectimax algorithm""" ""

    # dirs = ["l", "u", "d", "r"]
    depth = 5

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        # self.moves = {
        #     "u": self.grid.shift_up,
        #     "d": self.grid.shift_down,
        #     "l": self.grid.shift_left,
        #     "r": self.grid.shift_right,
        # }

    def play(self, *args, **kwargs) -> bool:
        move = MoveFactory.create(self.get_best_move(self.grid))
        return self.grid.move(move)

    def get_best_move(self, grid):
        best_value = float("-inf")
        best_move = None

        for direction in MOVES:
            new_grid = deepcopy(grid)
            move = MoveFactory.create(direction)
            moved = new_grid.move(move, add_tile=True)
            if new_grid.no_moves:
                return direction
            if not moved:
                continue
            value = self.expectimax(new_grid, move, self.depth, "ai")
            if value > best_value:
                best_value = value
                best_move = direction
        return best_move

    def expectimax(self, grid, move, depth, player):
        if depth == 0 or grid.no_moves:
            return self.evaluate(grid, move)
        if player == "ai":
            best_value = float("-inf")
            for direction in MOVES:
                new_grid = deepcopy(grid)
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                # if not moved:
                #     continue
                value = self.expectimax(new_grid, move, depth - 1, "random")
                best_value = max(best_value, value)
            return best_value
        else:
            # random player
            values = []
            for direction in MOVES:
                new_grid = deepcopy(grid)
                # new_grid.add_random_tile(new_grid.get_empty_fields())
                direction = choice(list(MOVES))
                move = MoveFactory.create(direction)
                moved = new_grid.move(move, add_tile=True)
                # if not moved:
                #     continue
                values.append(self.expectimax(new_grid, None, depth - 1, "ai"))
            return sum(values) / len(values)

    def evaluate(self, grid, move=None):
        """Return the score of the grid"""
        maxi = helpers.max_tile(grid)
        move_score = move.score if move else 0

        val = [
            0.1 * move_score,
            # (0.01 * helpers.shift_score(grid) + 0.001 * grid.score) / 2,
            # 0.1 * helpers.grid_sum(grid),
            0.1 * grid.score,
            0.4 * helpers.zeros(grid),
            0.2 * helpers.pairs(grid),
            # 1.25 / (helpers.smoothness(grid) + 1),
            # 0.01 * helpers.max_tile(grid),
            # 0.005 * helpers.zero_field(grid) * helpers.max_tile(grid),
            0.001 * helpers.monotonicity(grid),
            helpers.high_vals_on_edge(grid, 512),
        ]
        print(val)
        return sum(val)
