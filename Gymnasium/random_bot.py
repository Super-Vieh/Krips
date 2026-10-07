import random

from Klassen.spiel import Spiel


class RandomBot:


    def __init__(self, seed: int ):
        self.rng: random.Random = random.Random(seed)

    def act(self, game: Spiel):
        all_moves: list[str] = game.all_moves()
        return self.rng.choice(all_moves)

    def act_off_turn(self) -> str:
        return self.rng.choice(["K0K0","H0H0"])# H0H0 is a temporary value it is not legal so in practice it skips the move