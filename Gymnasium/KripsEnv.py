
import gymnasium
import numpy as np
from gymnasium import spaces

from Klassen.game import Game
from Klassen.gameorchestor import GameOrchestor
from Klassen.move import DestinationType, Move, OriginType
from Klassen.player import Player
from .observation import VECTOR_SIZE, encode_game
from .random_bot import RandomBot


class KripsEnv(gymnasium.Env):

    def __init__(self, render_mode: str | None = None):
        super().__init__()
        self.game: Game | None = None
        self.oponnent_agent = None
        self.render_mode: str | None = render_mode
        self.seed_value: int | None = None
        self.action_space: spaces.MultiDiscrete = spaces.MultiDiscrete([12, 21])
        self.observation_space: spaces.Box = spaces.Box(
            low=0.0, high=1.0, shape=(VECTOR_SIZE,), dtype=np.float32
        )

    def reset(self, seed: int | None = None, options: dict | None = None):
        generator = np.random.default_rng(seed)
        while True:
            game_seed = int(generator.integers(0, 2 ** 32))
            orchestrator = GameOrchestor(game_seed)
            game = orchestrator.set_up_game()
            if game.current_player is not None:
                break
        self.game = game
        self.seed_value = game_seed
        return self._observe(), self._info()

    def step(self, action):
        player_number = self.game.current_player.player_number
        move: Move = action if isinstance(action, Move) else self.action_to_move(action)
        if move is None:
            raise ValueError(f"Invalid action: {action}")
        self.game.play_move(move)
        terminated = self._terminated()
        off_turn = bool(self.game.is_krips) and not terminated
        return self._observe(), self._reward(player_number), terminated, False, self._info(off_turn)

    def step_off_turn(self, move: Move):
        self.game.play_move_off_turn(move)
        terminated = self._terminated()
        return self._observe(), terminated, self._info(False)

    def _agent_player(self) -> Player:
        return self.game.current_player

    def _observe(self) -> np.ndarray:
        return encode_game(self.game)

    def _reward(self, player_number: int) -> float:
        if self.game.is_running:
            return 0.0
        if self.game.player1.won:
            return 1.0 if player_number == 1 else -1.0
        if self.game.player2.won:
            return 1.0 if player_number == 2 else -1.0
        return 0.0

    def _terminated(self) -> bool:
        return not self.game.is_running

    def _info(self, off_turn: bool = False) -> dict:
        return {
            "player": self.game.current_player.player_number,
            "off_turn": off_turn,
            "seed": self.seed_value,
        }

    @staticmethod
    def action_to_move(action: np.ndarray) -> Move:

        n: int = action[0]
        m: int = action[1]
        # n 0 -> Krips
        if n == 0 :
            origin_type: OriginType = OriginType.KRIPS
            origin_value: int = 1
        # n 1 -> 8 Tableau
        elif 1 <= n <= 8:
            origin_type: OriginType = OriginType.TABLEAU
            origin_value: int = n - 1
        # n 9 -> 11 PlayerPacks
        elif 9 <= n <= 11:
            origin_type: OriginType = OriginType.PLAYER
            origin_value: int = n - 9
        else:
            return None

        #  (0 = K0, 1-8 = S1-S8, 9-16 = M1-M8, 17-19 = A0-A2, 20 = G0)
        if m == 0 :
            destination_type: DestinationType = DestinationType.KRIPS
            destination_value: int = 1
        elif 1 <= m <= 8:
            destination_type: DestinationType = DestinationType.TABLEAU
            destination_value: int = m - 1
        elif 9 <= m <= 16:
            destination_type: DestinationType = DestinationType.FOUNDATION
            destination_value: int = m - 9
        elif 17 <= m <= 19:
            destination_type: DestinationType = DestinationType.PLAYER
            destination_value: int = m - 17
        elif m == 20:
            destination_type: DestinationType = DestinationType.OPPONENT
            destination_value: int = 0
        else:
            return None

        return Move(origin_type, origin_value, destination_type, destination_value)

    def render(self):
        pass

    def close(self):
        pass
