"""Benchmark: Batched-DQN-Schritt CPU vs Intel Arc (xpu).

Zeigt, wo die Zeit im batched Schritt hinfliesst (encode/step vs. NN-Update)
und welchen Gewinn die GPU bringt.
"""
import time
import torch as T

from Datenbank.datenbank import Datenbank
from Klassen.spielinititalisierer import SpielInitialisierer
from Neuralnetwork_Stuff.storage import Storage
from Neuralnetwork_Stuff.qualing_q_learning import DualingQNetwork
from Neuralnetwork_Stuff.batched_train import q_grid, best_actions, decode_index, batched_update


def build_games(n):
    db = Datenbank("Datenbank/krips_replay_store.duckdb")
    games, storages = [], []
    for _ in range(n):
        g, gid = SpielInitialisierer.initialize_game_for_storage(db)
        games.append(g)
        storages.append(Storage(g))
    # db bleibt offen; GC schliesst es
    return games, storages


def encode(games, storages):
    return T.stack([s.initialize_states(g) for s, g in zip(storages, games)])


def bench(B=64, K=30, device='cpu'):
    print(f"\n=== Batched-DQN-Schritt  B={B}  K={K}  device={device} ===")
    games, storages = build_games(B)
    net = DualingQNetwork(1e-3, "/tmp/bench_none.pth")
    net.to(device)
    net.device = T.device(device)   # forward() nutzt self.device -> muss zum Gewicht passen
    opt = T.optim.Adam(net.parameters(), lr=1e-3)
    states = encode(games, storages).to(device)

    # warmup
    for _ in range(3):
        q = q_grid(net, states); acts = best_actions(q)
        next_s = states; rwd = T.zeros(B, device=device)
        batched_update(net, opt, states, acts, rwd, next_s, device=device)

    t_upd = t_step = t_rest = 0.0
    for it in range(K):
        t0 = time.perf_counter()
        q = q_grid(net, states)                      # (B,12,21)
        acts = best_actions(q)                       # (B,)
        t = time.perf_counter()
        # Schritte fuer jedes Spiel (CPU)
        for i, (g, s) in enumerate(zip(games, storages)):
            idx = int(acts[i].item())
            g.play_nn(decode_index(idx))
        next_states = encode(games, storages).to(device)
        rwd = T.zeros(B, device=device)
        t_step += time.perf_counter() - t
        t_rest += time.perf_counter() - t0
        # der eigentliche GPU-/NN-Update
        u0 = time.perf_counter()
        batched_update(net, opt, states, acts, rwd, next_states, device=device)
        t_upd += time.perf_counter() - u0
        states = next_states

    per = (t_step + t_upd) / K * 1000
    print(f"  Gesamt pro Schritt : {per:8.2f} ms  ({K/per*1000:,.0f} Schritte/s)")
    print(f"   - NN-Update (forward+backward+Adam): {t_upd/K*1000:8.2f} ms  ({t_upd/(t_step+t_upd)*100:.0f}%)")
    print(f"   - Spielschritt + Encoding (CPU)     : {t_step/K*1000:8.2f} ms")
    return (t_step + t_upd) / K


if __name__ == "__main__":
    cpu_ms = bench(B=64, K=30, device='cpu')
    try:
        if T.xpu.is_available():
            gpu_ms = bench(B=64, K=30, device='xpu')
            print(f"\n>>> GPU-Beschleunigung (xpu): {cpu_ms:g} ms -> {gpu_ms:g} ms  = {cpu_ms/gpu_ms:.2f}x")
        else:
            print("\n>>> xpu nicht verfügbar -> nur CPU-Benchmark")
    except Exception as e:
        import traceback; traceback.print_exc()
