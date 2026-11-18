
import os
import sys

import gymnasium
import numpy as np
from gymnasium import spaces

from Klassen.game import Game
from Klassen.game_factory import GameFactory
from Klassen.move import DestinationType, Move, OriginType
from Neuralnetwork_Stuff import GameEngineEncoder, RewardEngine, Recorder



class KripsEnv(gymnasium.Env):

    def __init__(self):
        super().__init__()
        self.game: Game | None = None
        self.game_seed: int | None = None
        self.recorder: Recorder | None = None

        self.action_space: spaces.Discrete = spaces.Discrete(184)
        self.observation_space: spaces.MultiBinary = spaces.MultiBinary(1144)
        self.move_history=[]

    def reset(self, seed: int|None = None):
        super().reset(seed=seed)
        if seed is None:
            seed = int(self.np_random.integers(0, 2 ** 32 - 1))
        self.game_seed = seed
        factory = GameFactory()
        self.game = factory.set_up_game(seed)

        self.move_history = []
        self.recorder = Recorder(self.game)
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

        return (observation,reward,terminated,truncated,info)

    def _observe(self) -> np.ndarray:
        return GameEngineEncoder.encode_states(self.game)

    def _reward(self):
        return RewardEngine.reward(self.game, self.recorder)

    def _terminated(self):
        return not self.game.is_running
    def _truncated(self):
        return False
    def _info(self)-> dict:
        player_number = None
        if self.game and self.game.current_player:
            player_number = self.game.current_player.player_number
        information :dict ={
            "legal_moves":self.legal_moves(),
            "player_number":player_number
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

    def render(self):
        if self.game_seed is None:
            return None
        ui_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "UI")
        if ui_dir not in sys.path:
            sys.path.insert(0, ui_dir)
        from ui_game_replay import play_replay

        start_game = GameFactory().set_up_game(self.game_seed)
        return play_replay(start_game, list(self.move_history), seed=self.game_seed)

    def close(self):
        self.game = None
        self.recorder = None
        self.previous_state = None
        self.before_previous_state = None
        self.oponnent_agent = None
