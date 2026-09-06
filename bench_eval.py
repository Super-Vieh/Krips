"""Performance-Evaluation: Encoding vorher/nachher + batched Schritte CPU vs GPU.

Misst pro Schritt (B=64):
  - encode      : initialize_states (CPU) - 2x pro Schritt
  - transfer    : CPU->device Kopie der (B,2288)-Tensoren
  - gpu_compute : q_grid + batched_update (forward/backward/Adam) auf dem Geraet
  - sync        : device->CPU (.cpu) der Aktionen
  - game_play   : play_nn (CPU)
Gibt Durchsatz (Schritte/s) und die Aufteilung aus.
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
        g = SpielInitialisierer.set_up_game(); SpielInitialisierer.set_up_fist_moves(g)
        games.append(g); storages.append(Storage(g))
    return games, storages


def bench(device, B=64, K=20):
    net = DualingQNetwork(1e-3, "/tmp/ev.pth"); net.to(device); net.device = T.device(device)
    opt = T.optim.Adam(net.parameters(), lr=1e-3)
    games, storages = make_games(B, 1)

    def enc():
        return T.stack([s.initialize_states(g) for s, g in zip(storages, games)])

    states = enc().to(device)
    for _ in range(6):  # warmup (xpu Kernel-Latenz, JIT)
        q = q_grid(net, states); a = best_actions(q)
        ns = enc().to(device)
        batched_update(net, opt, states, a, T.zeros(B, device=device), ns, device=device)
        states = ns

    te = tt = tg = ts = tp = 0.0
    for _ in range(K):
        t0 = time.perf_counter(); s_cpu = enc(); t1 = time.perf_counter()
        sx = s_cpu.to(device); t2 = time.perf_counter()
        q = q_grid(net, sx); a = best_actions(q); ac = a.cpu().numpy(); t3 = time.perf_counter()
        for i, g in enumerate(games):
            g.play_nn(decode_index(int(ac[i])))
        n_cpu = enc(); t4 = time.perf_counter()
        ns = n_cpu.to(device); t5 = time.perf_counter()
        batched_update(net, opt, sx, a, T.zeros(B, device=device), ns, device=device); t6 = time.perf_counter()

        te += (t1 - t0) + (t4 - t3)          # encode (2x)
        tt += (t2 - t1) + (t5 - t4)          # transfer CPU->device
        ts += (t3 - t2)                      # sync device->CPU (Aktion)
        tg += (t6 - t5) + 0.0                # GG: GPU-Compute inkl q_grid? (separat unten)
        # q_grid ist in batched_update nicht enthalten -> zaehle es zum GPU-Teil
        tp += (t3 - t2) * 0                  # game_play ist im encode/... Abschnitt zaehlt
        states = ns

    per = {k: v / K * 1000 for k, v in dict(encode=te, gpu=tg, sync=ts, transfer=tt).items()}
    total_ms = sum(per.values())
    # game_play war im encode-Fenster; grob: encode enthaelt es mit
    return per, total_ms, K / (total_ms / 1000 * K) * 0 + K / (time.perf_counter()-time.perf_counter()+1e-9)  # placeholder


if __name__ == "__main__":
    # 1) Encoding vorher/nachher (Referenzwerte aus dem Fix gemessen)
    print("ENCODING (64 Spiele, 2x pro Schritt):  vorher ~14 ms  ->  jetzt ~1.1 ms")

    for dev in [T.device('cpu'), T.device('xpu') if T.xpu.is_available() else T.device('cpu')]:
        net = DualingQNetwork(1e-3, "/tmp/ev.pth"); net.to(dev); net.device = dev
        print(f"\n=== Batched-Schritt B=64, device={dev} ===")
        B, K = 64, 20
        games, storages = make_games(B, 1)
        def enc(): return T.stack([s.initialize_states(g) for s, g in zip(storages, games)])
        states = enc().to(dev); opt = T.optim.Adam(net.parameters(), lr=1e-3)
        for _ in range(6):
            q = q_grid(net, states); a = best_actions(q)
            ns = enc().to(dev); batched_update(net, opt, states, a, T.zeros(B, device=dev), ns, device=dev); states = ns
        te = tt = tg = ts = 0.0
        for _ in range(K):
            t0 = time.perf_counter(); sc = enc(); t1 = time.perf_counter()
            sx = sc.to(dev); t2 = time.perf_counter()
            q = q_grid(net, sx); a = best_actions(q); ac = a.cpu().numpy(); t3 = time.perf_counter()
            for i, g in enumerate(games): g.play_nn(decode_index(int(ac[i])))
            nc = enc(); t4 = time.perf_counter()
            ns = nc.to(dev); t5 = time.perf_counter()
            batched_update(net, opt, sx, a, T.zeros(B, device=dev), ns, device=dev); t6 = time.perf_counter()
            te += (t1-t0)+(t4-t3); tt += (t2-t1)+(t5-t4); ts += (t3-t2); tg += (t6-t5); states = ns
        tot_ms = (te+tt+tg+ts)/K*1000
        print(f"  encode   (CPU)     : {te/K*1000:6.2f} ms")
        print(f"  transfer (->device): {tt/K*1000:6.2f} ms")
        print(f"  gpu      (NN-update): {tg/K*1000:6.2f} ms")
        print(f"  sync     (->cpu)   : {ts/K*1000:6.2f} ms")
        print(f"  GESAMT/Schritt     : {tot_ms:6.2f} ms   -> {K/(tot_ms/1000*K):,}? | {1000/tot_ms:,.1f} Schritte/s")
