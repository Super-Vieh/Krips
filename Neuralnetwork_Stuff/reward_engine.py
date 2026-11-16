import numpy as np

from Klassen import Game
#print_bot, print_sidesplus, print_top
from .game_engine_encoder import GameEngineEncoder

class RewardEngine():

    @staticmethod
    def reward(game:Game, previous_state:np.ndarray | None, before_previous_state:np.ndarray | None = None) -> float:
        reward: float = 0
        #[0] and [1] if current state are list with the cards of player1 and player2
        #[2] and [3] are the lists of the playing field 3 is the list with the sidelists and 4 is the list with the centerlists
        #every ellement in the tuple is a list of lists
        current_state: np.ndarray = GameEngineEncoder.encode_states(game)
        if previous_state is None:
            return reward
        if not RewardEngine.did_an_action_do_something(previous_state, current_state):reward-=5#; print("action did something")
        if RewardEngine.punish_back_and_forth(before_previous_state, current_state): reward-=5#; print("back and forth punished")
        if RewardEngine.put_card_in_the_middel(previous_state, current_state): reward+=3 #; print("card in the middel")
        if RewardEngine.card_fromplayer_toboard(game,previous_state, current_state): reward+=10 #; print("card from player to board")
        if RewardEngine.did_end_move(game,previous_state, current_state): reward=1#; print("did end move")
        if RewardEngine.count_additional_spaces(previous_state, current_state): reward += RewardEngine.count_additional_spaces(previous_state, current_state)*0.15#;print("created space")
        #print(f"the reward is {reward}")
        #if reward> 0:
        #    print_top(game)
        #    print_sidesplus(game)
        #    print_bot(game)
        return reward

    #first only this function to test if the nn can atleast do leagal moves
    @staticmethod
    def did_an_action_do_something(previous_state:np.ndarray, current_state:np.ndarray)->bool:
        a_card_opened_or_closed: bool = False

        if np.array_equal(current_state, previous_state):
            return False

        else:
            return True

    @staticmethod
    def punish_back_and_forth(before_previous_state:np.ndarray | None, current_state:np.ndarray)->bool:
        # if the state is the same after 2 moves it means that the agent just shifted the cards
        # something similar might happen after 4 moves
        if before_previous_state is None:
            return False
        if np.array_equal(current_state, before_previous_state):
            return True
        return False
    @staticmethod
    def put_card_in_the_middel(previous_state:np.ndarray, current_state:np.ndarray)->bool:
        # the middel list are supposed to be the last 8 list in the state tensor
        if not np.array_equal(current_state[728:1144], previous_state[728:1144]):
            return True
        return False
    @staticmethod
    def card_fromplayer_toboard(game:Game, previous_state:np.ndarray, current_state:np.ndarray)->bool:
        player1_cards_changed: bool = not np.array_equal(current_state[0:156], previous_state[0:156])
        player2_cards_changed: bool = not np.array_equal(current_state[156:312], previous_state[156:312])
        side_cards_changed: bool = not np.array_equal(current_state[312:728], previous_state[312:728])

        if game.current_player is not None and game.current_player.player_number == 1:
            if player1_cards_changed and side_cards_changed:
                return True

        if game.current_player is not None and game.current_player.player_number == 2:
            if player2_cards_changed and side_cards_changed:
                return True
        return False

    @staticmethod
    def did_end_move(game:Game, previous_state:np.ndarray, current_state:np.ndarray) -> bool:
        player1_put_card: bool = (np.sum(current_state[0:52]) == np.sum(previous_state[0:52]) - 1)
        player2_put_card: bool = (np.sum(current_state[156:208]) == np.sum(previous_state[156:208]) - 1)
        #wenn der Spielerhaufen um eine karte weniger hat als letzen spielzug
        player1_stock_got_card: bool = (np.sum(current_state[52:104]) + 1 == np.sum(previous_state[52:104]))
        player2_stock_got_card: bool = (np.sum(current_state[208:260]) + 1 == np.sum(previous_state[208:260]))

        if game.current_player is not None and game.current_player.player_number ==1:
            if player1_put_card and player1_stock_got_card:
                return True
        if game.current_player is not None and game.current_player.player_number ==2:
            if player2_put_card and player2_stock_got_card:
                return True
        return False

    @staticmethod
    def count_created_spaces(state:np.ndarray)->int:
        #[312:728] are bits for the side spaces.
        # Counts all the all bits. if there are no bit meaning no cards it will be counted as one free space
        x: int = 312
        count_of_spaces: int = 0
        for i in range(0,8):
            if np.sum(state[x+i*52:x+(i+1)*52])==0:
                count_of_spaces +=1
        return count_of_spaces
    @staticmethod
    def count_additional_spaces(previous_state:np.ndarray, current_state:np.ndarray)->int:
        space_last_move: int = RewardEngine.count_created_spaces(previous_state)
        space_current_move: int = RewardEngine.count_created_spaces(current_state)

        if space_last_move == space_current_move:
            return 0
        if space_current_move> space_last_move:
            return space_current_move - space_last_move
        else:
            return 0
