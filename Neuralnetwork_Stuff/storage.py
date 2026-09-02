import os
import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
#from Klassen import print_top,print_sidesplus,print_bot
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
        """
        KARTEN-MENGEN (welche Karten liegen in der Liste): 22 Listen * 52 = 1144
        SPIELER 1:
        [0:52]     -> Spieler 1 Päckchen (Handkarten)
        [52:104]   -> Spieler 1 Haufen (Ablagestapel)
        [104:156]  -> Spieler 1 Dreizehner

        SPIELER 2:
        [156:208]  -> Spieler 2 Päckchen (Handkarten)
        [208:260]  -> Spieler 2 Haufen (Ablagestapel)
        [260:312]  -> Spieler 2 Dreizehner

        SPIELFELD Seitenplätze:
        [312:728]  -> Platzliste 8 Listen * 52
        (z.B. Platz 1 ist 312:364, Platz 2 ist 364:416, ...)

        SPIELFELD Mitte:
        [728:1144] -> Mittelliste 8 Listen * 52

        OBERSTE KARTE PRO LISTE (welche Karte ist oben/spielbar): 22 * 52 = 1144
        [1144:2288] -> für jede der 22 Listen dieselbe Reihenfolge wie oben,
                       aber nur die oberste aufgedeckte Karte gesetzt.
        Grund: die Mengen-Kodierung verliert die Reihenfolge (z.B. beim
        Ablagehaufen), damit wäre die einzig spielbare Karte unsichtbar.
        """


        states:list=[]
        spieler_listen = []
        #spielerfeld listen is a list of all list that are on the playing field.
        # it is a list of lists and so are platzliste and mittlereliste. they can be added
        spielfeld_listen = game.platzliste+game.mittlereliste

        #spieler listen is a list of all lists that belong to the players the list itself is also a list of list
        # but the game.spieler1 and game.spieler2 list are only simple lists
        spieler_listen.append(game.spieler1Paechen)
        spieler_listen.append(game.spieler1Haufen)
        spieler_listen.append(game.spieler1Dreizehner)

        spieler_listen.append(game.spieler2Paechen)
        spieler_listen.append(game.spieler2Haufen)
        spieler_listen.append(game.spieler2Dreizehner)

        # Layout: erst alle 22 Karten-Mengen-Vektoren ([0:1144]), dann alle 22
        # Top-Karten-Vektoren ([1144:2288]) - entspricht dem Docstring oben und
        # den Indizes in reward_engine.py. (NICHT pro Liste interleaved.)
        for list in spieler_listen + spielfeld_listen:
            states += self.transform_to_52bitvektor(list)
        for list in spieler_listen + spielfeld_listen:
            states += self.transform_top_to_52bitvektor(list)
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

    def transform_top_to_52bitvektor(self, list:list[Karten]):
        """Kodiert NUR die oberste (spielbare) Karte einer Liste als 52-Bit.
        Die Mengen-Kodierung (transform_to_52bitvektor) verliert die Reihenfolge
        und damit, welche Karte oben liegt (kritisch beim Ablagehaufen: dort ist
        nur die oberste Karte spielbar und der Gegner spielt auf ihr)."""
        dict_suit = {
            KartenTyp.Pik: 0,
            KartenTyp.Coeur: 1,
            KartenTyp.Treff: 2,
            KartenTyp.Karro: 3
        }
        empty_list = [0] * 52
        if not list or not list[-1].karteOffen:
            return empty_list
        card = list[-1]
        empty_list[(dict_suit[card.kartentyp] * 13) + card.kartenwert.value - 1] = 1
        return empty_list
