import random

import torch as T

from Gymnasium.observation import VECTOR_SIZE, encode_game, encode_games


class Storage:
    def __init__(self, capacity: int = 100_000) -> None:
        self.capacity: int = capacity
        self.transitions: list[tuple] = []
        self.position: int = 0

    def initialize_states(self, game) -> T.Tensor:
        return T.from_numpy(encode_game(game)).unsqueeze(0)

    def initialize_states_batch(self, games: list) -> T.Tensor:
        if not games:
            return T.zeros((0, VECTOR_SIZE), dtype=T.float32)
        return T.from_numpy(encode_games(games))

    def add_transitions(
        self,
        states: T.Tensor,
        actions: T.Tensor,
        rewards: T.Tensor,
        next_states: T.Tensor,
        dones: T.Tensor,
    ) -> None:
        for i in range(states.shape[0]):
            transition = (
                states[i].detach().cpu().float(),
                int(actions[i]),
                float(rewards[i]),
                next_states[i].detach().cpu().float(),
                bool(dones[i]),
            )
            if len(self.transitions) < self.capacity:
                self.transitions.append(transition)
            else:
                self.transitions[self.position] = transition
                self.position = (self.position + 1) % self.capacity

    def sample_transitions(self, batch_size: int) -> dict[str, T.Tensor]:
        if not self.transitions:
            raise ValueError("No transitions stored")
        batch = random.sample(self.transitions, min(batch_size, len(self.transitions)))
        states = T.stack([row[0] for row in batch])
        actions = T.tensor([row[1] for row in batch], dtype=T.long)
        rewards = T.tensor([row[2] for row in batch], dtype=T.float32)
        next_states = T.stack([row[3] for row in batch])
        dones = T.tensor([row[4] for row in batch], dtype=T.float32)
        return {
            "states": states,
            "actions": actions,
            "rewards": rewards,
            "next_states": next_states,
            "dones": dones,
        }

    def __len__(self) -> int:
        return len(self.transitions)
