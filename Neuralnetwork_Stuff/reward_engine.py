from Klassen import Spiel, print_bot, print_sidesplus, print_top
from Neuralnetwork_Stuff.storage import Storage
import torch as T

class RewardEngine():
    def __init__(self, game:Spiel,storage:Storage):
        self.game = game
        self.storage = storage

    def reward(self):
        reward = 0
        #[0] and [1] if current state are list with the cards of player1 and player2
        #[2] and [3] are the lists of the playing field 3 is the list with the sidelists and 4 is the list with the centerlists
        #every ellement in the tuple is a list of lists
        current_state= self.storage.initialize_states(self.game)
        self.storage.all_states.append(current_state)
        if self.did_an_action_do_something(): reward+=0.1#; print("action did something")
        if self.punish_back_and_forth(): reward-=0.2#; print("back and forth punished")
        if self.put_card_in_the_middel(): reward+=0.3 #; print("card in the middel")
        if self.card_fromplayer_toboard(): reward+=0.1 #; print("card from player to board")
        if self.did_end_move(): reward-=0.2#; print("did end move")
        if self.count_additional_spaces(): reward += self.count_additional_spaces()*0.1#;print("created space")
        #print(f"the reward is {reward}")
        #if reward> 0:
        #    print_top(self.game)
        #    print_sidesplus(self.game)
        #    print_bot(self.game)
        return reward

    #first only this function to test if the nn can atleast do leagal moves
    def did_an_action_do_something(self)->bool:
        a_card_opened_or_closed = False

        if self.storage.all_states and len(self.storage.all_states)>=2 and T.equal(self.storage.all_states[-1] ,self.storage.all_states[-2]):
            return False

        else:
            return True

    def punish_back_and_forth(self)->bool:
        # if the state is the same after 2 moves it means that the agent just shifted the cards
        # something similar might happen after 4 moves
        if self.storage.all_states and len(self.storage.all_states)==3:
            if T.equal(self.storage.all_states[-1] , self.storage.all_states[-3]):
                return True
        if  len(self.storage.all_states) ==5:
            if T.equal(self.storage.all_states[-1],self.storage.all_states[-5]):
                return True
        return False
    def put_card_in_the_middel(self)->bool:
        # the middel list are supposed to be the last 8 list in the state tensor
        if self.storage.all_states and len(self.storage.all_states)>=2:
            if not T.equal(self.storage.all_states[-1][728:1144], self.storage.all_states[-2][728:1144]):
                return True
        return False
    def card_fromplayer_toboard(self)->bool:
        player1_cards_changed= not T.equal(self.storage.all_states[-1][0:156], self.storage.all_states[-2][0:156])
        player2_cards_changed = not T.equal(self.storage.all_states[-1][156:312], self.storage.all_states[-2][156:312])
        side_cards_changed = not T.equal(self.storage.all_states[-1][312:728], self.storage.all_states[-2][312:728])

        if self.game.current.spielernummer == 1:
            if player1_cards_changed and side_cards_changed:
                return True

        if self.game.current.spielernummer == 2:
            if player2_cards_changed and side_cards_changed:
                return True
        return False

    def did_end_move(self):
        player1_put_card = (T.sum(self.storage.all_states[-1][0:52])== T.sum(self.storage.all_states[-2][0:52])-1)
        player2_put_card = (T.sum(self.storage.all_states[-1][156:208])== T.sum(self.storage.all_states[-2][156:208])-1)
        #wenn der Spielerhaufen um eine karte weniger hat als letzen spielzug
        player1_paeckchen_gotcard= (T.sum(self.storage.all_states[-1][52:104])+1== T.sum(self.storage.all_states[-2][52:104]))
        player2_paeckchen_gotcard= (T.sum(self.storage.all_states[-1][208:260])+1== T.sum(self.storage.all_states[-2][208:260]))

        if self.game.current.spielernummer ==1:
            if player1_put_card and player1_paeckchen_gotcard:
                return True
        if self.game.current.spielernummer ==2:
            if player2_put_card and player2_paeckchen_gotcard:
                return True
        return False

    def count_created_spaces(self,state:T.tensor)->int:
        #[312:728] are bits for the side spaces.
        # Counts all the all bits. if there are no bit meaning no cards it will be counted as one free space
        x = 312
        count_of_spaces = 0
        for i in range(0,8):
            if T.sum(state[x+i*52:x+(i+1)*52])==0:
                count_of_spaces +=1
        return count_of_spaces
    def count_additional_spaces(self)->int:
        space_last_move = self.count_created_spaces(self.storage.all_states[-2])
        space_current_move = self.count_created_spaces(self.storage.all_states[-1])

        if space_last_move == space_current_move:
            return 0
        if space_current_move> space_last_move:
            return space_current_move - space_last_move
        else:
            return 0



