import os
import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
from Klassen import print_top,print_sidesplus,print_bot
class Storage:
    def __init__(self,game:Spiel):
        self.game = game
        self.transitions:list[tuple[T.Tensor,tuple[T.Tensor,T.Tensor],float,T.Tensor,bool]] = []
        # A list which contains tuples of the state(tensor),action(tupel of two tensors),reward(float),next_state(tensor),done(bool)
        self.all_states = [self.initialize_states(self.game)]
        # last state is the state that was stored before an action was taken in the form of a tensor
        self.last_state = self.initialize_states(self.game)


    def create_transition(self):
        #this function creates small packages moves with its consequences
        state = self.last_state
        # state is the last state that was stored before an action was taken
        next_state = self.initialize_states(self.game)
        # next_state is the current state after the action was taken
        (action1,action2) = self.initialize_actions()
        reward = self.reward()
        done = self.done()
        transition = (state,(action1,action2),reward,next_state,done)
        self.last_state = next_state
        return transition

    # is responsible for the done flag
    def done(self)->bool:
        if self.game.gameon == False:
            return True
        else:
            return False

    def reward(self):
        reward = 0
        #[0] and [1] if current state are list with the cards of player1 and player2
        #[2] and [3] are the lists of the playing field 3 is the list with the sidelists and 4 is the list with the centerlists
        #every ellement in the tuple is a list of lists
        current_state= self.initialize_states(self.game)
        self.all_states.append(current_state)
        reward+=self.did_an_action_do_something()
        if reward== 10:
            print_sidesplus(self.game)
            print_bot(self.game)
        reward+= self.punish_back_and_forth()
        print(reward)
        return reward


    #first only this function to test if the nn can atleast do leagal moves
    def did_an_action_do_something(self):

        if self.all_states and len(self.all_states)>=2 and T.equal(self.all_states[-1] ,self.all_states[-2]):
                return -20
        else:
                return 10
    def punish_back_and_forth(self):
        # if the state is the same after 2 moves it means that the agent just shifted the cards
        # something similar might happen after 4 moves
        if self.all_states and len(self.all_states)==3:
            if T.equal(self.all_states[-1] , self.all_states[-3]):
                return -10
        if  len(self.all_states) ==5:
            if T.equal(self.all_states[-1],self.all_states[-5]):
                return -10
        return 1

    def initialize_actions(self)->T.tensor:
        actions_firstoutputlayer=[
            0,1,2,3,4,5,6,7,8,9,10,11,
        ]
        # K->0 , S1-S8 ->1-8,A0->9 A1->10 A2->11 = in total 12 states for the first action

        actions_secondoutputlayer=[
            0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
        ]
        # K->0 ,S1-S8 ->1-8,M1-M8->9-16,A0->18 A1->19 A2->20, G0->21 = intotal 22 states for the second action
        actions_firstoutputlayer_t=T.tensor(actions_firstoutputlayer, dtype=T.float32)
        actions_secondoutputlayer_t=T.tensor(actions_secondoutputlayer, dtype=T.float32)
        return actions_firstoutputlayer_t, actions_secondoutputlayer_t
    def initialize_states(self,game:Spiel)->T.tensor:
        states:list=[]
        spieler_listen = []
        #spielerfeld listen is a list of all list that are on the playing field.
        # it is a list of lists and so are platzliste and mittlereliste. they can be added
        spielfeld_listen = game.platzliste+game.mittlereliste

        #spieler listen is a list of all lists that belong to the players the list itself is also a list of list
        # but the game.spieler1 and game.spieler2 list are only sipmle lists
        spieler_listen.append(game.spieler1Haufen)
        spieler_listen.append(game.spieler1Paechen)
        spieler_listen.append(game.spieler1Dreizehner)

        spieler_listen.append(game.spieler2Haufen)
        spieler_listen.append(game.spieler2Paechen)
        spieler_listen.append(game.spieler2Dreizehner)


        i =0
        for list in spieler_listen + spielfeld_listen:
            i+=1
            states+=self.transform_to_52bitvektor(list)
        return T.tensor(states, dtype=T.float32)

    def transform_to_52bitvektor(self,list:list[Karten]):
        dict_suit ={
            KartenTyp.Pik:0,
            KartenTyp.Coeur:1,
            KartenTyp.Treff:2,
            KartenTyp.Karro:3
        }
        empty_list = [0]*52
        if not list:# wenn die liste kein element hat wird ein voller 0 vektor zurückgegeben
            return empty_list
        for card in list:
            if card.karteOffen== False and list[-1].karteOffen== False:
                # wenn die Karte nicht offen ist, dann wird sie nicht in den Vektor aufgenommen
                # das list[-1] ist für doe spielerlisten da dort die letze karte die erste ist
                break
            if card.karteOffen == False:
                # wenn die Karte nicht offen ist, dann wird sie nicht in den Vektor aufgenommen
                # die zweite überprüfung is notwending da im ersten if auf eine kombination
                continue
            mult = dict_suit[card.kartentyp]
            empty_list[(mult*13)+card.kartenwert.value-1]=1
            # der intex wird berechnet durch die art von Karte 0-3 und den Wert1-13

        return empty_list
