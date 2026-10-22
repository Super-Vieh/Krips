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
    Agent as BatchAgent,
    DualingQNetwork as BatchDualingQNetwork,
    Storage as BatchStorage,
)
from performance_evaluation import benchmark_engine_and_encoding


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


def _create_parralel_games(n_games: int) -> list[tuple]:
    list_of_enviroments = []
    for _ in range(n_games):
        env = KripsEnv()
        env.reset()
        seed = random.randint(0, 2 ** 32 - 1)
        bot1 = RandomBot(seed)
        bot2 = RandomBot(seed)
        list_of_enviroments.append((env, bot1, bot2))
    return list_of_enviroments


def benchmark_parallel_envs(n_games: int = 1000) -> None:
    storage = BatchStorage()
    net = BatchDualingQNetwork(0.001, "benchmark_parallel.txt")
    agent = BatchAgent(net, storage, seed=1)
    games = _create_parralel_games(n_games)

    start = time.perf_counter()
    states = storage.initialize_states_batch([env.game for env, _, _ in games])
    encode_dauer = time.perf_counter() - start

    net.eval()
    start = time.perf_counter()
    with torch.no_grad():
        for _ in range(10000):
            q = net.q_values(states)
    forward_dauer = time.perf_counter() - start

    start = time.perf_counter()
    actions = agent.act([env.game for env, _, _ in games], epsilon=0.0)
    act_dauer = time.perf_counter() - start

    print("Envs:", n_games, "States:", tuple(states.shape))
    print("States aus Envs:", encode_dauer)
    print("10000 Forward-Passes mit Batch", n_games, ":", forward_dauer)
    print("Agent.act fuer", n_games, "Envs:", act_dauer, "Aktionen:", len(actions))


def main():

    #game = SpielInitialisierer.initialize_game_for_play()
    #SpielInitialisierer.play_init(game)
    #benchmark_batch()
    #benchmark_parallel_envs(5000)
    benchmark_engine_and_encoding()
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
