
from Klassen import Spiel, Spieler, initialize_paechen, initialize
from Neuralnetwork_Stuff import Agent, DualingQNetwork, Storage, TensorMetricBoard

import random

class AgentTrainer:
    def __init__(self):
        self.agent1:Agent = None
        self.agent2:Agent = None
        self.initialize_agents('Agent2.txt', 'Agent1.txt')
        self.game = None
        self.current_playing_agent:Agent = None
        self.tensorboard = TensorMetricBoard()



    def initialize_agents(self, file_Path1, file_Path2):

        try:
            nn1 = DualingQNetwork(0.005, file_Path1)
            nn1.load_savestate()
            self.agent1 =Agent(nn1)
        except:
            print("No savestate found for agent 1, starting from scratch")
            nn1 = DualingQNetwork(0.005, file_Path1)
            self.agent1 = Agent(nn1)

        try:
            nn2 = DualingQNetwork(0.005, file_Path2)
            nn2.load_savestate()
            self.agent2 =Agent(nn2)
        except:
            print("No savestate found for agent 2, starting from scratch")
            nn2 = DualingQNetwork(0.005, file_Path2)
            self.agent2 = Agent(nn2)

    def train_agents(self,nr_episodes,steps,start_epsilon= 0.9,discount_factor=0.9,epsilon_decay=0.99995):
        max_number_of_moves = steps
        current_epsilon = start_epsilon
        current_move = 0
        for episode in range(nr_episodes):
            move = 0
            self.initialize_game()
            print("New Episode started")
            while move < max_number_of_moves and self.game.gameon:
                self.check_current_agent()
                made_moves,valid_moves, epsilon, total_reward, total_loss= self.current_playing_agent.train_one_turn(current_epsilon, discount_factor, epsilon_decay)
                current_epsilon = epsilon
                print(epsilon)
                move += made_moves
                current_move +=1
                if total_loss != 0:
                    reward_loss_ratio = total_reward / (-total_loss)
                else:
                    reward_loss_ratio = 0
                if made_moves != 0:
                    valid_moves_ratio = valid_moves / made_moves
                else:
                    valid_moves_ratio = 0

                self.tensorboard.log_turn(current_move,made_moves,valid_moves, epsilon, total_reward, total_loss, reward_loss_ratio, valid_moves_ratio)
        self.agent1.nn.save_savestate()
        self.agent2.nn.save_savestate()
        self.tensorboard.close()










    def set_all_game(self,game):
        self.game = game
        self.agent1.game = game
        self.agent2.game = game


    def initialize_game(self):
        self.game = Spiel()
        self.set_all_game(self.game)
        newdeck1 =  self.game.kartenDeckErstellung()
        newdeck2 =  self.game.kartenDeckErstellung()

        random.shuffle(newdeck1)
        random.shuffle(newdeck2)

        spieler1 = Spieler(1, newdeck1)
        spieler2 = Spieler(2, newdeck2)
        self.game.spieler1 = spieler1
        self.game.spieler2 = spieler2

        self.agent1.spieler = spieler1
        self.agent2.spieler = spieler2

        initialize( self.game, spieler1, spieler2)

        spieler1.ersteAktion()
        spieler2.ersteAktion()
        self.game.game_first_move()
        initialize_paechen(self.game)

        self.agent1.storage = Storage(self.game)
        self.agent2.storage = Storage(self.game)

        if self.agent1.spieler.anderreihe:
            self.current_playing_agent = self.agent1
            print("der Momentane agent 1 ist "  + str(self.current_playing_agent.spieler.anderreihe)+" anderreihe")


        else:
            self.current_playing_agent = self.agent2
            print("der Momentane agent 2 ist "  + str(self.current_playing_agent.spieler.anderreihe)+" anderreihe")



    def delete_game(self):
        del self.agent1.game
        del self.agent1.spieler
        del self.agent2.game
        del self.agent2.spieler
        del self.game

    def check_current_agent(self):
        #wenn der Spieler des Agente nicht ander reihe ist wird der momentan spielende Agent gewechselt
        if self.current_playing_agent.spieler.anderreihe == False:
            if self.current_playing_agent == self.agent1:
                self.current_playing_agent = self.agent2
            else:
                self.current_playing_agent = self.agent1
