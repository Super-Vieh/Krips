# Exposé zur Bachelorarbeit: Reinforcement Learning und Optimierung im Kartenspiel "Krips"

## 1. Einleitung und Spielregeln von Krips
Das Projekt beschäftigt sich mit dem Kartenspiel "Krips" (auch bekannt als Zank-Patience, Russian Bank oder Crapette). Es ist ein strategisches Kartenspiel für zwei Spieler, das mit zwei regulären 52-Karten-Decks gespielt wird. Ziel des Spieles ist es, als erster Spieler alle Karten (insbesondere das sogenannte 13er-Päckchen) abzulegen.

**Wesentliche Spielregeln:**
- **Spielfeld:** In der Mitte gibt es 8 Zielfelder (Foundation-Piles), auf denen Karten aufsteigend von Ass bis König nach Farbe (Pik, Herz, etc.) abgelegt werden. Außen gibt es 8 weitere Ablagefelder, die wie bei Solitär absteigend und in abwechselnden Farben bedient werden können.
- **Spieler-Decks:** Jeder Spieler hat drei Haufen: Ein normales Nachzieh-Päckchen, einen Ablagehaufen und das 13er-Päckchen (13 verdeckte Karten).
- **Ablauf:** Man deckt Karten auf und versucht, diese an den Mittel- oder Außenfeldern anzulegen. Mittelstapel haben absolute Priorität. Übersieht ein Spieler eine mögliche Ablage in der Mitte, kann der Gegner eingreifen und der Zug wechselt. Das Spiel endet, sobald ein Spieler sein 13er-Päckchen vollständig abgelegt hat oder ein Spieler keine Karten mehr besitzt.

## 2. Architektur des Spiels
Die zugrundeliegende Spiel-Engine wurde in Python im Ordner `Klassen/` objektorientiert implementiert:
- **`karten.py` / `karteneigenschaftenenum.py`:** Repräsentation der Karten (Wert, Typ, Sichtbarkeit).
- **`spieler.py`:** Verwaltet den Zustand eines Spielers (seine drei Haufen, Handkarten).
- **`spiel.py`:** Beinhaltet die zentrale Spiellogik, Zugvalidierung und Regel-Engine.
- **`spielinititalisierer.py`:** Übernimmt das Mischen und die korrekte Startaufstellung.

Diese Architektur simuliert die Spielregeln präzise und bietet eine Schnittstelle für den RL-Agenten, um Spielzustände abzufragen und Züge auszuführen.

## 3. Architektur des Neuronalen Netzwerks
Der aktuelle Agent basiert auf einer **Deep Dueling Q-Learning** Architektur (`qualing_q_learning.py`). 
Eine Besonderheit von Dueling Q-Learning ist die Aufspaltung des Netzwerks zur separaten Schätzung des Zustands-Wertes (Value) und des Aktions-Vorteils (Advantage).

**Netzwerkaufbau:**
- **Input:** 1144 Neuronen (Repräsentiert den Spielzustand als Tensor, bestehend aus 22 Listen à 52 Bit).
- **Feature Extraction:** Drei Fully-Connected (Linear) Schichten (2000 -> 1000 -> 512 Neuronen) mit ReLU-Aktivierung.
- **Value-Stream:** Schätzt den Wert des aktuellen Zustandes über weitere Schichten (512 -> 256 -> 64 -> 1).
- **Advantage-Stream:** Schätzt die Qualität der verfügbaren Aktionen. Dies ist aufgeteilt in zwei Reihen (12 und 21 Output-Neuronen), welche gekoppelt berechnet werden, um die Aktionspaare des Spiels zu bewerten.
- **Output:** Kombination aus Value und Advantage zur Berechnung der finalen Q-Werte für alle möglichen Züge.

## 4. Lernmethode und das Reward-System
Der Agent lernt mittels Q-Learning aus der Interaktion mit dem Spiel. Das momentane **Reward-System** (`reward_engine.py`) basiert auf handgeschriebenen, heuristischen Belohnungen:
- +3 für das Ablegen in der Mitte.
- +10 für das Ablegen einer Karte vom Spieler auf das Brett.
- +1 für das Beenden eines Zuges.
- Negative Belohnungen (-5) für bedeutungslose Züge oder Hin-und-Her-Wechsel.
- Belohnungen für das Freimachen von Feldern.

**Notwendigkeit der Überarbeitung:** 
Das aktuelle Reward-System ist stark heuristisch ("Reward Shaping"). Dies kann zu unerwünschten lokalen Optima führen (z.B. der Agent macht Züge nur, um Zwischenbelohnungen abzugreifen, anstatt zu gewinnen). Für eine Bachelorarbeit ist es essenziell, dieses System wissenschaftlich fundiert zu überarbeiten. Ein reiner Win/Loss-Reward mit eventuell besserem Discount-Faktor oder sparsamen Zwischen-Rewards für abgebautes 13er-Päckchen verspricht eine stabilere und repräsentativere Konvergenz.

## 5. Tensorboard-Integration
Zur Überwachung des Trainingsprozesses wird Tensorboard (`tensor_metric_board.py`) eingesetzt. Folgende Metriken werden aktuell geloggt:
- `turn/made_moves` (Gespielte Züge)
- `turn/valid_moves` (Anzahl gültiger Züge)
- `turn/epsilon` (Exploration-Rate)
- `turn/total_reward` und `turn/total_loss`
- `turn/reward_loss_ratio` und `turn/valid_moves_ratio`

Dies bietet eine exzellente Grundlage zur Visualisierung des Lernfortschritts in der wissenschaftlichen Ausarbeitung.

## 6. Zustand und Architektur der Datenbank
Eine effiziente Datenhaltung für Replays und Spielzüge existiert im Ordner `Datenbank/`.
- **Technologie:** Es wird **DuckDB** als performantes, spaltenbasiertes Datenbanksystem verwendet (`krips_replay_store.duckdb`).
- **Tabellenarchitektur:**
  - `StartingCards`: Speichert die Game-ID und die JSON-codierten Decks beider Spieler.
  - `Moves`: Speichert die Züge in einer schachähnlichen Notation als Arrays unter der Game-ID.
- Dies ermöglicht es, gespielte Matches für das Training auszuwerten, Replays zu analysieren oder als Experience Replay Buffer zu dienen.

## 7. Geplante Optimierungen und Erweiterungen (Roadmap)
Im Rahmen der Bachelorarbeit sollen folgende technische Ziele umgesetzt werden:
1. **Multiprocessing / Parallelisierung:** Die Ausführung der Spiele und des Trainings soll durch Multiprocessing beschleunigt werden, um mehr Spiele pro Sekunde zu simulieren und den Lernprozess drastisch zu verkürzen.
2. **Neuentwicklung der UI:** Eine moderne, entkoppelte grafische Oberfläche soll entwickelt werden, die zur Demonstration und für Testspiele gegen den Agenten geeignet ist.
3. **Komplettes Refactoring:** Der Codebase soll überarbeitet werden (Clean Code, Performance-Optimierungen), um eine solide Basis für komplexe Experimente zu schaffen.
4. **Überarbeitung des Reward-Systems:** Weg von strikten Heuristiken hin zu generalisierteren Ansätzen, die langfristiges Planen (Sieg) fördern.

## 8. Vorschläge für Analysen und Forschung
Um den akademischen Anspruch der Bachelorarbeit zu untermauern, werden folgende Analysen vorgeschlagen:

### 8.1. Analyse zur erwartbaren Qualität des Lernens (Convergence & Performance)
- Analyse der "Sample Efficiency" und Konvergenzgeschwindigkeit durch Multiprocessing.
- Gegenüberstellung des aktuellen Reward-Shapings gegenüber einem unvoreingenommenen Sparse-Reward (nur Win/Loss/Draw) in Bezug auf strategisches Fehlverhalten (Exploiting der Heuristik).
- Analyse der Strategien des Agenten gegen Ende des Trainings (Entwickelt die KI "menschliche" oder gar überlegene Eröffnungs- und Endspielstrategien?).

### 8.2. Verbesserung der Neuronalen Netzwerk-Architektur
- **Architektur-Vergleich:** Evaluierung, ob Fully-Connected (Linear) Layers für den 1144-dimensionalen Input optimal sind. Vorschlag: Einbindung von faltungsbasierten (CNNs) oder aufmerksamkeitsbasierten (Transformer) Ansätzen, da der Spielzustand räumliche und ordnende Beziehungen (Sets, Reihenfolgen) besitzt.
- **Hyperparameter-Tuning:** Systematische Untersuchung von Lernraten, Batch-Sizes und der Größe des Replay-Buffers (DuckDB Integration).

### 8.3. Analyse der Lernmethode (Algorithmische Verbesserungen)
- Anstelle von reinem Dueling Q-Learning könnte der Einsatz von **Proximal Policy Optimization (PPO)** oder **Soft Actor-Critic (SAC)** untersucht werden.
- Integration von **Prioritized Experience Replay**, bei dem der Agent aus Spielen, in denen der Loss besonders hoch war, häufiger lernt.

## Fazit
Dieses Projekt bietet eine ideale Schnittmenge aus moderner Softwareentwicklung (Datenbanken, UI, Multiprocessing) und komplexem Machine Learning (Reinforcement Learning). Der bestehende Code dient als perfektes Proof-of-Concept, während die anstehenden Refactorings und wissenschaftlichen Analysen den Rahmen einer hervorragenden Bachelorarbeit im Bereich Informatik / Wirtschaftsinformatik bilden.
