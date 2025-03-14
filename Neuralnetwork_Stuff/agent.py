import os
import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from Neuralnetwork_Stuff.storage import Storage
from Neuralnetwork_Stuff.qualing_q_learning import DualingQNetwork
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
class Agent():
    def __init__(self,storage:Storage,nn:DualingQNetwork):
        self.storage = storage
        self.nn = nn

    def select_action(self):
        # epsilon-greedy policy
        pass

    def compute_loss(self,state,action1,action2,reward,next_state,done,discount_factor):


        (value,advantage1,advantage2)= self.nn.forward(state)
        predicted_value = self.map_qvalue_to_action(value, advantage1, advantage2, action1, action2)

        (value,advantage1,advantage2) = self.nn.forward(next_state)
        predicted_value_nextstate = T.max(self.nn.combine_value_advantage(value,advantage1,advantage2))

        target_value =  reward + discount_factor * predicted_value_nextstate * (1 - done)
        loss = F.mse_loss(predicted_value, target_value)
        return loss

    def map_qvalue_to_action(self,value,advantage1,advantage2,action1,action2):
        # i have to map an N(0-11) and M(0-21) intex to the action pair


        all_q_values =self.nn.combine_value_advantage(value, advantage1, advantage2)# ist eine NxM distribution
        #action1 and action are int values so you can just plug them in
        estimated_q_value= all_q_values[action1][action2]

        return estimated_q_value
    def update_network(self):
        pass

    def trainig_loop(self):
        pass
