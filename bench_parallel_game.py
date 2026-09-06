"""Benchmark: Multiprozess-Spielen + Batched-GPU-Update vs. sequenziell.

Vergleicht den vollen Trainingsschritt (Spiele erzeugen + SPIELEN + Encoding +
ein batched GPU-forward/backward/Adam) fuer zwei Varianten:
  - sequenziell: alle Spiele im Hauptprozess, Encoding+Step an einem Ort
  - multiprocess: Worker erzeugen+spielen ihre Spiele, schicken obs als rohe Bytes
Beides auf dem Arc GPU (xpu).
"""
import time
import numpy as np
import torch as T

from Neuralnetwork_Stuff.batched_train import q_grid, best_actions, batched_update, decode_index
from Neuralnetwork_Stuff.qualing_q_learning import DualingQNetwork


def make_games(n, seed):
    import random
    from Klassen.spielinititalisierer import SpielInitialisierer
    from Neuralnetwork_Stuff.storage import Storage
    random.seed(seed)
    games, storages = [], []
    for _ in range(n):
        g = SpielInitialisierer.set_up_game()
        SpielInitialisierer.set_up_fist_moves(g)
        games.append(g); storages.append(Storage(g))
    return games, storages


def net_on(device):
    net = DualingQNetwork(1e-3, "/tmp/b_none.pth"); net.to(device); net.device = T.device(device)
    return net, T.optim.Adam(net.parameters(), lr=1e-3)


def sequential(B, K, device):
    net, opt = net_on(device)
    games, storages = make_games(B, 1)
    states = T.stack([s.initialize_states(g) for s, g in zip(storages, games)]).to(device)
    for _ in range(2):  # warmup
        q = q_grid(net, states); acts = best_actions(q)
        batched_update(net, opt, states, acts, T.zeros(B, device=device), states, device=device)
    t0 = time.perf_counter()
    for _ in range(K):
        q = q_grid(net, states); acts = best_actions(q)
        for i, g in enumerate(games):
            g.play_nn(decode_index(int(acts[i].item())))
        ns = T.stack([s.initialize_states(g) for s, g in zip(storages, games)]).to(device)
        batched_update(net, opt, states, acts, T.zeros(B, device=device), ns, device=device)
        states = ns
    return K / (time.perf_counter() - t0)


def parallel(nw, gpw, K, device):
    from Neuralnetwork_Stuff.parallel_sim import VectorizedParallelSim
    B = nw * gpw
    net, opt = net_on(device)
    sim = VectorizedParallelSim(n_workers=nw, games_per_worker=gpw, seed=1)
    states = T.from_numpy(sim.observe()).to(device)
    for _ in range(2):
        q = q_grid(net, states); acts = best_actions(q)
        obs, done = sim.step(acts.cpu().numpy())
        ns = T.from_numpy(obs).to(device)
        batched_update(net, opt, states, acts, T.zeros(B, device=device), ns, device=device)
        states = ns
    t0 = time.perf_counter()
    for _ in range(K):
        q = q_grid(net, states); acts = best_actions(q)
        obs, done = sim.step(acts.cpu().numpy())
        ns = T.from_numpy(obs).to(device)
        batched_update(net, opt, states, acts, T.zeros(B, device=device), ns, device=device)
        states = ns
    dt = time.perf_counter() - t0
    sim.close()
    return K / dt


if __name__ == "__main__":
    DEVICE = T.device('xpu') if T.xpu.is_available() else T.device('cpu')
    print(f"device = {DEVICE}")
    B, K, nw = 64, 20, 4
    s = sequential(B, K, DEVICE)
    print(f"sequential (B={B}): {s:,.0f} Schritte/s  ({K/s*1000:.2f} ms/Schritt)")
    p = parallel(nw, B // nw, K, DEVICE)
    print(f"multiprocess ({nw} Worker): {p:,.0f} Schritte/s  ({K/p*1000:.2f} ms/Schritt)")
    print(f"-> Multiprozess-Faktor: {p/s:.2f}x")
