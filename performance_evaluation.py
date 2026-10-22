import random
import time

import torch

from Gymnasium import KripsEnv, RandomBot
from Klassen import SpielInitialisierer
from Neuralnetwork_Batch import (
    Agent as BatchAgent,
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
        for _ in range(100000):
            q = net.q_values(states)
    forward_dauer = time.perf_counter() - start

    start = time.perf_counter()
    actions = agent.act([env.game for env, _, _ in games], epsilon=0.0)
    act_dauer = time.perf_counter() - start

    print("Envs:", n_games, "States:", tuple(states.shape))
    print("States aus Envs:", encode_dauer)
    print("100 Forward-Passes mit Batch", n_games, ":", forward_dauer)
    print("Agent.act fuer", n_games, "Envs:", act_dauer, "Aktionen:", len(actions))


def benchmark_engine_and_encoding(n_games: int = 5000, n_rounds: int = 100000) -> None:
    storage = BatchStorage()
    games = _create_parralel_games(n_games)
    spiele = [env.game for env, _, _ in games]
    for index, game in enumerate(spiele):
        while game.current is None:
            games[index][0].reset()
            spiele[index] = game = games[index][0].game

    encode_dauer = 0.0
    move_dauer = 0.0
    engine_dauer = 0.0
    reset_dauer = 0.0
    zuge = 0

    for _ in range(n_rounds):
        start = time.perf_counter()
        states = storage.initialize_states_batch(spiele)
        encode_dauer += time.perf_counter() - start

        for index, game in enumerate(spiele):
            start = time.perf_counter()
            moves_available = game.all_moves()
            move_dauer += time.perf_counter() - start

            move = random.choice(moves_available)
            start = time.perf_counter()
            game.play_nn(move)
            game.game_ended()
            engine_dauer += time.perf_counter() - start
            zuge += 1

            if not game.gameon:
                start = time.perf_counter()
                games[index][0].reset()
                spiele[index] = games[index][0].game
                while spiele[index].current is None:
                    games[index][0].reset()
                    spiele[index] = games[index][0].game
                reset_dauer += time.perf_counter() - start

    print("Envs:", n_games, "Runden:", n_rounds, "Zuege:", zuge)
    print("Encoding gesamt:", encode_dauer, "->", encode_dauer / zuge * 1e6, "us/Zustand")
    print("Engine gesamt:", engine_dauer, "->", engine_dauer / zuge * 1e6, "us/Zug")
    print("all_moves gesamt:", move_dauer, "->", move_dauer / zuge * 1e6, "us/Zug")
    print("Reset gesamt:", reset_dauer, "->", reset_dauer / max(1, n_games) * 1e6, "us/Reset")
    print("Engine Zuege/Minute:", zuge / engine_dauer * 60)
    print("Encoding Zustands/Minute:", zuge / encode_dauer * 60)


if __name__ == "__main__":
    benchmark_batch()
    benchmark_parallel_envs(5000)
