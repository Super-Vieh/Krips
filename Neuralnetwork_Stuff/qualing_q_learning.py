import os
import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert

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

        return valueoutput, (advantagefullyconnectedoutput, advantageoutput)


    def combine_value_advantage(self, value,advantage1, advantage2):
        # This is a non standard way of combining the value and advantage streams
        # it seams that this function is very inefficient and maybe not very good because it does not opperate on the gpu or rather the tensors

        # it takes all posible pairs of advantage1 and advantage2.
        # then i takes the mean of the sum of each pair o find the best advantage pair with.
        # then if takes the mean of all posible pairs and subracts it from the advantage
        # and adds it to the value to get the q value
        advatage1list = advantage1.tolist()
        advatage2list = advantage2.tolist()
        mean_of_the_sum=[]
        for  first_e in advatage1list:
            for  second_e in advatage2list:
                mean_of_the_sum.append((first_e+second_e)/2)
        advantage = max(mean_of_the_sum)
        mean_of_mean= 0
        for each in mean_of_the_sum:
            mean_of_mean+=each
        mean_of_mean=mean_of_mean/len(mean_of_the_sum)

        q_value = value + advantage - mean_of_mean
        return q_value
    def save_savestate(self):
        print('... saving model ...')
        T.save(self.state_dict(), self.savestate_file)

    def load_savestate(self):
        print('... loading model ...')
        self.load_state_dict(T.load(self.savestate_file))