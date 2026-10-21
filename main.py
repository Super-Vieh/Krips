import time
from enum import Enum
import random

import pygame

from Datenbank.datenbank import Datenbank
from Gymnasium import KripsEnv, RandomBot
from Klassen.spielinititalisierer import SpielInitialisierer
from Datenbank import Datenbank

from Pygame import GUI, MKarte
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert, SpielInitialisierer
from Neuralnetwork_Stuff import Agent, DualingQNetwork, Storage, AgentTrainer
def main():

    #game = SpielInitialisierer.initialize_game_for_play()
    #SpielInitialisierer.play_init(game)
    start = time.perf_counter()
    games = _create_parralel_games(1000)
    for i in range(0, 1000):
        for game_tuple in games:

            (env,bot1,bot2) = game_tuple
            if env.game.current.spielernummer == 1:
                move = bot1.act(env.game)
                env.step(move, False)
                move = bot2.act_off_turn()
                env.step(move, True)
                continue
            if env.game.current.spielernummer == 2:
                move = bot2.act(env.game)
                env.step(move, False)
                move = bot1.act_off_turn()
                env.step(move, True)

    dauer = time.perf_counter() - start
    print(dauer)



"""
    for i in range(0,40):
        trainer = AgentTrainer()
        trainer.load_nn("Agent1.txt", "Agent2.txt")
        trainer.train_agents_and_store(1, 2000, 0.9, 0.9, 0.9999)
        #trainer.train_agents_and_replay(20, 2000, 0.9, 0.9, 0.9999)

        #play_from_db(game1,db,6)
        #gui = GUI(game1)
        #gui.instance()

        #play_console(game1,db)
        #pygame.quit()


        #db.verbindung_schliessen()
2
"""
def _create_parralel_games(n_games:int)->list[tuple]:
    list_of_enviroments = []
    for _ in range(n_games):
        env = KripsEnv()
        env.reset()
        seed = random.randint(0, 2 ** 32 - 1)
        bot1 = RandomBot(seed)
        bot2 = RandomBot(seed)
        list_of_enviroments.append((env,bot1,bot2))
    return list_of_enviroments



if __name__ == "__main__":
    main()
