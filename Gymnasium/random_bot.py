import random

from Klassen.game import Game
from Klassen.move import Move


class RandomBot:


    def __init__(self, seed: int ):
        self.rng: random.Random = random.Random(seed)

    def act(self, game: Game) -> Move:
        legal_moves: list[Move] = game.rules.get_all_valid_moves()
        return self.rng.choice(legal_moves)

    def act_off_turn(self, game: Game) -> Move:
        legal_moves = game.rules.get_valid_moves_when_not_playing()
        return self.rng.choice(legal_moves)