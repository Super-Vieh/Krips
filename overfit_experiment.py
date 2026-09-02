#!/usr/bin/env python3
"""
Overfit-Experiment für Krips (Dueling DQN).

Ablauf
------
Phase 1: Ein Spiel mit `TARGET_MOVES` validen Zügen generieren (legaler
         Zug-Generator, ohne Neuronales Netz) und in der DuckDB speichern.
         Zusätzlich wird die Zustandsfolge mitgespeichert und auf Aliasing
         geprüft (derselbe 1144-Bit-Vektor mit verschiedenen Folge-Zügen).

Phase 2: Ein frisches Dueling-DQN ausschließlich auf diesem EINEN Spiel
         trainieren (Replay über `EPOCHS` Epochen) und messen:
           - Trainings-Loss   (sollte gegen ~0 gehen, wenn es memorisiert)
           - Trefferquote     (Anteil der Schritte, bei denen argmax Q ==
                               der aufgezeichnete Zug ist)

Overfit-Kriterium
-----------------
  Trefferquote >= OVERFIT_ACC  UND  Loss <= OVERFIT_LOSS  => overfittet.

Bedeutung des Ergebnisses
-------------------------
- Overfittet  : Das Netz kann das einzelne Spiel memorieren -> State-
                Repräsentation ist ausreichend, Lernmechanik funktioniert.
- Nicht        : Indiz für eine mehrdeutige State-Repräsentation (der
  overfittet     1144-Bit-Vektor verschweigt verdeckte Karten, Stapel-Längen
                 und Historie) oder für instabiles Training. Die Diagnose
                 zeigt dann, ob Aliasing die perfekte Memorierung
                 prinzipiell unmöglich macht.

Hinweis: Der bestehende `Agent.update_network()` hat eine falsche Signatur
(TypeError); dieses Skript macht die Optimizer-Schritte direkt.
"""

import os
import random
import sys
import argparse
import io
from contextlib import contextmanager, redirect_stdout

import torch as T

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Datenbank.datenbank import Datenbank
from Klassen.spielinititalisierer import SpielInitialisierer
from Neuralnetwork_Stuff.qualing_q_learning import DualingQNetwork
from Neuralnetwork_Stuff.storage import Storage
from Neuralnetwork_Stuff.reward_engine import RewardEngine

DB_PATH = "Datenbank/krips_replay_store.duckdb"
TARGET_MOVES = 100
MAX_GEN_STEPS = 30000
MAX_GEN_ATTEMPTS = 12
EPOCHS = 120
LR = 0.001
DISCOUNT = 0.9
PRINT_EVERY = 10
OVERFIT_ACC = 0.90
OVERFIT_LOSS = 0.05
EARLY_STOP_EPOCHS = 8

# Aktionen -> Indizes (identisch zu Agent.select_action)
DICT_ACT1 = {0: "K0", 1: "S1", 2: "S2", 3: "S3", 4: "S4", 5: "S5",
             6: "S6", 7: "S7", 8: "S8", 9: "A0", 10: "A1", 11: "A2"}
DICT_ACT2 = {0: "K0", 1: "S1", 2: "S2", 3: "S3", 4: "S4", 5: "S5",
             6: "S6", 7: "S7", 8: "S8", 9: "M1", 10: "M2", 11: "M3",
             12: "M4", 13: "M5", 14: "M6", 15: "M7", 16: "M8",
             17: "A0", 18: "A1", 19: "A2", 20: "G0"}


@contextmanager
def silence():
    """Unterdrückt stdout (die DB-/Spiel-Module drucken lautstarke Dumps)."""
    with redirect_stdout(io.StringIO()):
        yield


# ---------------------------------------------------------------------------
# Phase 1: legaler Zug-Generator
# ---------------------------------------------------------------------------

def _own_piles(game):
    """[Päckchen, Haufen, Dreizehner] des Spielers, der am Zug ist."""
    p = game.current
    return game.spieler1listen if p.spielernummer == 1 else game.spieler2listen


def _can_place_middle(p, card, stelle):
    """Spiegelt die Regeln von Spieler.mitteHinlegen (inkl. Ass-Sonderfall)."""
    midliste = p.game.mittlereliste[stelle - 1]
    if card.kartenwert.value == 1:
        if len(midliste) != 0:
            return False
        return ((stelle in (1, 2) and card.kartentyp.value == "Pik") or
                (stelle in (3, 4) and card.kartentyp.value == "Coeur") or
                (stelle in (5, 6) and card.kartentyp.value == "Treff") or
                (stelle in (7, 8) and card.kartentyp.value == "Karro"))
    return p.kannMitteHinlegen(card, stelle)


def legal_actions(game):
    """Alle Aktionen, die im aktuellen Zustand etwas bewirken (legal)."""
    p = game.current
    paechen, haufen, drz = _own_piles(game)
    actions = []

    # Aufdecken (nur wenn die oberste Karte noch zugeklappt ist -> bewirkt etwas)
    if paechen and not paechen[-1].karteOffen:
        actions.append("A0A0")
    if drz and not drz[-1].karteOffen:
        actions.append("A2A2")

    # Zug beenden (oberste Päckchen-Karte -> Haufen) bzw. Haufen neu mischen
    # ("A0A1" löst bei leerem Päckchen automatisch resetHaufen aus)
    if (paechen and paechen[-1].karteOffen) or not paechen:
        actions.append("A0A1")

    # Offene Quellkarten sammeln
    sources = []
    if paechen and paechen[-1].karteOffen:
        sources.append(("A0", paechen[-1]))
    if drz and drz[-1].karteOffen:
        sources.append(("A2", drz[-1]))
    if haufen and haufen[-1].karteOffen:
        sources.append(("A1", haufen[-1]))
    for i, sl in enumerate(game.platzliste):
        if sl and sl[-1].karteOffen:
            sources.append((f"S{i + 1}", sl[-1]))

    for src, card in sources:
        # auf Foundation (Mitte)
        for j in range(1, 9):
            if _can_place_middle(p, card, j):
                actions.append(f"{src}M{j}")
        # auf Seitenplätze (inkl. leerer Plätze)
        for j in range(1, 9):
            if src == f"S{j}":
                continue
            sl = game.platzliste[j - 1]
            if (not sl) or p.kannSeiteHinlegen(card, j):
                actions.append(f"{src}S{j}")
        # auf den Ablagehaufen des Gegners
        if p.kann_gegener_geben(card):
            actions.append(f"{src}G0")
    return actions


def _weight(action, last_action=None):
    # Priorität des Spiels: Mitte zuerst, dann aufdecken/Karte ablegen,
    # dann Gegner, dann Seite-zu-Seite, dann Stopp.
    if action[2] == "M":
        return 10
    if action in ("A0A0", "A2A2"):
        return 5
    if action[2] == "G":
        return 3
    if action[2] == "S" and action[0] in ("A",):
        return 4          # aufgedeckte Karte auf Seitenplatz legen: gut
    if action[2] == "S":
        # Seite-zu-Seite: direktes Rückgängigmachen vermeiden
        if last_action is not None and len(action) == 4 and len(last_action) == 4 \
                and action[0:2] == last_action[2:4] and action[2:4] == last_action[0:2]:
            return 1      # genau das Gegenteil des letzten Zuges -> fast nie
        return 2
    return 1


def pick_move(game, last_action=None):
    actions = legal_actions(game)
    if not actions:
        return None
    weights = [_weight(a, last_action) for a in actions]
    return random.choices(actions, weights=weights, k=1)[0]


def generate_and_store_game(db, target_moves=TARGET_MOVES):
    """Generiert ein Spiel, speichert es und liefert (gid, moves, state_keys)."""
    attempted_ids = []
    for attempt in range(1, MAX_GEN_ATTEMPTS + 1):
        with silence():
            game, gid = SpielInitialisierer.initialize_game_for_storage(db)
        attempted_ids.append(gid)
        storage = Storage(game)
        recorded = []
        state_keys = []
        steps = 0
        while len(recorded) < target_moves and game.gameon and steps < MAX_GEN_STEPS:
            steps += 1
            before = storage.initialize_states(game)
            state_keys.append(tuple(before.tolist()))
            last_action = recorded[-1] if recorded else None
            action = pick_move(game, last_action)
            if action is None:
                break
            with silence():
                game.play_nn(action)
            after = storage.initialize_states(game)
            if not T.equal(before, after):
                recorded.append(action)
        print(f"[Phase 1] Versuch {attempt}/{MAX_GEN_ATTEMPTS}: {len(recorded)}/{target_moves} "
              f"valide Züge | Spiel zu Ende={not game.gameon} | Schritte={steps}")
        if len(recorded) >= target_moves:
            db.save_game_moves(recorded, gid)
            # Aufräumen: fehlgeschlagene Versuche aus StartingCards entfernen
            for bad in attempted_ids:
                if bad != gid:
                    db.connection.execute("DELETE FROM StartingCards WHERE GAME_ID = ?", (bad,))
            return gid, recorded, state_keys
    raise RuntimeError(f"Kein Spiel mit >= {target_moves} Zügen in {MAX_GEN_ATTEMPTS} Versuchen erzeugt")


def analyze_aliasing(moves, state_keys):
    """Prüft, ob derselbe 1144-Bit-Zustand mit verschiedenen Folge-Zügen kollidiert."""
    state_to_actions = {}
    for key, action in zip(state_keys, moves):
        state_to_actions.setdefault(key, set()).add(action)
    collisions = {k: v for k, v in state_to_actions.items() if len(v) > 1}
    n = len(moves)
    max_acc = (n - sum(len(v) - 1 for v in collisions.values())) / n if n else 0.0
    print("[Diagnose]")
    print(f"  Transitionen                : {n}")
    print(f"  Eindeutige Zustände         : {len(state_to_actions)}")
    print(f"  Zustände mit Aliasing       : {len(collisions)} "
          f"({len(collisions) / max(len(state_to_actions), 1) * 100:.1f} % der Zustände)")
    print(f"  Theoretisch max. Trefferquote (durch Aliasing begrenzt): {max_acc * 100:.1f} %")
    return max_acc


# ---------------------------------------------------------------------------
# Phase 2: Overfit-Training auf dem EINEN Spiel
# ---------------------------------------------------------------------------

def load_replay(db, gid):
    with silence():
        moves = db.load_game_moves(gid)
        game = SpielInitialisierer.initialize_game_for_replay(db, gid)
    return game, moves


def collect_state_keys(db, gid, moves):
    """Replay des Spiels und Sammeln aller Zustands-Schlüssel (für Aliasing-Analyse)."""
    game, _ = load_replay(db, gid)
    storage = Storage(game)
    keys = []
    for action in moves:
        keys.append(tuple(storage.initialize_states(game).tolist()))
        with silence():
            game.play_nn(action)
    return keys


def greedy_action(nn, state):
    """Greedy-Aktion (argmax Q) ohne den fehlerhaften Agent.select_action."""
    value, adv1, adv2 = nn.forward(state)
    q = nn.combine_value_advantage(value, adv1, adv2).detach().clone()
    q[0, 0] = -float("inf")  # K0K0 ausblenden
    flat = q.reshape(-1)
    best = int(flat.argmax().item())
    n, m = divmod(best, 21)
    return DICT_ACT1[n] + DICT_ACT2[m]


def compute_loss(nn, state, action1, action2, reward, next_state, done, discount):
    value, adv1, adv2 = nn.forward(state)
    q = nn.combine_value_advantage(value, adv1, adv2)
    predicted = q[action1, action2]
    value2, adv12, adv22 = nn.forward(next_state)
    q2 = nn.combine_value_advantage(value2, adv12, adv22)
    target = reward + discount * q2.max() * (1 - int(done))
    return nn.loss(predicted, target)


def run_overfit_training(db, gid, moves, epochs=EPOCHS):
    nn = DualingQNetwork(LR, "tmp_overfit_net.pt")
    history = []
    for ep in range(1, epochs + 1):
        game, _ = load_replay(db, gid)
        storage = Storage(game)
        reward_engine = RewardEngine(game, storage)
        remaining = list(moves)
        correct = 0
        total_loss = 0.0
        total_reward = 0.0
        n = 0
        while remaining:
            action = remaining.pop(0)
            states = storage.initialize_states(game)

            if greedy_action(nn, states) == action:
                correct += 1

            with silence():
                game.play_nn(action)
            next_state = storage.initialize_states(game)
            reward = reward_engine.reward()
            done = storage.done()

            a1 = next(k for k, v in DICT_ACT1.items() if v == action[0:2])
            a2 = next(k for k, v in DICT_ACT2.items() if v == action[2:4])
            loss = compute_loss(nn, states, a1, a2, reward, next_state, done, DISCOUNT)

            nn.optimizer.zero_grad()
            loss.backward()
            nn.optimizer.step()

            total_loss += loss.item()
            total_reward += reward
            n += 1

        avg_loss = total_loss / n if n else float("nan")
        acc = correct / n if n else 0.0
        history.append((ep, avg_loss, acc, total_reward))
        if ep == 1 or ep % PRINT_EVERY == 0 or ep == epochs:
            print(f"[Phase 2] Epoche {ep:4d} | Loss {avg_loss:10.4f} | "
                  f"Treffer {acc * 100:5.1f} % | Reward {total_reward:8.2f}")
        recent = history[-EARLY_STOP_EPOCHS:]
        if len(recent) == EARLY_STOP_EPOCHS and all(h[2] >= OVERFIT_ACC for h in recent):
            print(f"[Phase 2] Früh-Stopp: Trefferquote seit {EARLY_STOP_EPOCHS} Epochen "
                  f">= {OVERFIT_ACC * 100:.0f} %")
            break
    return history


def run_supervised_memorization(db, gid, moves, epochs=60):
    """Kapazitäts-Test: identisches Netz, aber stabiles Supervised-Ziel.
    Lernt die Zuordnung (Zustand -> aufgezeichneter Zug) als Klassifikation.
    Isoliert 'State-Repräsentation reicht nicht' von 'Q-Learning instabil'."""
    nn = DualingQNetwork(LR, "tmp_overfit_net.pt")
    F = T.nn.functional
    t1 = [next(k for k, v in DICT_ACT1.items() if v == a[0:2]) for a in moves]
    t2 = [next(k for k, v in DICT_ACT2.items() if v == a[2:4]) for a in moves]
    history = []
    for ep in range(1, epochs + 1):
        game, _ = load_replay(db, gid)
        storage = Storage(game)
        correct = 0
        total_loss = 0.0
        n = 0
        for action, a1, a2 in zip(moves, t1, t2):
            states = storage.initialize_states(game)
            with silence():
                game.play_nn(action)
            value, adv1, adv2 = nn.forward(states)
            loss = (F.cross_entropy(adv1.unsqueeze(0), T.tensor([a1], device=adv1.device)) +
                    F.cross_entropy(adv2.unsqueeze(0), T.tensor([a2], device=adv2.device)))
            nn.optimizer.zero_grad()
            loss.backward()
            nn.optimizer.step()
            total_loss += loss.item()
            ok = (int(adv1.detach().argmax()) == a1) and (int(adv2.detach().argmax()) == a2)
            correct += int(ok)
            n += 1
        avg_loss = total_loss / n if n else float("nan")
        acc = correct / n if n else 0.0
        history.append((ep, avg_loss, acc))
        if ep == 1 or ep % 10 == 0 or ep == epochs:
            print(f"[Supervised] Epoche {ep:3d} | Loss {avg_loss:8.4f} | Treffer {acc * 100:5.1f} %")
    return history


# ---------------------------------------------------------------------------
# Ansatz 1: reines Reward-Lernen OHNE legale Maske (Freies Spiel, Option a)
# ---------------------------------------------------------------------------
# Der Agent spielt jede Epoche das Spiel von vorn frei (epsilon-greedy ueber
# alle 252 Aktionen). Er lernt die Legalitaet implizit ueber die Belohnung
# (No-op = illegal -> -5). Metriken: Legalitaetsquote, Reward, Memorierung.

def random_action():
    """Zufaellige Aktion aus dem vollen 252er-Aktionsraum (keine Maske)."""
    n = random.randint(0, 11)
    m = random.randint(0, 20)
    return DICT_ACT1[n] + DICT_ACT2[m]


def memorization_accuracy(nn, db, gid, moves):
    """Deterministisches Replay des Spiels: wie oft stimmt Greedy-Argmax
    mit dem aufgezeichneten Zug ueberein (Clean-Imitation-Mass)."""
    game, _ = load_replay(db, gid)
    storage = Storage(game)
    correct = 0
    for action in moves:
        states = storage.initialize_states(game)
        if greedy_action(nn, states) == action:
            correct += 1
        with silence():
            game.play_nn(action)
    return correct / len(moves) if moves else 0.0


def run_explore_training(db, gid, moves, epochs=40, eps_start=1.0, eps_end=0.05,
                         max_steps=400, discount=DISCOUNT):
    """Answer 1: Freies Spiel per epsilon-greedy ueber alle 252 Aktionen.
    Der Agent waehlt zufaellig (hohes eps) und lernt ueber den Reward, welche
    Zuege legal/gut sind. Kein legal_actions-Zugriff."""
    nn = DualingQNetwork(LR, "tmp_overfit_net.pt")
    best_acc = 0.0
    for ep in range(1, epochs + 1):
        eps = max(eps_end, eps_start * (eps_end / eps_start) ** ((ep - 1) / max(epochs - 1, 1)))
        game, _ = load_replay(db, gid)
        storage = Storage(game)
        reward_engine = RewardEngine(game, storage)
        legal = 0
        total_reward = 0.0
        total_loss = 0.0
        n = 0
        steps = 0
        while game.gameon and steps < max_steps:
            steps += 1
            states = storage.initialize_states(game)
            if random.random() < eps:
                action = random_action()
            else:
                action = greedy_action(nn, states)
            with silence():
                game.play_nn(action)
            next_state = storage.initialize_states(game)
            if not T.equal(states, next_state):
                legal += 1
            reward = reward_engine.reward()
            done = storage.done()
            a1 = next(k for k, v in DICT_ACT1.items() if v == action[0:2])
            a2 = next(k for k, v in DICT_ACT2.items() if v == action[2:4])
            loss = compute_loss(nn, states, a1, a2, reward, next_state, done, discount)
            nn.optimizer.zero_grad()
            loss.backward()
            nn.optimizer.step()
            total_loss += loss.item()
            total_reward += reward
            n += 1
        legal_frac = legal / n if n else 0.0
        avg_loss = total_loss / n if n else float("nan")
        memo = memorization_accuracy(nn, db, gid, moves)
        best_acc = max(best_acc, memo)
        if ep == 1 or ep % 5 == 0 or ep == epochs:
            print(f"[Explore] Epoche {ep:3d} | eps {eps:4.2f} | Legal {legal_frac*100:5.1f} % | "
                  f"Reward {total_reward:9.2f} | Loss {avg_loss:10.4f} | "
                  f"Memo {memo*100:5.1f} % | Schritte {n}")
    return nn, best_acc


def report(history, n_moves, max_acc, supervised_history=None):
    print("\n===== Ergebnis =====")
    print(f"Züge im Spiel              : {n_moves}")
    if max_acc is not None:
        print(f"Aliasing-begrenztes Maximum: {max_acc * 100:.1f} %")
    if supervised_history:
        _, s_loss, s_acc = supervised_history[-1]
        print(f"[Kapazitäts-Vergleich] Supervised-Memorization "
              f"(gleiche Architektur/Repräsentation):")
        print(f"  Finaler Loss: {s_loss:.4f} | Trefferquote: {s_acc * 100:.1f} %")
    if not history:
        print("\n(Q-Learning übersprungen; nur Kapazitätstest gelaufen.)")
        if supervised_history and s_acc >= OVERFIT_ACC:
            print("=> Die State-Repräsentation reicht aus; das Netz kann die Züge")
            print("   memorieren. Das Q-Learning-Training ist der Flaschenhals.")
        else:
            print("=> Die State-Repräsentation ist der Flaschenhals (Memorieren")
            print("   scheitert selbst mit stabilem Supervised-Ziel).")
        return

    ep, loss, acc, reward = history[-1]
    overfit = acc >= OVERFIT_ACC and loss <= OVERFIT_LOSS
    print(f"Trainierte Epochen         : {len(history)}")
    print(f"Finaler Loss (Q-Learning)  : {loss:.4f}")
    print(f"Finale Trefferquote        : {acc * 100:.1f} %")
    if overfit:
        print("\n=> OVERFITTED: Das Netz hat das einzelne Spiel memoriert.")
        print("   State-Repräsentation ist ausreichend; die Lernmechanik kann lernen.")
    else:
        print("\n=> NICHT overfittet.")
        if supervised_history and s_acc >= OVERFIT_ACC:
            print("   ABER: Supervised-Memorization erreicht die Aliasing-Grenze ->")
            print("   Die State-Repräsentation reicht aus; das Q-Learning-Training")
            print("   (Bootstrapping, Aktion-Rauschen) ist der Flaschenhals.")
        elif supervised_history and max_acc is not None:
            if s_acc >= max_acc - 0.10:
                print("   Supervised erreicht fast die Aliasing-Grenze -> Repräsentation reicht")
                print("   aus; das Q-Learning-Training (Bootstrapping, Aktion-Diskriminierung")
                print("   über viele Aktionen) ist der verbleibende Flaschenhals.")
            else:
                print("   Supervised bleibt deutlich unter der Aliasing-Grenze -> Repräsentation")
                print("   ist weiterhin unvollständig (z.B. verdeckte Karten / Stapel-Längen).")
        elif max_acc is not None and max_acc < 1.0:
            print("   Ursache: Aliasing in der State-Repräsentation macht perfektes")
            print("   Memorieren prinzipiell unmöglich (derselbe Zustand, andere Züge).")
        else:
            print("   Ursache: instabiles/schwaches Lernen, nicht Aliasing "
                  "(Zustände sind eindeutig, aber das Netz lernt die Zuordnung nicht).")


def main():
    parser = argparse.ArgumentParser(description="Overfit-Experiment für Krips")
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--moves", type=int, default=TARGET_MOVES)
    parser.add_argument("--db", type=str, default=DB_PATH)
    parser.add_argument("--supervised", action="store_true",
                        help="Zusätzlichen Supervised-Kapazitätstest ausführen")
    parser.add_argument("--sup-epochs", type=int, default=60)
    parser.add_argument("--gid", type=int, default=None,
                        help="Vorhandene Spiel-ID laden statt neues Spiel zu generieren")
    parser.add_argument("--explore", action="store_true",
                        help="Ansatz 1: freies Reward-Lernen (keine legale Maske)")
    parser.add_argument("--explore-epochs", type=int, default=40)
    parser.add_argument("--eps-start", type=float, default=1.0)
    parser.add_argument("--eps-end", type=float, default=0.05)
    parser.add_argument("--max-steps", type=int, default=400)
    args = parser.parse_args()

    db = Datenbank(args.db)
    print(f"Datenbank: {args.db} (nächste Spiel-ID: {db.get_next_game_id()})")

    if args.gid is not None:
        game, moves = load_replay(db, args.gid)
        gid = args.gid
        state_keys = collect_state_keys(db, gid, moves)
        print(f"Geladenes Spiel: ID {gid} mit {len(moves)} Zügen")
        max_acc = analyze_aliasing(moves, state_keys)
    else:
        gid, moves, state_keys = generate_and_store_game(db, target_moves=args.moves)
        print(f"\nGespeichert: Spiel-ID {gid} mit {len(moves)} Zügen")
        print(f"Erste Züge: {moves[:12]}")
        max_acc = analyze_aliasing(moves, state_keys)

    if not moves:
        print("Keine Züge zum Trainieren -> Abbruch.")
        db.connection.close()
        return

    if args.explore:
        print("\n== Ansatz 1: Freies Reward-Lernen (ohne legale Maske) ==")
        nn, best_acc = run_explore_training(
            db, gid, moves, epochs=args.explore_epochs,
            eps_start=args.eps_start, eps_end=args.eps_end, max_steps=args.max_steps)
        print(f"\n[Explore-Ende] Beste Memorierung (argmax == aufgezeichneter Zug): {best_acc * 100:.1f} %")
        db.connection.close()
        return

    history = None
    if args.epochs > 0:
        history = run_overfit_training(db, gid, moves, epochs=args.epochs)
    supervised_history = None
    if args.supervised:
        print("\n--- Supervised-Kapazitätstest ---")
        supervised_history = run_supervised_memorization(db, gid, moves, epochs=args.sup_epochs)
    report(history, len(moves), max_acc, supervised_history)

    db.connection.close()


if __name__ == "__main__":
    main()
