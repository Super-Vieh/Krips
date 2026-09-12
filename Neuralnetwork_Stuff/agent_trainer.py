
from Klassen import Game, Player, GameInitializer
#, initialize_paechen, initialize_oponents)
from Neuralnetwork_Stuff import Agent, DualingQNetwork, Storage, TensorMetricBoard
import random

from Neuralnetwork_Stuff.reward_engine import RewardEngine


class AgentTrainer:
    def __init__(self):
        self.agent1:Agent = None
        self.agent2:Agent = None
        #self.load_nn()
        self.game: Game = None
        self.current_playing_agent:Agent = None
        self.tensorboard: TensorMetricBoard = TensorMetricBoard()
        self.replay_ids: list[int] = []




    def load_nn(self, file_Path1: str, file_Path2: str, learnig_rate: float = 0.001) -> None:

        try:
            nn1: DualingQNetwork = DualingQNetwork(learnig_rate, file_Path1)
            nn1.load_savestate()
            self.agent1 =Agent(nn1)
        except:
            print("No savestate found for agent 1, starting from scratch")
            nn1: DualingQNetwork = DualingQNetwork(learnig_rate, file_Path1)
            self.agent1 = Agent(nn1)

        try:
            nn2: DualingQNetwork = DualingQNetwork(learnig_rate, file_Path2)
            nn2.load_savestate()
            self.agent2 =Agent(nn2)
        except:
            print("No savestate found for agent 2, starting from scratch")
            nn2: DualingQNetwork = DualingQNetwork(learnig_rate, file_Path2)
            self.agent2 = Agent(nn2)

    def train_agents_and_store(self, nr_episodes: int, steps: int, start_epsilon: float = 0.9, discount_factor: float = 0.9, epsilon_decay: float = 0.99995) -> None:
        from Datenbank.datenbank import Database
        db: Database = Database("Datenbank/krips_replay_store.duckdb")
        max_number_of_moves: int = steps
        current_epsilon: float = start_epsilon
        current_move: int = 0
        list_of_valid_moves: list = []
        for episode in range(nr_episodes):
            move: int = 0
            id: int = self.initialize_agenttrainer_for_storage(db)
            self.set_game_for_agent(self.agent1)
            self.set_game_for_agent(self.agent2)
            print("New Episode started")
            while move < max_number_of_moves and self.game.is_running:
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
    def train_agents_and_replay(self, nr_episodes: int, steps: int, start_epsilon: float = 0.9, discount_factor: float = 0.9, epsilon_decay: float = 0.99995) -> None:
        from Datenbank.datenbank import Database
        db: Database = Database("Datenbank/krips_replay_store.duckdb")
        max_number_of_moves: int = steps
        current_epsilon: float = start_epsilon
        current_move: int = 0
        self.set_replay_ids(db)

        for episode,id in zip(range(nr_episodes),self.replay_ids):
            print(id)
            move: int = 0
            self.initialize_agenttrainer_for_replay(db,id)
            self.set_game_for_agent(self.agent1)
            self.set_game_for_agent(self.agent2)
            print("New Episode started")
            while move < max_number_of_moves and self.game.is_running:
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


    def initialize_agenttrainer_for_storage(self, db: 'Database') -> int:

        self.game ,id= SpielInitialisierer.initialize_game_for_storage(db)
        self.agent1.game = self.game
        self.agent2.game = self.game
        self.agent1.player = self.game.player1
        self.agent2.player = self.game.player2
        self.agent1.storage = Storage(self.game)
        self.agent2.storage = Storage(self.game)
        self.agent1.reward_engine = RewardEngine(self.game,self.agent1.storage)
        self.agent2.reward_engine = RewardEngine(self.game,self.agent2.storage)

        if self.game.current_player is self.agent1.player:
            self.current_playing_agent = self.agent1
        else:
            self.current_playing_agent = self.agent2
        return id
    def initialize_agenttrainer_for_replay(self, db: 'Database', id: int) -> None:

        self.game: Game = SpielInitialisierer.initialize_game_for_replay(db,id)
        print(self.game)
        self.agent1.game = self.game
        self.agent2.game = self.game
        self.agent1.player = self.game.player1
        self.agent2.player = self.game.player2
        self.agent1.storage = Storage(self.game)
        self.agent2.storage = Storage(self.game)
        self.agent1.reward_engine = RewardEngine(self.game, self.agent1.storage)
        self.agent2.reward_engine = RewardEngine(self.game, self.agent2.storage)
        self.agent1.replay_moves = db.load_game_moves(id)
        self.agent2.replay_moves = db.load_game_moves(id)


        if self.game.current_player is self.agent1.player:
            self.current_playing_agent = self.agent1
        else:
            self.current_playing_agent = self.agent2




    def delete_game(self) -> None:
        del self.agent1.game
        del self.agent1.player
        del self.agent2.game
        del self.agent2.player
        del self.game

    def check_current_agent(self) -> None:
        #wenn der Spieler des Agente nicht ander reihe ist wird der momentan spielende Agent gewechselt
        if self.game.current_player is not self.current_playing_agent.player:
            if self.current_playing_agent == self.agent1:
                self.current_playing_agent = self.agent2
            else:
                self.current_playing_agent = self.agent1
    def set_game_for_agent(self, agent: Agent) -> None:
        agent.game = self.game
    def set_replay_ids(self, db: 'Database') -> None:
        try:
            next_id: int = db.get_next_game_id()
            self.replay_ids= [id for id in range(1,next_id)]
        except:
            raise ValueError("Keine Spiele aus der Datenbank gehohlt")



