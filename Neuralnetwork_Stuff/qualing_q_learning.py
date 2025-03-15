import os
import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert

class DualingQNetwork(nn.Module):
    def __init__(self,learning_rate,savestate_file_name):
        super().__init__()
        self.savestate_dir = 'Savestates'
        self.savestate_file = os.path.join(self.savestate_dir, savestate_file_name)
        self.learning_rate = learning_rate
        #self.states:T.Tensor = None
        self.inputlayer=nn.Linear(1144,700)
        self.linearlayer2=nn.Linear(700,200)
        self.linearlayer3=nn.Linear(200,128)
        self.valuelayer1=nn.Linear(128,64)
        self.valueoutputlayer=nn.Linear(64,1)
        self.advantagelayer1=nn.Linear(128,64)
        self.advantage_fullyconnected_outputlayer=nn.Linear(64,12)
        self.advantageoutputlayer=nn.Linear(12,21)

        self.optimizer = optim.Adam(self.parameters(), lr=self.learning_rate)
        self.loss = nn.MSELoss()
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)



    def forward(self,states):

        states = states.to(self.device)
        #here are the first 3 layers
        # die inputdaten(states(als tensor)) werden in die erste lineare schicht gegeben und die ergebnisse der gewichtug wird gespeichert
        input = self.inputlayer(states)
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

        return valueoutput, advantagefullyconnectedoutput, advantageoutput


    def combine_value_advantage(self,value, advantage1, advantage2):
        # the unsequeeze function adds a dimension to the tensor it makes it a list of lists with only one list containig all elements
        # for the opperations to work on  the tensors,they need to be a centain shape
        # here the unsqueeze 1 makes the adv1 tensor in the shape of (N,1) the 0 makes adv2 in the shape of (1,M)
        adv1 = advantage1.unsqueeze(1)
        adv2 = advantage2.unsqueeze(0)

        # the pair_mean is also now a list of list.
        # it is like a nested for loop where the first element of adv1 is seperatly added to all elements of adv2 creating a 1d list
        # then the second element of adv1 is seperatly added to all elements of adv2 creating a 1d and so on
        #these 1d list are as long as there are elements in adv2 and as many as there are elements in adv1
        # pair_mean = [N][M]
        pair_mean = (adv1 + adv2) / 2

        # the overall_mean is the scalar of all pairs of N and M
        # it takes the mean of MxN pairs
        overall_mean = pair_mean.mean()

        # the q_values are the standart value v(s) and the advantage of an action (a)
        # the advantage is calculated by how good the pair values are compared to the average values
        # and the value is the value of the state so it is always present
        q_values = value + pair_mean - overall_mean
        # P.S. this is a heavily simplified version done by a LLM.
        # my version was python algorith based and not tensor based thus extremly slow the idea was the same though
        return q_values




    # i have to get back to this and unterstand how to save the model
    def save_savestate(self):
        print('... saving model ...')
        T.save(self.state_dict(), self.savestate_file)

    def load_savestate(self):
        print('... loading model ...')
        self.load_state_dict(T.load(self.savestate_file))