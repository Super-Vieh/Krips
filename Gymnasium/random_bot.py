import random

from Klassen.game import Game
from Klassen.move import Move


class RandomBot:


    def __init__(self, seed: int ):
        self.rng: random.Random = random.Random(seed)

    def act(self, legal_moves:list[Move]) -> Move:
        return self.rng.choice(legal_moves)

    def act_off_turn(self, legal_moves:list[Move]) -> Move:
        return self.rng.choice(legal_moves)