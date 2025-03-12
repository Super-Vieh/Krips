import os
import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
class Storage:
    def __init__(self,game:Spiel):
        self.game = game
        self.states = T.tensor([], dtype=T.bool)
        self.actions = T.tensor([], dtype=T.int64)
        self.rewards = T.tensor([], dtype=T.float32)

    # is responsible for the done flag
    def done(self)->bool:
        return self.game.gameon

    def reward(self):
        pass
    def initialize_actions(self)->T.tensor:
        actions_firstoutputlayer=[
            0,1,2,3,4,5,6,7,8,9,10,11,12,13
        ]

        actions_secondoutputlayer=[
            0,1,2,3,4,5,6,7,8,9,10,11,12,13
        ]
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
        return T.tensor(states, dtype=T.bool)

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
class DualingQNetwork(nn.Module):
    def __init__(self,states,learning_rate,savestate_file_name):
        super().__init__()
        self.savestate_dir = 'Savestates'
        self.savestate_file = os.path.join(self.savestate_dir, savestate_file_name)
        self.learning_rate = learning_rate
        self.states:T.Tensor =states
        self.inputlayer=nn.Linear(1144,700)
        self.linearlayer2=nn.Linear(700,200)
        self.linearlayer3=nn.Linear(200,128)
        self.valuelayer1=nn.Linear(128,64)
        self.valueoutputlayer=nn.Linear(64,1)
        self.advantagelayer1=nn.Linear(128,64)
        self.advantage_fullyconnected_outputlayer=nn.Linear(64,5)
        self.advantageoutputlayer=nn.Linear(5,5)

        self.optimizer = optim.Adam(self.parameters(), lr=self.learning_rate)
        self.loss = nn.MSELoss()
        # a device may be needed

    def forward(self,states):
        #here are the first 3 layers
        # die inputdaten(states(als tensor)) werden in die erste lineare schicht gegeben und die ergebnisse der gewichtug wird gespeichert
        input = F.relu(input) # das ergebniss der gewichte wird durch die relu funktion gegeben und gespeichert.
        secondlayer = self.linearlayer2(input)
        secondlayer = F.relu(secondlayer)
        thirdlayer = self.linearlayer3(secondlayer)
        thirdlayer = F.relu(thirdlayer)
        #here is the dualing part
        # the value stream
        valueinput = self.valuelayer1(thirdlayer)
        valueinput = F.relu(valueinput)
        # no activation fuction for the output
        valueoutput = self.valueoutputlayer(valueinput)


        # the advantage stream
        advantageinput = self.advantagelayer1(thirdlayer)
        advantageinput = F.relu(advantageinput)
        # no activation fuction for the output
        advantagefullyconnectedoutput = self.advantage_fullyconnected_outputlayer(advantageinput)

        advantageoutput = self.advantageoutputlayer(advantagefullyconnectedoutput)

        return valueoutput, (advantagefullyconnectedoutput, advantageoutput)


    def save_savestate(self):
        print('... saving model ...')
        T.save(self.state_dict(), self.savestate_file)

    def load_savestate(self):
        print('... loading model ...')
        self.load_state_dict(T.load(self.savestate_file))