"""AI player using Monte Carlo Tree Search algorithm"""
from copy import deepcopy
from math import log, sqrt
from random import choice

from grid2048 import helpers
from grid2048.grid2048 import DIRECTION, Grid2048, MoveFactory
from players.player import AIPlayer


class Node:
    c = 1.41

    def __init__(self, grid: Grid2048, direction: DIRECTION, parent=None):
        self.grid = grid
        self.direction = direction
        self.visits = 1
        self.value = 0
        self.parent = parent
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def update(self, value):
        self.visits += 1
        self.value += value

    @property
    def depth(self):
        d = 0
        node = self
        while node.parent:
            d += 1
            node = node.parent
        return d

    @property  # added property to calculate UCT score for each child node
    def uct(self):  # UCT score calculation formula
        return (
            self.value / self.visits
            + self.c * sqrt(2 * log(self.parent.visits) / self.visits)
            # if self.visits
            # else 0
        )

    # @property  # added property to get the move associated with the node
    # def move(
    #     self,
    # ):  # loop through children and return the move associated with the node
    #     for move, child in self.children:
    #         if child == self:
    #             return move


class MCTSPlayer(AIPlayer):
    """AI player using Monte Carlo simulation"""

    max_depth = 100
    n_sim = 300
    c = 0.1

    def __init__(self, grid: Grid2048):
        super().__init__(grid)
        self.height = self.grid.height
        self.width = self.grid.width
        self.root = Node(grid, None)

    def play(self, *args, **kwargs) -> bool:
        move = MoveFactory.create(self.get_best_direction())
        return self.grid.move(move)

    def get_best_direction(self) -> DIRECTION:
        # self.expand(self.root)
        for _ in range(self.n_sim):
            self.search(self.root)
        # select the child node with the highest visit count
        best_child = max(self.root.children, key=lambda x: x.visits)
        self.root = best_child
        return self.root.direction

    def search(self, node):
        node = self.select(node)
        if node.depth < self.max_depth:
            child = self.expand(node)
            score = self.simulate(child)
        else:
            score = self.evaluate(node.grid)
        self.backpropagate(node, score)

    def select(self, node):
        """Traverse the tree using UCT to select the best child node to expand"""
        node = self.root
        while node.children:
            best_child = max(node.children, key=lambda x: x.uct)
            node = best_child
        return node

    def expand(self, node: Node):
        """Expand the node by adding a new child"""
        grid = deepcopy(node.grid)
        while True:
            direction = self.get_random_direction()
            move = grid.move(MoveFactory.create(direction), add_tile=True)
            if move or grid.no_moves:
                break
        child = Node(grid, direction, node)
        node.add_child(child)
        return child

    def simulate(self, node: Node):
        """Simulate the game from the node using a random playout policy"""
        grid = deepcopy(node.grid)
        while not grid.no_moves:
            move = self.get_random_direction()
            grid.move(MoveFactory.create(move), add_tile=True)
        return self.evaluate(grid)

    def backpropagate(self, node: Node, score):
        """Backpropagate the score to update the information in the tree"""
        while node:
            node.update(score)
            # node.uct = node.score / node.visits + self.c * sqrt(
            #     2 * log(node.parent.visits) / node.visits
            # )
            node = node.parent

    # def get_best_move(self):
    #     """Return the move that corresponds to the child node with the highest UCT"""
    #     return max(self.root.children, key=lambda x: x.uct).move

    def get_random_direction(self):
        """Return a random move from all possible moves"""
        directions = list(DIRECTION)
        return choice(directions)

    def evaluate(self, grid):
        """Return the score of the grid"""
        maxi = helpers.max_tile(grid)
        high_val = maxi // 4 if maxi > 256 else 256
        score = grid.last_move.score
        val = [
            0.5 * score,
            # (0.01 * helpers.shift_score(grid) + 0.001 * grid.score) / 2,
            # 0.1 * helpers.grid_sum(grid),
            2 * helpers.zeros(grid),
            # 0.2 * helpers.pairs(grid) * helpers.monotonicity(grid),
            # # 2 / (helpers.smoothness(grid) + 1),
            # # 0.01 * helpers.max_tile(grid),
            # # helpers.zero_field(grid) * helpers.max_tile(grid),
            # helpers.monotonicity(grid),
            helpers.higher_on_edge(grid),
            # 2 * helpers.high_vals_on_edge(grid, high_val),
            # 4 * helpers.low_to_high(grid, 256),
        ]
        # print(val)
        return sum(val)
