# Performance-Optimierung des Krips-RL-Systems

_Branch: `wip/overfit-explore-ansatz1` · Stand: 2026-09-03_

Dieses Dokument hält alle Änderungen dieser Session fest — jeweils mit **Problem → Änderung → Ergebnis**, dem Kontext dahinter und den gemessenen Zahlen (B=64-Spiel-Batch, Intel-Arc-GPU, `.venv` mit `torch 2.9.1`).

---

## 1. Ausgangslage & Ziel

Das Krips-RL-System spielte Karten-Spiele mit einem Dueling-DQN (`DualingQNetwork`, 7.38 M Parameter, 2288-dim Beobachtung, 12×21-Aktions-Grid). Ausgangsproblem: **Training extrem langsam** — ein einziges Spiel, seriell auf der CPU, mit vollem Netz-Training pro Zug.

**Ziel:** Die Spiele und das Spielen **parallelisieren** und den teuren NN-Teil **batchen + auf GPU** verlagern, um den Engpass (CPU/Netz) zu beseitigen.

---

## 2. Zusammenfassung Vorher / Nachher

| Metrik | Vorher | Nachher | Faktor |
|---|---|---|---|
| Durchsatz (Züge/s) | **10** | **9.496** (B=640, GPU) | **~946×** |
| Encoding (1 Spiel) | 0,223 ms | 0,019 ms | **12,5×** |
| Encoding (64 Spiele) | ~14 ms | 1,1 ms | **12,7×** |
| NN-Update (batch 64) | 363,6 ms (CPU) | 16,7 ms (GPU) | **~22×** |
| Batched-Schritt (B=64) | 407,6 ms (CPU) | 32,3 ms (GPU) | **12,6×** |
| GPU-Compute-Skalierung | — | ~17–20 ms (flat) | latency-gebunden |

---

## 3. Diagnose: Wo die Zeit verloren ging (der Weg zum Engpass)

Am Anfang analysierte ich das System mit einem Profiler (PyCharm-Statistik). Ergebnis pro Trainingsschritt:

- `run_backward` (Autograd): **29,8 %**
- `_single_tensor_adam` (Optimizer, kumulativ): **53,1 %**
- `linear` (Forward-Matmul): 12,0 %
- Die Elementwise-Ops (`sqrt`, `lerp`, `addcdiv`, `mul`, `addcmul`, `add`) mit ~25.000 Aufrufen: **Adam pro Parameter-Tensor**

**Diagnose:** ~95 % der Zeit war **reines Netz-Training** (forward+backward+Adam) — die Spiel-Logik und das Encoding tauchten im Profiler gar nicht auf. Der **Engpass war das serielle, einzel-spielige, CPU-Netz-Training**, nicht das Spiel.

Daraus ergaben sich drei Hebel: **batching + GPU + Encoding-Fix**.

---

## 4. Die einzelnen Änderungen

### 4.1 Hänger-Fix (`agent.py`)

**Problem:** `train_one_turn_storage` / `train_one_turn_replay` endeten nie (Hänger).

**Kontext:** Der innere `while self.game.current == self.spieler and self.game.gameon` hatte keine Abbruchbedingung, weil `Spiel.play_nn()` / `case_*` **nie `game.current` wechseln** und das (tote) `Spiel.game_ended()` **nie aufgerufen** wird → `gameon` blieb `True` und `current` wechselte nie. Ein Profil-Lauf hing deshalb in den Time-out.

**Änderung:** `game_ended()` nach jedem Zug wirklich aufrufen + `max_turn_moves = 100` als Sicherheitsgrenze in beiden Trainingsmethoden.

**Ergebnis:** Kein Hänger mehr; Trainingslauf beendet sauber.

---

### 4.2 Batch-fähiges Netz (`qualing_q_learning.py`)

**Problem:** Das Netz verarbeitete nur **einen** Zustand (`(2288,)`, 1D). Ein Batch `(B,2288)` brach ab.

**Kontext:** `forward` nutzte `T.cat(..., dim=0)` (für 1D korrekt = Feature-Konkatenation 12+256=268), `combine_value_advantage` nutzte `unsqueeze(1)/(0)` — beides nur für `N=1` gültig. Für einen echten Batch brauchte es `dim=1` und `unsqueeze(2)/(1)`.

**Änderung:** `forward` normalisiert 1D→2D (`unsqueeze(0)`) und nutzt `cat dim=1`; `combine` broadcastet über den Batch (`unsqueeze(2)/(1)`, `value.unsqueeze(2)`), sodass `(B,2288) → (B,12,21)` funktioniert — während der Single-Pfad weiterhin `(12,21)` liefert.

**Ergebnis:** **`(100,2288) → (100,12,21)` in einem forward.** Verifiziert: B=1 → `(12,21)` (unverändert), B=100 → `(100,12,21)`.

> ⚠️ **Korrektur-Kontext:** Ich "fixte" anfangs fälschlich `cat`/`unsqueeze` als Bug (weil ich mit `(1,2288)`-2D testete). Der reale Pfad übergibt aber 1D `(2288,)` — der Original-Code war für 1D korrekt. Ich **revertierte** meine falschen Änderungen und baute stattdessen die **batch-robuste** Normalisierung (1D→2D) ein, die beide Fälle abdeckt.

---

### 4.3 GPU-Anbindung (Intel Arc 140V, `xpu`)

**Problem** / **Kontext:** Dein `torch 2.9.1+cu128` ist der NVIDIA-CUDA-Stack und sieht die **Intel Arc 140V** (Lunar Lake iGPU) nie (`cuda_available=False`). Die Arc ist ein Intel-Device → braucht den **`xpu`-Stack** (`torch 2.9.1+xpu`, Intel-PyTorch).

**Änderungen:**
1. System-Driver (Level Zero `libze_intel_gpu.so`, OpenCL-ICD, `renderD128`) waren bereits vorhanden → **nichts zu installieren**.
2. `torch 2.9.1+xpu` ins venv installiert (ersetzt `+cu128`, gleiche Version). Wichtig: nur `--extra-index-url https://download.pytorch.org/whl/xpu` (nicht `--index-url`, sonst fehlen torch-Deps). Der erste Versuch schlug fehl, weil ich `torch==2.9.1` statt `torch==2.9.1+xpu` installierte (der `+xpu`-Local-Version-Tag passt nicht zu `==2.9.1`).
3. Device-Selektion in `qualing_q_learning.py`: `xpu → cuda → cpu` mit `hasattr`-Guard.

**Ergebnis:** `torch.xpu.is_available() = True`, Gerät `Intel(R) Arc(TM) Graphics`, forward auf `xpu:0` funktioniert. **Batched-Schritt 12,6× schneller als CPU**, NN-Update allein **~22×**.

> ⚠️ **Design-Fund:** `self.device` wird einmal gecacht; `net.to(device)` bewegt Gewichte, ohne `self.device` zu aktualisieren → im Benchmark musste `net.device` manuell mitgezogen werden. Für die bestehende Single-Game-Schleife ist das ein Kandidat für Device-Mismatch in `compute_loss`.

---

### 4.4 Encoding-Optimierung (`storage.py`)

**Problem:** `initialize_states` kostete 0,22 ms pro Spiel (14 ms für 64) — obwohl es nur ~104 Karten iteriert.

**Kontext / Dissektion:** Ich zählte die Operationen und decomponierte:
- 104 Karten iterieren + Attribute lesen → **0,01 ms** (die echte Encoding-Arbeit ist fast gratis)
- 44× `[0]*52` allokieren → 0,01 ms
- `states +=` konkatenieren → 0,01 ms
- **`T.tensor([2288])` (Python-Liste → Tensor) → 0,14 ms** ← **der eigentliche Kostenfaktor (64 %)**

Das Encoding selbst war also fast nichts; der teure Teil war die **Umwandlung der Python-Liste in einen Torch-Tensor**.

**Änderung:** Statt Python-Liste + `T.tensor(list)` direkt in ein `numpy`-Array `np.zeros(2288)` schreiben und per `torch.from_numpy` (kein Copy) zurückgeben. `_SUIT` einmalig als Modul-Konstante (statt 44× `dict_suit`-Neuaufbau pro Spiel).

**Ergebnis:** 0,223 ms → **0,019 ms** pro Spiel (**12,5×**), 64 Spiele 14 ms → **1,1 ms**. Korrektheit identisch (`max diff = 0.0`).

---

### 4.5 Multiprocessing-Untersuchung (`parallel_sim.py`)

**Ziel:** Spiele + Spielen in Worker-Prozesse, Beobachtungen gebatcht an die GPU.

**Befunde (jeweils Problem → Erkenntnis):**

1. **DuckDB-Ein-Schreiber-Sperre:** Jeder Worker, der `initialize_game_for_storage` aufrief, kollidierte mit dem DB-Lock (`Conflicting lock`). → **DB-freier Deal nötig.** Lösung: `set_up_game()` + `set_up_fist_moves()` ist **DB-frei und seedbar** (`random.seed`) — jeder Worker erzeugt eigene Spiele ohne DB.
2. **Fork-COW beim `step`:** Mit `fork` erbt der Worker eine Kopie; Mutationen (Spiel-Züge) propagieren **nicht** zum Hauptprozess. → Multiprocessing funktioniert sauber nur, wenn ein Worker seine Spiele **selbst besitzt** (read-only Encoding ok, `step` geht nicht über geteilte Objekte).
3. **Pickle vs. rohe Bytes (der eigentliche Transfer-Befund):** Die `(B,2288)`-Observations sind klein (1 Obs = 8,9 KB, 64 = 590 KB, pro Worker 147 KB). Aber das **Pickling einer Tensor-Liste** kostet **8,46 ms pro 16 Obs**, als **rohe Bytes** (`send_bytes`) nur **0,85 ms** → **10× schneller**.

**Ergebnis des Vergleichs:**
- Encoding parallel (4 Worker, read-only): 14,7 → **9,8 ms (1,5×)**.
- Mit **rohen Bytes**: Gesamt ≈ **13,2 ms < 14,7 ms** → Multiprocessing **~1,1× besser** (marginal).
- **Aber:** Der volle Sim-Stepp (Mutation) scheitert an fork-COW; und auf GPU bleibt der **Host→GPU-Transfer** der Observations bestehen.

**Schluss:** Multiprocessing ist zum reinen read-only-Encoding mit Shared-Memory/rohen Bytes **~1,1×** — kein großer Hebel. Der Transfer/`all_states` bleibt der Engpass → **tensorisierte Engine** nötig, um Transfer komplett zu eliminieren.

---

### 4.6 Batch-Skalierung

**Frage:** Wie skaliert die Zeit mit größeren Batches?

**gemessen (GPU):**

| B | Schritt | Züge/s | encode | transfer | gpu | sync |
|---|---|---|---|---|---|---|
| 64 | 36 ms | 1.768 | 5,7 | 6,0 | 20,3 | 4,2 |
| 320 | 57 ms | 5.565 | 28,0 | 4,2 | 19,9 | 5,3 |
| 640 | 67 ms | 9.496 | 38,4 | 5,2 | 17,0 | 6,7 |
| 1024 | 99 ms | 10.390 | 34 | 43 | 8 | 13 |
| 5120 | 429 ms | 11.930 | **189** | **164** | 20 | 57 |

**Erkenntnisse:**
- **GPU-Compute bleibt ~17–20 ms flat** → die iGPU ist **latency-gebunden**, nicht compute-gebunden (schon ein triviales `(64,2288).sum()` kostet ~19 ms Launch-Latenz). Dadurch: **10× Batch = 5,4× mehr Züge/s** (GPU wird pro Batch amortisiert).
- **Encoding + Transfer skalieren mit B** → bei B=5120 dominiert die CPU-Seite (encode 189 + transfer 164 = **82 %**).
- **Sweet-Spot: B ≈ 320–640** (5.565–9.496 Züge/s) — darüber abnehmender Ertrag + Sprengung von Speicher/Transfer.

---

### 4.7 `train_agents_batched` + TensorBoard (`agent_trainer.py`, `tensor_metric_board.py`, `main.py`)

**Ziel:** Der batched Ansatz als Aufruf wie die anderen (`train_agents_and_store` / `_replay`).

**Änderungen:**
- `AgentTrainer.train_agents_batched(nr_episodes, steps, batch_size, start_epsilon, discount_factor, epsilon_decay, n_workers)`: erzeugt `VectorizedParallelSim` (N Worker, DB-frei, seedbar), macht pro Schritt **ein batched GPU-Update** (`batched_update`), ε-greedy, speichert das Netz am Ende.
- `TensorMetricBoard.log_episode(...)`: schreibt pro Episode `episode/made_moves`, `episode/total_reward`, `episode/total_loss`, `episode/epsilon` + gibt eine Zeile pro Episode aus.
- `VectorizedParallelSim.step` liefert jetzt `(obs, reward, done)` (Belohnung aus `RewardEngine` pro Spiel, rohe Bytes).
- `main.py`: Aufruf neben den anderen (Store kommentiert).

**Ergebnis:** Läuft stabil (5 Episoden, 7,3 s, Worker räumen sauber auf). TensorBoard zeigt pro Episode `episode/*`.

> ⚠️ **Ehrlich:** Es läuft **mechanisch**, aber die Spiele enden nie (`done` bleibt `False`), weil **ohne Legal-Mask** der Agent viele illegale/no-op-Züge macht → Reward stark negativ (−6.400), Loss lernt nur „vermeide illegale Züge". Für echtes Spielen fehlen **Legal-Mask** und **Terminal**.

---

### 4.8 Gym-Umgebung (Design-Entscheidung)

**Kernfrage:** Zerstört Batching/Parallelisierung die Gym-Schnittstelle? **Nein.**

**Prinzip (Trennung der Zuständigkeiten):**
```
Policy (RL-Agent / MinMax / MCTS / Mensch)
        │  obs → action → (obs, reward, terminated, truncated, info)
Einzel-Env  KripsEnv  (die Gym-Schnittstelle, policy-agnostisch)
        │  optional im Training
Vektorisierungs-Schicht (multiprocessing + batched GPU)   ← nur zum Trainieren
```

**Ergebnis:**
- **Trainieren (Batching/GPU EIN):** viele `KripsEnv` parallel via Vektor-Wrapper + Multiprozess.
- **MinMax-Baum/MCTS/Bots (Batching AUS):** **eine** `KripsEnv`-Instanz, synchron — gleiche Schnittstelle, keine Änderung.
- **Jede Policy** (RL, MinMax, MCTS, Mensch) nutzt nur `obs` → `action` → `step` — die Env kennt die Policy nicht.

**Voraussetzungen (noch offen):** Einzel-`KripsEnv` sauber herauslösen (aktuell ist `VectorizedParallelSim` die vektorisierte Schicht), `gymnasium` installieren, MDP-Semantik (Legal-Mask/Terminal) fixen.

---

## 5. Alle Zeitmessungen (Übersicht)

**GPU-Lauf pro Schritt (B=64) — Aufteilung nach CPU/GPU/Transfer:**

| Teil | Wo | Zeit | Anteil |
|---|---|---|---|
| Spiel-Logik `play_nn` | CPU | 0,91 ms | 3 % |
| Encoding (2×) | CPU | 4,93 ms | 14 % |
| **CPU gesamt** | | **5,84 ms** | 17 % |
| Transfer CPU→GPU | | 5,96 ms | 17 % |
| Sync GPU→CPU | | 1,32 ms | 4 % |
| select-forward | GPU | 2,72 ms | 8 % |
| update (fwd+bwd+Adam) | GPU | 19,52 ms | 55 % |
| **GPU gesamt** | | **22,23 ms** | 63 % |

**Durchsatz am Anfang vs. jetzt:**
| Version | Züge/s | Faktor |
|---|---|---|
| Original (1 Spiel, CPU) | 10 | 1× |
| Batched GPU, B=64 | 1.768 | ×176 |
| Batched GPU, B=640 | 9.496 | ×946 |

---

## 6. Technische Erkenntnisse (die wichtigsten)

1. **Die iGPU (Arc 140V) ist latency-gebunden** für diese Workload: ~19 ms Launch-Latenz pro Op, auch bei trivialem Compute. Daher bringt größeres B keinen/schwachen GPU-Compute-Zuwachs, aber amortisiert die Latenz → **5,4× mehr Züge/s bei 10× Batch**.
2. **DuckDB ist Ein-Schreiber** → Worker können nicht parallel aus der DB initiieren. **DB-freier, seedbarer Deal** (`set_up_game`+`set_up_fist_moves`) nötig.
3. **`torch.from_numpy` statt `T.tensor(list)`** ist der entscheidende Encoding-Fix (0,14 ms → ~0).
4. **Pickle-vs-Byte-Transfer:** Observations sind klein (590 KB), aber das Pickling einer Tensor-Liste kostet 10× mehr als rohe Bytes → Transfer ist nur wegen Pickling teuer, nicht wegen der Bytes.
5. **`Storage.all_states`-Seiteneffekt** (`RewardEngine` hängt bei jedem Schritt an) wächst pro Episode → bei langen Episoden speicherlastig (REW-02 aus dem Requirements-Katalog).

---

## 7. Geänderte / neue Dateien

**Geändert:**
- `Neuralnetwork_Stuff/agent.py` — Hänger-Fix (`game_ended()` + `max_turn_moves`)
- `Neuralnetwork_Stuff/qualing_q_learning.py` — batch-fähiges `forward`/`combine` + `xpu`-Device-Selektion
- `Neuralnetwork_Stuff/storage.py` — Encoding-Optimierung (numpy-direct + `from_numpy`)
- `Neuralnetwork_Stuff/tensor_metric_board.py` — `log_episode`
- `Neuralnetwork_Stuff/agent_trainer.py` — `train_agents_batched`
- `main.py` — Aufruf `train_agents_batched`

**Neu:**
- `Neuralnetwork_Stuff/batched_train.py` — `q_grid`, `best_actions`, `decode_index`, `batched_update`
- `Neuralnetwork_Stuff/parallel_sim.py` — `VectorizedParallelSim` (Multiprozess, DB-frei)
- `bench_batch.py`, `bench_eval.py`, `bench_parallel_game.py` — Benchmarks
- `docs/gym_krips/` — LaTeX-Studien-Dokument zu Gymnasium + Krips-Requirements

**Umgebung:** `torch 2.9.1+cu128` → `torch 2.9.1+xpu` (Intel-Stack).

---

## 8. Offene Punkte & Empfehlungen

1. **Legal-Action-Mask (ACT-03):** aus `overfit_experiment.legal_actions()` batchfähig — Agent wählt nur legale Züge → Spiele schreiten fort, `terminated` feuert, Reward wird aussagekräftig.
2. **Echtes Terminal (TER-01..03) + Terminal-Reward (REW-06):** `game_ended()`/`is_stalemate()` aufrufen — sonst enden Episoden nie.
3. **Reward-Purity (REW-02):** `all_states`-Seiteneffekt entfernen — sonst Speicherwachstum pro Episode.
4. **gymnasium installieren + Einzel-`KripsEnv` herauslösen** für eine saubere, policy-agnostische Gym-Schnittstelle (RL + MinMax/MCTS auf derselben Env).
5. **Tensorisierte Engine** (Zustand als Tensoren auf dem Gerät) wäre der einzige Weg, den **Encoding+Transfer**-Engpass bei großem B zu eliminieren → dann skaliert B ~linear mit Züge/s.
