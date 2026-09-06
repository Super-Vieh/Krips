"""Multiprozess-Umgebung: Worker erzeugen + SPIELEN eigene Spiele.

Kern: set_up_game()+set_up_fist_moves() ist DB-FREI und seedbar -> jeder Worker
erzeugt eigene befuellte Spiele OHNE DuckDB-Sperre. Worker schicken die
(B,2288)-Beobachtungen als ROH-BYTES (kein Pickle) zurueck; der Hauptprozess
batcht sie und schickt sie an die GPU fuer den naechsten Schritt.

Kommandos an Worker ('reset', seed) / ('step', actions_indices) / ('close').
"""
import multiprocessing as mp
import numpy as np


def _worker(conn, n_games, seed):
    from Klassen.spielinititalisierer import SpielInitialisierer
    from Neuralnetwork_Stuff.storage import Storage

    def make_games(s):
        import random
        from Neuralnetwork_Stuff.reward_engine import RewardEngine
        random.seed(s)
        games, storages, rew = [], [], []
        for _ in range(n_games):
            g = SpielInitialisierer.set_up_game()
            SpielInitialisierer.set_up_fist_moves(g)
            st = Storage(g)
            games.append(g); storages.append(st); rew.append(RewardEngine(g, st))
        return games, storages, rew

    games, storages, rew = make_games(seed)

    def encode():
        import torch as T
        return T.stack([storages[i].initialize_states(g) for i, g in enumerate(games)]).numpy()

    while True:
        msg = conn.recv()
        if msg == 'close':
            break
        if msg[0] == 'reset':
            games, storages, rew = make_games(msg[1])
            conn.send('ok')
        elif msg[0] == 'observe':
            arr = encode()                     # (chunk,2288) ohne zu ziehen
            conn.send_bytes(arr.tobytes())
            conn.send({'shape': arr.shape})
        elif msg[0] == 'step':
            from Neuralnetwork_Stuff.batched_train import decode_index
            acts = msg[1]                     # Liste lokaler Aktions-Indizes
            for li, g in enumerate(games):
                try:
                    g.play_nn(decode_index(acts[li]))
                except Exception:
                    pass
            arr = encode()                     # (chunk,2288) float32
            conn.send_bytes(arr.tobytes())     # roh, kein Pickel
            done = np.array([0.0 if g.gameon else 1.0 for g in games], dtype=np.float32)
            try:
                rwd = np.array([rew[i].reward() for i in range(len(games))], dtype=np.float32)
            except Exception:
                rwd = np.zeros(len(games), dtype=np.float32)
            conn.send({'shape': arr.shape, 'done': done.tobytes(), 'reward': rwd.tobytes()})


class VectorizedParallelSim:
    def __init__(self, n_workers=4, games_per_worker=8, seed=0):
        self.npipes = []
        self.nprocs = []
        self.n_workers = n_workers
        self.games_per_worker = games_per_worker
        for w in range(n_workers):
            parent, child = mp.Pipe()
            p = mp.Process(target=_worker, args=(child, games_per_worker, seed + w * 1000), daemon=True)
            p.start()
            self.npipes.append(parent)
            self.nprocs.append(p)

    def reset(self, seed=0):
        for i, pr in enumerate(self.npipes):
            pr.send(('reset', seed + i * 1000))
        for pr in self.npipes:
            pr.recv()

    def observe(self):
        """Kodiert alle Workergames OHNE zu ziehen -> (B,2288) numpy."""
        obs_parts = []
        for pr in self.npipes:
            pr.send(('observe',))
            b = pr.recv_bytes()
            meta = pr.recv()
            obs_parts.append(np.frombuffer(b, dtype=np.float32).reshape(meta['shape']))
        return np.concatenate(obs_parts)

    def step(self, actions):
        """actions: flache Aktions-Indizes (B,). Gibt (obs, reward, done) numpy zurueck."""
        chunks = [ch.tolist() for ch in np.array_split(actions, len(self.npipes))]
        obs_parts, rwd_parts, done_parts = [], [], []
        for pr, ch in zip(self.npipes, chunks):
            pr.send(('step', ch))
            b = pr.recv_bytes()
            meta = pr.recv()
            obs_parts.append(np.frombuffer(b, dtype=np.float32).reshape(meta['shape']))
            rwd_parts.append(np.frombuffer(meta['reward'], dtype=np.float32))
            done_parts.append(np.frombuffer(meta['done'], dtype=np.float32))
        return (np.concatenate(obs_parts), np.concatenate(rwd_parts), np.concatenate(done_parts))

    def close(self):
        for pr in self.npipes:
            pr.send('close')
        for p in self.nprocs:
            p.join()
