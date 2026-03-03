
from Klassen import Spiel, Spieler, SpielInitialisierer
#, initialize_paechen, initialize_oponents)
from Neuralnetwork_Stuff import Agent, DualingQNetwork, Storage, TensorMetricBoard
import random

from Neuralnetwork_Stuff.reward_engine import RewardEngine


class AgentTrainer:
    def __init__(self):
        self.agent1:Agent = None
        self.agent2:Agent = None
        #self.load_nn()
        self.game = None
        self.current_playing_agent:Agent = None
        self.tensorboard = TensorMetricBoard()
        self.replay_ids = []




    def load_nn(self, file_Path1, file_Path2, learnig_rate = 0.001):

        try:
            nn1 = DualingQNetwork(learnig_rate, file_Path1)
            nn1.load_savestate()
            self.agent1 =Agent(nn1)
        except:
            print("No savestate found for agent 1, starting from scratch")
            nn1 = DualingQNetwork(learnig_rate, file_Path1)
            self.agent1 = Agent(nn1)

        try:
            nn2 = DualingQNetwork(learnig_rate, file_Path2)
            nn2.load_savestate()
            self.agent2 =Agent(nn2)
        except:
            print("No savestate found for agent 2, starting from scratch")
            nn2 = DualingQNetwork(learnig_rate, file_Path2)
            self.agent2 = Agent(nn2)

    def train_agents_and_store(self, nr_episodes, steps, start_epsilon= 0.9, discount_factor=0.9, epsilon_decay=0.99995):
        from Datenbank.datenbank import Datenbank
        db = Datenbank("Datenbank/krips_replay_store.duckdb")
        max_number_of_moves = steps
        current_epsilon = start_epsilon
        current_move = 0
        list_of_valid_moves = []
        for episode in range(nr_episodes):
            move = 0
            id = self.initialize_agenttrainer_for_storage(db)
            self.set_game_for_agent(self.agent1)
            self.set_game_for_agent(self.agent2)
            print("New Episode started")
            while move < max_number_of_moves and self.game.gameon:
                self.check_current_agent()
                made_moves,valid_moves, epsilon, total_reward, total_loss, list_of_valid_moves= self.current_playing_agent.train_one_turn_storage(current_epsilon, discount_factor, epsilon_decay)
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
            db.save_game_moves(list_of_valid_moves,id)
        self.agent1.nn.save_savestate()
        self.agent2.nn.save_savestate()

    'AKTIONEN MÜSSEN EINGESPEIST WERDEN;NOCH NICHT GEMACHT'
    def train_agents_and_replay(self, nr_episodes, steps, start_epsilon= 0.9, discount_factor=0.9, epsilon_decay=0.99995):
        from Datenbank.datenbank import Datenbank
        db = Datenbank("Datenbank/krips_replay_store.duckdb")
        max_number_of_moves = steps
        current_epsilon = start_epsilon
        current_move = 0
        self.set_replay_ids(db)

        for episode,id in zip(range(nr_episodes),self.replay_ids):
            print(id)
            move = 0
            self.initialize_agenttrainer_for_replay(db,id)
            self.set_game_for_agent(self.agent1)
            self.set_game_for_agent(self.agent2)
            print("New Episode started")
            while move < max_number_of_moves and self.game.gameon:
                self.check_current_agent()
                made_moves,valid_moves, epsilon, total_reward, total_loss= self.current_playing_agent.train_one_turn_replay(current_epsilon, discount_factor, epsilon_decay)
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


    def initialize_agenttrainer_for_storage(self,db:'Datenbank'):

        self.game ,id= SpielInitialisierer.initialize_game_for_storage(db)
        print(self.game.spieler1.anderreihe)
        print(self.game.spieler2.anderreihe)
        self.agent1.game = self.game
        self.agent2.game = self.game
        self.agent1.spieler = self.game.spieler1
        self.agent2.spieler = self.game.spieler2
        self.agent1.storage = Storage(self.game)
        self.agent2.storage = Storage(self.game)
        self.agent1.reward_engine = RewardEngine(self.game,self.agent1.storage)
        self.agent2.reward_engine = RewardEngine(self.game,self.agent2.storage)

        if self.agent1.spieler.anderreihe:
            self.current_playing_agent = self.agent1
        else:
            self.current_playing_agent = self.agent2
        return id
    def initialize_agenttrainer_for_replay(self,db:'Datenbank',id:int):

        self.game = SpielInitialisierer.initialize_game_for_replay(db,id)
        print(self.game)
        self.agent1.game = self.game
        self.agent2.game = self.game
        self.agent1.spieler = self.game.spieler1
        self.agent2.spieler = self.game.spieler2
        self.agent1.storage = Storage(self.game)
        self.agent2.storage = Storage(self.game)
        self.agent1.reward_engine = RewardEngine(self.game, self.agent1.storage)
        self.agent2.reward_engine = RewardEngine(self.game, self.agent2.storage)
        self.agent1.replay_moves = db.load_game_moves(id)
        self.agent2.replay_moves = db.load_game_moves(id)


        if self.agent1.spieler.anderreihe:
            self.current_playing_agent = self.agent1
        else:
            self.current_playing_agent = self.agent2




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
    def set_game_for_agent(self,agent:Agent):
        agent.game = self.game
    def set_replay_ids(self,db:'Datenbank'):
        try:
            next_id = db.get_next_game_id()
            self.replay_ids= [id for id in range(1,next_id)]
        except:
            raise ValueError("Keine Spiele aus der Datenbank gehohlt")



