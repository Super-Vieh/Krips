import time
from enum import Enum
import random

import pygame
import torch

from Datenbank.datenbank import Datenbank
from Gymnasium import KripsEnv, RandomBot
from Klassen.spielinititalisierer import SpielInitialisierer
from Datenbank import Datenbank

from Pygame import GUI, MKarte
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert, SpielInitialisierer
from Neuralnetwork_Stuff import Agent, DualingQNetwork, Storage, AgentTrainer
from Neuralnetwork_Batch import (
    DualingQNetwork as BatchDualingQNetwork,
    Storage as BatchStorage,
)


def benchmark_batch() -> None:
    random.seed(1)
    storage = BatchStorage()
    game = SpielInitialisierer.initialize_game_for_play()

    start = time.perf_counter()
    states = []
    for i in range(1000):
        states.append(storage.initialize_states(game))
        moves = game.all_moves()
        if not moves:
            game = SpielInitialisierer.initialize_game_for_play()
            continue
        game.play_nn(random.choice(moves))
        game.game_ended()
        if not game.gameon:
            game = SpielInitialisierer.initialize_game_for_play()
    states = torch.cat(states, dim=0)
    encode_dauer = time.perf_counter() - start

    net = BatchDualingQNetwork(0.001, "benchmark.txt")
    net.eval()

    start = time.perf_counter()
    with torch.no_grad():
        for i in range(100):
            q = net.q_values(states)
    forward_batch_1000 = time.perf_counter() - start

    start = time.perf_counter()
    with torch.no_grad():
        for i in range(100):
            q_small = net.q_values(states[i * 10:(i + 1) * 10])
    forward_batch_10 = time.perf_counter() - start

    print("States:", tuple(states.shape))
    print("1000 States erzeugen:", encode_dauer)
    print("100 Forward-Passes mit Batch 1000:", forward_batch_1000)
    print("100 Forward-Passes mit Batch 10 (1000 Vorhersagen):", forward_batch_10)
    print("Q:", tuple(q.shape), tuple(q_small.shape))


def main():

    #game = SpielInitialisierer.initialize_game_for_play()
    #SpielInitialisierer.play_init(game)
    benchmark_batch()
    """
    start = time.perf_counter()
    env = KripsEnv()
    env.reset()
    seed = random.randint(0, 2 ** 32 - 1)
    bot1 = RandomBot(seed)
    bot2 = RandomBot(seed)
    for i in range(0, 1000000):
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
                continue
            if env.game.gameon == False:
                env.reset()
    dauer = time.perf_counter() - start
    print(dauer)
"""
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

"""

if __name__ == "__main__":
    main()
