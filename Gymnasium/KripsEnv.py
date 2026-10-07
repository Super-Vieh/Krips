
import random
import gymnasium
import numpy as np
from gymnasium import spaces

from Klassen import SpielInitialisierer
from Klassen.spiel import Spiel
from .random_bot import RandomBot


class KripsEnv(gymnasium.Env):

    def __init__(self):
        self.game = None
        self.oponnent_agent = None
        self.action_space: spaces.MultiDiscrete = spaces.MultiDiscrete([12, 21])

    def reset(self):
        self.game = SpielInitialisierer.initialize_game_for_play()


    def step(self,move:str,off_turn:bool):
        #move: Move = self.action_to_move(action)
        if not off_turn:
            self.game.play_nn(move)
        elif off_turn:
            self.game.play_move_off_turn(move)

    def _agent_player(self):
        pass

    def _observe(self):
        pass

    def _reward(self):
        pass

    def _terminated(self):
        pass

    def _info(self):
        pass
    '''
    def action_to_move(self, action: np.ndarray) -> Move:

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
    '''
    def render(self):
        pass

    def close(self):
        pass
