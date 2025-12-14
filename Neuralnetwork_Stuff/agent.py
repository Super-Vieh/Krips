import os
import random
import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from Neuralnetwork_Stuff.storage import Storage
from Neuralnetwork_Stuff.qualing_q_learning import DualingQNetwork
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert,initialize_paechen,initialize
from Pygame import GUI, MKarte

class Agent():
    def __init__(self,nn:DualingQNetwork):
        self.storage = None
        self.nn = nn
        self.game= None
        self.spieler = None



    def training_loop(self,optimizer,nr_episodes,start_epsilon,discount_factor):
        #gui = GUI(self.game)

        epsilon = start_epsilon # random rate
        for i in range(0,nr_episodes):# the number of episodes of training
            if self.game:
                self.delete_game()
            self.initialize_game()
            #gui.game = self.game
            self.storage = Storage(self.game)

            done = False
            max_number_of_moves = 10000
            while not done and  max_number_of_moves > 0:
                max_number_of_moves -= 1
                print(max_number_of_moves)
                if self.game.spieler1.anderreihe == True: self.game.current = self.game.spieler1
                elif self.game.spieler2.anderreihe == True: self.game.current = self.game.spieler2

                states = self.storage.initialize_states(self.game)
                # makes states into a tensor

                action = self.select_action(epsilon,states)
                self.game.play_nn(action)
                next_state = self.storage.initialize_states(self.game)
                # rewards are computed in the storageclass
                reward = self.storage.reward()
                #if reward> 0: gui.image()
                done = self.storage.done()
                action1,action2 = self.decode_action(action)
                loss = self.compute_loss(states,action1,action2,reward,next_state,done,discount_factor)
                self.update_network(optimizer,loss)
                states = next_state
                if epsilon > 0.01:
                    epsilon = epsilon*0.99995 # decay epsilon
                print(f"Epsilon is now {epsilon}")

            self.nn.save_savestate()






    def select_action(self,epsilon,state)->str:
        dict_action1 =  {
            0:"K0",1:"S1",2:"S2",3:"S3",4:"S4",5:"S5",6:"S6",7:"S7",8:"S8",9:"A0",10:"A1",11:"A2"
        }
        dict_action2 = {
            0:"K0",1:"S1",2:"S2",3:"S3",4:"S4",5:"S5",6:"S6",7:"S7",8:"S8",9:"M1",10:"M2",11:"M3",12:"M4",13:"M5",14:"M6",15:"M7",16:"M8",17:"A0",18:"A1",19:"A2",20:"G0"
        }
        if epsilon > np.random.random() :
            n = np.random.randint(1,12) # returns a random integer from 0 to 11 excluding 12
            m = np.random.randint(1,21)
            s_n = dict_action1[n]
            s_m = dict_action2[m]
            action =  s_n +s_m
            return action



        value,advantage1,advantage2=self.nn.forward(state)
        all_q_values = self.nn.combine_value_advantage(value,advantage1,advantage2)
        all_q_values[0][0]= -np.inf  #K0K0 wird rausgenommen
        best_q_value= all_q_values.max()


        (n,m) = self.find_index_of_best_q_value(all_q_values,best_q_value)

        s_n = dict_action1[n]
        s_m = dict_action2[m]
        action = s_n +s_m
        return action
    def decode_action(self,action)->tuple[int,int]:
        # the functrion takes a action string and returns a tuple of the int values of the action A0A1 -> (9,18)
        swapped_dict_action1 = {
            "K0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5, "S6": 6, "S7": 7, "S8": 8, "A0": 9, "A1": 10, "A2": 11
        }
        swapped_dict_action2 = {
            "K0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5, "S6": 6, "S7": 7, "S8": 8, "M1": 9, "M2": 10, "M3": 11, "M4": 12, "M5": 13, "M6": 14, "M7": 15, "M8": 16, "A0": 17, "A1": 18, "A2": 19, "G0": 20
        }
        # first 2 letters are stringspliced and then the strings are fed ito the dict to get the int values
        action1,action2 = swapped_dict_action1[action[0:2]] , swapped_dict_action2[action[2:4]]
        #print(f"decode action: {action1} {action2}")
        return (action1,action2)
    def find_index_of_best_q_value(self,all_q_values,target_value):
        # the goal is to find the index of the best q-value in the list
        # the presmise is that the target value is in the list
        # if the target value is not in the list, the function will raise a ValueError which is good and will be used to debugg
        q_list = all_q_values.tolist()
        m = None
        for n,sublist in enumerate(q_list):
            if target_value in sublist:
                m = sublist.index(target_value)
                return (n,m)
        if m == None:
            raise ValueError("The expected Q-Value is not in the list\n "
                       "The error is in the function find_index_of_best_q_value in the class Agent or in the value given.\n"
                       "It might not exist")
        return (0,0) # this line should never be reached
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

        #action1 and action2 are int values so you can just plug them in
        #print(all_q_values)
        estimated_q_value= all_q_values[action1][action2]
        return estimated_q_value
    def update_network(q_network, optimizer, loss):
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    def train_one_turn(self, epsilon, discount_factor, epsilon_decay=0.9995)->tuple[int,float]:
        made_moves = 0
        while self.game.current == self.spieler and self.game.gameon:
            # could create a bug, not sure if the game.current can be equal to the player. 
            # Does the player object change after a move in the game?
            made_moves += 1
            states = self.storage.initialize_states(self.game)
            # makes states into a tensor

            action = self.select_action(epsilon, states)
            self.game.play_nn(action)
            next_state = self.storage.initialize_states(self.game)
            # rewards are computed in the storageclass
            reward = self.storage.reward()
            if reward > 0:
                print(action)
            done = self.storage.done()
            action1, action2 = self.decode_action(action)
            loss = self.compute_loss(states, action1, action2, reward, next_state, done, discount_factor)
            self.update_network(self.nn.optimizer, loss)
            states = next_state
            if epsilon > 0.1:
                epsilon = epsilon * epsilon_decay # decay epsilon

        return made_moves, epsilon
