import numpy as np
import torch as T
from Klassen import Game
from .game_engine_encoder import GameEngineEncoder
#from Klassen import print_top,print_sidesplus,print_bot
class Recorder:
    def __init__(self,game:Game) -> None:
        self.game: Game = game
        self.all_states: list[np.ndarray] = [GameEngineEncoder.encode_states(self.game)]

    def add_state(self):
        self.all_states.append(GameEngineEncoder.encode_states(self.game))
"""
    def create_transition(self) -> tuple[T.Tensor, tuple[T.Tensor, T.Tensor], float, T.Tensor, bool]:
        #this function creates small packages moves with its consequences
        state: T.Tensor = self.last_state
        # state is the last state that was stored before an action was taken
        next_state: T.Tensor = self.initialize_states(self.game)
        # next_state is the current state after the action was taken
        (action1,action2) = self.initialize_actions()
        reward: float = self.reward()
        done: bool = self.done()
        transition: tuple[T.Tensor, tuple[T.Tensor, T.Tensor], float, T.Tensor, bool] = (state,(action1,action2),reward,next_state,done)
        self.last_state = next_state
        return transition
"""

