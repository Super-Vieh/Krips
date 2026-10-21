import numpy as np
import torch as T
import torch.nn.functional as F

from Klassen import Spiel

from .qualing_q_learning import DualingQNetwork
from .storage import Storage

ACTION1: list[str] = [
    "K0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "A0", "A1", "A2",
]

ACTION2: list[str] = [
    "K0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8",
    "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8",
    "A0", "A1", "A2", "G0",
]


class Agent:
    def __init__(
        self,
        nn: DualingQNetwork,
        storage: Storage | None = None,
        seed: int = 0,
    ) -> None:
        self.nn: DualingQNetwork = nn
        self.storage: Storage = storage if storage is not None else Storage()
        self.rng: np.random.Generator = np.random.default_rng(seed)

    def act(self, games: list[Spiel], epsilon: float = 0.0) -> list[str]:
        if not games:
            return []
        states = self.storage.initialize_states_batch(games)
        indices = self.select_action(epsilon, states)
        return [self._index_to_action(int(index)) for index in indices]

    def act_off_turn(self, games: list[Spiel], epsilon: float = 0.0) -> list[str]:
        actions: list[str] = []
        for game in games:
            if game.wouldbeKrips and (epsilon <= 0.0 or self.rng.random() >= epsilon):
                actions.append("K0K0")
            else:
                actions.append("H0H0")
        return actions

    def select_action(self, epsilon: float, states: T.Tensor) -> list[int]:
        with T.no_grad():
            q_values = self.nn.q_values(states)
        flat_q = q_values.reshape(q_values.shape[0], -1)
        greedy = flat_q.argmax(dim=1)

        indices: list[int] = []
        for row in range(flat_q.shape[0]):
            if epsilon > 0.0 and self.rng.random() < epsilon:
                indices.append(int(self.rng.integers(flat_q.shape[1])))
            else:
                indices.append(int(greedy[row]))
        return indices

    def decode_action(self, action: str) -> tuple[int, int]:
        return ACTION1.index(action[0:2]), ACTION2.index(action[2:4])

    def decode_indices(self, indices: T.Tensor) -> tuple[T.Tensor, T.Tensor]:
        n = indices // 21
        m = indices % 21
        return n, m

    def _index_to_action(self, index: int) -> str:
        n, m = divmod(index, 21)
        return ACTION1[n] + ACTION2[m]

    def compute_loss(
        self,
        states: T.Tensor,
        actions: T.Tensor,
        rewards: T.Tensor,
        next_states: T.Tensor,
        dones: T.Tensor,
        discount_factor: float = 0.99,
    ) -> T.Tensor:
        actions = actions.to(self.nn.device)
        rewards = rewards.to(self.nn.device)
        dones = dones.to(self.nn.device)

        q_values = self.nn.q_values(states).reshape(actions.shape[0], -1)
        predicted = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        with T.no_grad():
            next_q = self.nn.q_values(next_states).reshape(actions.shape[0], -1)
            next_max = next_q.max(dim=1).values
            target = rewards + discount_factor * next_max * (1.0 - dones)

        return F.mse_loss(predicted, target)
