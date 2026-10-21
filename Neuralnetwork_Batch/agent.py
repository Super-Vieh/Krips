import numpy as np
import torch as T
import torch.nn.functional as F

from Klassen import Spiel

from .legal_moves import ACTION1, ACTION2, legal_masks
from .qualing_q_learning import DualingQNetwork
from .storage import Storage


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
        masks = legal_masks(games)
        indices = self.select_action(epsilon, states, masks)
        return [self._index_to_action(int(index)) for index in indices]

    def act_off_turn(self, games: list[Spiel], epsilon: float = 0.0) -> list[str]:
        actions: list[str] = []
        for game in games:
            if game.wouldbeKrips and (epsilon <= 0.0 or self.rng.random() >= epsilon):
                actions.append("K0K0")
            else:
                actions.append("H0H0")
        return actions

    def select_action(
        self,
        epsilon: float,
        states: T.Tensor,
        masks: T.Tensor,
    ) -> list[int]:
        masks = masks.to(self.nn.device)
        flat_masks = masks.reshape(masks.shape[0], -1)
        with T.no_grad():
            q_values = self.nn.q_values(states)
        flat_q = q_values.reshape(q_values.shape[0], -1)
        masked_q = flat_q.masked_fill(~flat_masks, T.finfo(flat_q.dtype).min)
        greedy = masked_q.argmax(dim=1)

        indices: list[int] = []
        for row in range(flat_q.shape[0]):
            legal_indices = T.nonzero(flat_masks[row], as_tuple=False).flatten()
            if legal_indices.numel() == 0:
                raise RuntimeError(f"No legal action for row {row}")
            if epsilon > 0.0 and self.rng.random() < epsilon:
                pick = legal_indices[int(self.rng.integers(legal_indices.numel()))]
                indices.append(int(pick))
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
        next_masks: T.Tensor,
        discount_factor: float = 0.99,
    ) -> T.Tensor:
        actions = actions.to(self.nn.device)
        rewards = rewards.to(self.nn.device)
        dones = dones.to(self.nn.device)
        next_masks = next_masks.to(self.nn.device)

        q_values = self.nn.q_values(states).reshape(actions.shape[0], -1)
        predicted = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        with T.no_grad():
            next_q = self.nn.q_values(next_states).reshape(actions.shape[0], -1)
            flat_next_masks = next_masks.reshape(actions.shape[0], -1)
            next_q = next_q.masked_fill(~flat_next_masks, T.finfo(next_q.dtype).min)
            next_max = next_q.max(dim=1).values
            target = rewards + discount_factor * next_max * (1.0 - dones)

        return F.mse_loss(predicted, target)
