import random

import numpy as np
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


class SequenceStorage:
    def __init__(
        self,
        capacity: int = 100_000,
        sequence_length: int = 8,
        action_count: int = 252,
        seed: int = 0,
    ) -> None:
        self.capacity: int = capacity
        self.sequence_length: int = sequence_length
        self.action_count: int = action_count
        self.episodes: list[dict] = []
        self.buffers: dict[int, dict] = {}
        self.size: int = 0
        self.rng = np.random.default_rng(seed)

    def initialize_states(self, game) -> T.Tensor:
        return T.from_numpy(encode_game(game)).unsqueeze(0)

    def initialize_states_batch(self, games: list) -> T.Tensor:
        if not games:
            return T.zeros((0, VECTOR_SIZE), dtype=T.float32)
        return T.from_numpy(encode_games(games))

    def add(
        self,
        env_index: int,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        mask: np.ndarray,
        next_mask: np.ndarray,
        expert: int = -1,
    ) -> None:
        buffer = self.buffers.get(env_index)
        if buffer is None:
            buffer = {
                "states": [],
                "masks": [],
                "actions": [],
                "rewards": [],
                "dones": [],
                "next_states": [],
                "next_masks": [],
                "expert": [],
            }
            self.buffers[env_index] = buffer
        buffer["states"].append(state.astype(np.float16, copy=True))
        buffer["masks"].append(mask.astype(bool, copy=True))
        buffer["actions"].append(int(action))
        buffer["rewards"].append(float(reward))
        buffer["dones"].append(float(done))
        buffer["next_states"].append(next_state.astype(np.float16, copy=True))
        buffer["next_masks"].append(next_mask.astype(bool, copy=True))
        buffer["expert"].append(int(expert))

    def finish(self, env_index: int, terminal_reward: float = 0.0) -> None:
        buffer = self.buffers.get(env_index)
        if buffer is None:
            return
        if buffer["actions"]:
            buffer["dones"][-1] = 1.0
            buffer["rewards"][-1] += float(terminal_reward)
        self.flush(env_index)

    def flush(self, env_index: int) -> None:
        buffer = self.buffers.pop(env_index, None)
        if buffer is None or not buffer["actions"]:
            return
        episode = {
            "states": np.stack(buffer["states"]),
            "masks": np.stack(buffer["masks"]),
            "actions": np.asarray(buffer["actions"], dtype=np.int64),
            "rewards": np.asarray(buffer["rewards"], dtype=np.float32),
            "dones": np.asarray(buffer["dones"], dtype=np.float32),
            "expert": np.asarray(buffer["expert"], dtype=np.int64),
            "final_state": buffer["next_states"][-1],
            "final_mask": buffer["next_masks"][-1],
        }
        self.episodes.append(episode)
        self.size += int(episode["actions"].shape[0])
        while self.size > self.capacity and self.episodes:
            removed = self.episodes.pop(0)
            self.size -= int(removed["actions"].shape[0])

    def clear_buffers(self) -> None:
        self.buffers.clear()

    def reset(self) -> None:
        self.episodes.clear()
        self.buffers.clear()
        self.size = 0

    def sample(self, batch_size: int) -> dict[str, T.Tensor]:
        if not self.episodes:
            raise ValueError("No episodes stored")
        lengths = np.fromiter(
            (episode["actions"].shape[0] for episode in self.episodes),
            dtype=np.int64,
            count=len(self.episodes),
        )
        cumulative = np.cumsum(lengths)
        starts = np.concatenate(([0], cumulative[:-1]))
        picks = self.rng.integers(0, int(cumulative[-1]), size=batch_size)
        episode_indices = np.searchsorted(cumulative, picks, side="right")
        offsets = picks - starts[episode_indices]

        k = self.sequence_length
        positions = offsets[:, None] + (np.arange(k)[None, :] - (k - 1))
        valid = positions >= 0
        clipped = np.clip(positions, 0, None)

        states = np.zeros((batch_size, k, VECTOR_SIZE), dtype=np.float16)
        next_states = np.zeros((batch_size, k, VECTOR_SIZE), dtype=np.float16)
        masks = np.zeros((batch_size, k, self.action_count), dtype=bool)
        next_masks = np.zeros((batch_size, k, self.action_count), dtype=bool)
        actions = np.zeros((batch_size, k), dtype=np.int64)
        rewards = np.zeros((batch_size, k), dtype=np.float32)
        dones = np.zeros((batch_size, k), dtype=np.float32)
        expert = np.full((batch_size, k), -1, dtype=np.int64)

        for row in range(batch_size):
            episode = self.episodes[episode_indices[row]]
            place = clipped[row]
            length = episode["actions"].shape[0]
            following = np.minimum(place + 1, length - 1)
            tail = place + 1 >= length

            states[row] = episode["states"][place]
            next_states[row] = episode["states"][following]
            masks[row] = episode["masks"][place]
            next_masks[row] = episode["masks"][following]
            actions[row] = episode["actions"][place]
            rewards[row] = episode["rewards"][place]
            dones[row] = episode["dones"][place]
            expert[row] = episode["expert"][place]
            if tail.any():
                next_states[row][tail] = episode["final_state"]
                next_masks[row][tail] = episode["final_mask"]

        return {
            "states": T.from_numpy(states).float(),
            "actions": T.from_numpy(actions),
            "rewards": T.from_numpy(rewards),
            "next_states": T.from_numpy(next_states).float(),
            "dones": T.from_numpy(dones),
            "masks": T.from_numpy(masks),
            "next_masks": T.from_numpy(next_masks),
            "expert": T.from_numpy(expert),
            "valid": T.from_numpy(valid).float(),
        }

    def __len__(self) -> int:
        return self.size
