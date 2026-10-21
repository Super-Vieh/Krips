import random

import numpy as np
import torch as T

from Klassen import Karten, KartenTyp, Spiel


class Storage:
    def __init__(self, game: Spiel | None = None) -> None:
        self.game = game
        self.transitions: list[tuple] = []
        self.all_states: list[T.Tensor] = []
        self.last_state: T.Tensor | None = None
        if game is not None:
            state = self.initialize_states(game)
            self.all_states = [state]
            self.last_state = state

    def initialize_states(self, game: Spiel) -> T.Tensor:
        """
        SPIELER 1:
        [0:52]     -> Spieler 1 Päckchen (Handkarten)
        [52:104]   -> Spieler 1 Haufen (Ablagestapel)
        [104:156]  -> Spieler 1 Dreizehner

        SPIELER 2:
        [156:208]  -> Spieler 2 Päckchen (Handkarten)
        [208:260]  -> Spieler 2 Haufen (Ablagestapel)
        [260:312]  -> Spieler 2 Dreizehner

        SPIELFELD Seitenplätze:
        [312:728]  -> Platzliste 8 Listen * 52
        (z.B. Platz 1 ist 312:364, Platz 2 ist 364:416, ...)

        SPIELFELD Mitte:
        [728:1144] -> Mittelliste 8 Listen * 52
        """
        states: list[int] = []
        for pile in self.game_piles(game):
            states += self.transform_to_52bitvektor(pile)
        return T.tensor(states, dtype=T.float32).unsqueeze(0)

    def initialize_states_batch(self, games: list[Spiel]) -> T.Tensor:
        if not games:
            return T.zeros((0, 1144), dtype=T.float32)
        return T.cat([self.initialize_states(game) for game in games], dim=0)

    def game_piles(self, game: Spiel) -> list[list[Karten]]:
        spieler_listen: list[list[Karten]] = [
            game.spieler1Paechen,
            game.spieler1Haufen,
            game.spieler1Dreizehner,
            game.spieler2Paechen,
            game.spieler2Haufen,
            game.spieler2Dreizehner,
        ]
        return spieler_listen + game.platzliste + game.mittlereliste

    def transform_to_52bitvektor(self, pile: list[Karten]) -> list[int]:
        dict_suit: dict[KartenTyp, int] = {
            KartenTyp.Pik: 0,
            KartenTyp.Coeur: 1,
            KartenTyp.Treff: 2,
            KartenTyp.Karro: 3,
        }
        empty_list: list[int] = [0] * 52
        if not pile:
            return empty_list
        for card in pile:
            if card.karteOffen == False and pile[-1].karteOffen == False:
                break
            if card.karteOffen == False:
                continue
            empty_list[(dict_suit[card.kartentyp] * 13) + card.kartenwert.value - 1] = 1
        return empty_list

    def done(self, game: Spiel) -> bool:
        return not game.gameon

    def initialize_actions(self) -> tuple[T.Tensor, T.Tensor]:
        actions_firstoutputlayer = list(range(12))
        actions_secondoutputlayer = list(range(21))
        actions_firstoutputlayer_t = T.tensor(actions_firstoutputlayer, dtype=T.float32)
        actions_secondoutputlayer_t = T.tensor(actions_secondoutputlayer, dtype=T.float32)
        return actions_firstoutputlayer_t, actions_secondoutputlayer_t

    def add_transitions(
        self,
        states: T.Tensor,
        actions: T.Tensor,
        rewards: T.Tensor,
        next_states: T.Tensor,
        dones: T.Tensor,
        next_masks: T.Tensor,
    ) -> None:
        for i in range(states.shape[0]):
            self.transitions.append(
                (
                    states[i].detach().cpu().float(),
                    int(actions[i]),
                    float(rewards[i]),
                    next_states[i].detach().cpu().float(),
                    bool(dones[i]),
                    next_masks[i].detach().cpu().bool(),
                )
            )

    def sample_transitions(self, batch_size: int) -> dict[str, T.Tensor]:
        if not self.transitions:
            raise ValueError("No transitions stored")
        batch = random.sample(self.transitions, min(batch_size, len(self.transitions)))
        states = T.stack([row[0] for row in batch])
        actions = T.tensor([row[1] for row in batch], dtype=T.long)
        rewards = T.tensor([row[2] for row in batch], dtype=T.float32)
        next_states = T.stack([row[3] for row in batch])
        dones = T.tensor([row[4] for row in batch], dtype=T.float32)
        next_masks = T.stack([row[5] for row in batch])
        return {
            "states": states,
            "actions": actions,
            "rewards": rewards,
            "next_states": next_states,
            "dones": dones,
            "next_masks": next_masks,
        }

    def create_transition(self, action_index: int, reward: float) -> tuple:
        if self.game is None:
            raise ValueError("Storage has no game")
        state = self.last_state
        next_state = self.initialize_states(self.game)
        transition = (state, action_index, reward, next_state, not self.game.gameon)
        self.last_state = next_state
        return transition
