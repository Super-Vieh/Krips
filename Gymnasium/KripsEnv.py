
import os
import sys

import gymnasium
import numpy as np
from gymnasium import spaces

from Klassen.game import Game
from Klassen.game_orchestor import GameOrchestor
from Klassen.move import DestinationType, Move, OriginType
from Neuralnetwork_Stuff import GameEngineEncoder, RewardEngine, Recorder

def build_action_list() -> list[Move]:
    moves: list[Move] = [
        Move(OriginType.PLAYER, 0, DestinationType.PLAYER, 0),
        Move(OriginType.PLAYER, 0, DestinationType.PLAYER, 1),
        Move(OriginType.PLAYER, 2, DestinationType.PLAYER, 2),
    ]
    for origin in range(3):
        for destination in range(8):
            moves.append(
                Move(OriginType.PLAYER, origin, DestinationType.TABLEAU, destination)
            )
            moves.append(
                Move(OriginType.PLAYER, origin, DestinationType.FOUNDATION, destination)
            )
        moves.append(Move(OriginType.PLAYER, origin, DestinationType.OPPONENT, 0))
    for origin in range(8):
        for destination in range(8):
            moves.append(
                Move(OriginType.TABLEAU, origin, DestinationType.TABLEAU, destination)
            )
            moves.append(
                Move(OriginType.TABLEAU, origin, DestinationType.FOUNDATION, destination)
            )
        moves.append(Move(OriginType.TABLEAU, origin, DestinationType.OPPONENT, 0))
    return moves


ACTION_LIST: list[Move] = build_action_list()
ACTION_COUNT: int = len(ACTION_LIST)


class KripsEnv(gymnasium.Env):

    def __init__(self, render_mode: str | None = None):
        super().__init__()
        self.render_mode: str | None = render_mode
        self.game: Game | None = None
        self.recorder: Recorder | None = None
        self.previous_state: np.ndarray | None = None
        self.before_previous_state: np.ndarray | None = None
        self.oponnent_agent = None
        self.action_space: spaces.Discrete = spaces.Discrete(ACTION_COUNT)
        self.observation_space: spaces.MultiBinary = spaces.MultiBinary(1144)
        self.move_history=[]

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        while True:
            game_seed = int(self.np_random.integers(0, 2 ** 32 - 1))
            orchestrator = GameOrchestor(game_seed)
            self.game = orchestrator.set_up_game()
            if self.game.current_player is not None:
                break
        self.game_seed = game_seed
        self.move_history = []
        self.recorder = Recorder(self.game)
        self.previous_state = GameEngineEncoder.encode_states(self.game)
        self.before_previous_state = None
        return self._observe(), self._info()

    def step(self, move: Move, off_turn: bool):
        if self.game is None or not self.game.is_running:
            raise RuntimeError("step() called on a finished or uninitialized game")
        if off_turn:
            legal_moves = self.game.rules.get_legal_moves_when_not_playing()
        else:
            legal_moves = self.game.rules.get_all_legal_moves()
        if move in legal_moves:
            if off_turn:
                self.game.play_move_off_turn(move)
            else:
                self.game.play_move(move)
            self.move_history.append(move)
        observation = self._observe()
        reward = self._reward()
        terminated = self._terminated()
        truncated = self._truncated()
        info = self._info()
        self.recorder.add_state()
        self.before_previous_state = self.previous_state
        self.previous_state = observation

        return (observation,reward,terminated,truncated,info)

    def _observe(self) -> np.ndarray:
        return GameEngineEncoder.encode_states(self.game)

    def _reward(self):
        return RewardEngine.reward(
            self.game, self.previous_state, self.before_previous_state
        )

    def _terminated(self):
        return not self.game.is_running
    def _truncated(self):
        return False
    def _info(self)-> dict:
        player = (
            self.game.current_player.player_number
            if self.game.current_player is not None
            else None
        )
        information :dict ={
            "legal_moves":self.legal_moves(),
            "player":player
        }
        return information
    def legal_moves(self, off_turn: bool | None = None)->list[Move]:
        if self.game is None or not self.game.is_running:
            return []
        if off_turn is None:
            off_turn = bool(self.game.is_krips)
        if not off_turn:
            return self.game.rules.get_all_legal_moves()
        if  off_turn:
            return self.game.rules.get_legal_moves_when_not_playing()
    def action_to_move(self, action: int) -> Move:
        if not 0 <= action < ACTION_COUNT:
            raise ValueError(f"Invalid action: {action}")
        return ACTION_LIST[action]

    def render(self):
        if self.game is None or getattr(self, "game_seed", None) is None:
            return None
        ui_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "UI")
        if ui_dir not in sys.path:
            sys.path.insert(0, ui_dir)
        from ui_game_replay import play_replay

        start_game = GameOrchestor(self.game_seed).set_up_game()
        return play_replay(start_game, list(self.move_history), seed=self.game_seed)

    def close(self):
        self.game = None
        self.recorder = None
        self.previous_state = None
        self.before_previous_state = None
        self.oponnent_agent = None
