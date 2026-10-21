import random

import numpy as np
import torch as T

from Klassen import Spiel, SpielInitialisierer

from .legal_moves import legal_masks, legal_moves
from .storage import Storage


def _call_krips(game: Spiel) -> None:
    player = game.current
    paechen = game.spieler1Paechen if player.spielernummer == 1 else game.spieler2Paechen
    if paechen:
        game.play_off_turn("K0K0")
        return
    player.anderreihe = False
    player.gegenspieler.anderreihe = True
    game.current = player.gegenspieler
    game.wouldbeKrips = False


class GamePool:
    def __init__(
        self,
        num_games: int,
        base_seed: int = 0,
        storage: Storage | None = None,
    ) -> None:
        self.num_games: int = num_games
        self.base_seed: int = base_seed
        self.storage: Storage = storage if storage is not None else Storage()
        self.games: list[Spiel] = []
        self.reset(base_seed)

    def reset(self, base_seed: int | None = None) -> T.Tensor:
        if base_seed is not None:
            self.base_seed = base_seed
        self.games = []
        for index in range(self.num_games):
            random.seed(self.base_seed + index)
            self.games.append(SpielInitialisierer.initialize_game_for_play())
        return self.encode()

    def encode(self) -> T.Tensor:
        return self.storage.initialize_states_batch(self.games)

    def legal_moves(self) -> list[list[str]]:
        return [legal_moves(game) for game in self.games]

    def legal_masks(self) -> T.Tensor:
        return legal_masks(self.games)

    def current_players(self) -> np.ndarray:
        return np.array([game.current.spielernummer for game in self.games])

    def active(self) -> np.ndarray:
        return np.array([game.gameon for game in self.games])

    def active_indices(self) -> list[int]:
        return [index for index, game in enumerate(self.games) if game.gameon]

    def krips_available(self) -> np.ndarray:
        return np.array([bool(game.wouldbeKrips) for game in self.games])

    def step(
        self,
        actions: list[str | None],
    ) -> tuple[T.Tensor, np.ndarray, np.ndarray, np.ndarray]:
        rewards = np.zeros(self.num_games, dtype=np.float32)
        terminated = np.zeros(self.num_games, dtype=bool)

        for index, game in enumerate(self.games):
            if not game.gameon:
                terminated[index] = True
                continue
            action = actions[index] if index < len(actions) else None
            if action is None:
                raise ValueError(f"No action for active game {index}")
            player_number = game.current.spielernummer
            game.play_nn(action)
            game.game_ended()
            if not game.gameon:
                if game.winner == player_number:
                    rewards[index] = 1.0
                elif game.winner in (1, 2):
                    rewards[index] = -1.0
                terminated[index] = True

        return self.encode(), rewards, terminated, self.active()

    def step_off_turn(
        self,
        actions: list[str | None],
    ) -> tuple[T.Tensor, np.ndarray]:
        called = np.zeros(self.num_games, dtype=bool)

        for index, game in enumerate(self.games):
            if not game.gameon:
                continue
            action = actions[index] if index < len(actions) else None
            if action == "K0K0" and game.wouldbeKrips:
                _call_krips(game)
                game.game_ended()
                called[index] = True

        return self.encode(), called
