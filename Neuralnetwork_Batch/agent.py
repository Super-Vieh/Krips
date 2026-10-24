import numpy as np
import torch as T
import torch.nn.functional as F

from Gymnasium import KripsEnv
from Klassen.move import DestinationType, Move, OriginType

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
        player_number: int = 1,
        seed: int = 0,
    ) -> None:
        self.nn: DualingQNetwork = nn
        self.storage: Storage = storage if storage is not None else Storage()
        self.player_number: int = player_number
        self.rng: np.random.Generator = np.random.default_rng(seed)

    def act(self, game, epsilon: float = 0.0) -> Move:
        return self.act_batch([game], epsilon)[0]

    def act_batch(self, games: list, epsilon: float = 0.0) -> list[Move]:
        if not games:
            return []
        states = self.storage.initialize_states_batch(games)
        indices = self.select_action(epsilon, states)
        return [self.index_to_move(index) for index in indices]

    def act_off_turn(self, game, epsilon: float = 0.0) -> Move:
        if game.is_krips and (epsilon <= 0.0 or self.rng.random() >= epsilon):
            return Move(OriginType.KRIPS, 1, DestinationType.KRIPS, 1)
        return Move(OriginType.KRIPS, 0, DestinationType.KRIPS, 0)

    def select_action(self, epsilon: float, states: T.Tensor) -> list[int]:
        with T.no_grad():
            q_values = self.nn.q_values(states)
        flat_q = q_values.reshape(q_values.shape[0], -1)
        flat_q[:, 0] = T.finfo(flat_q.dtype).min
        greedy = flat_q.argmax(dim=1).tolist()

        indices: list[int] = []
        for best in greedy:
            if epsilon > 0.0 and self.rng.random() < epsilon:
                n = int(self.rng.integers(1, 12))
                m = int(self.rng.integers(1, 21))
                indices.append(n * 21 + m)
            else:
                indices.append(int(best))
        return indices

    @staticmethod
    def index_to_move(index: int) -> Move:
        n, m = divmod(index, 21)
        return KripsEnv.action_to_move((n, m))

    @staticmethod
    def move_to_index(move: Move) -> int:
        if move.origin_type == OriginType.KRIPS:
            n = 0
        elif move.origin_type == OriginType.TABLEAU:
            n = move.origin_value + 1
        else:
            n = move.origin_value + 9
        if move.destination_type == DestinationType.KRIPS:
            m = 0
        elif move.destination_type == DestinationType.TABLEAU:
            m = move.destination_value + 1
        elif move.destination_type == DestinationType.FOUNDATION:
            m = move.destination_value + 9
        elif move.destination_type == DestinationType.PLAYER:
            m = move.destination_value + 17
        else:
            m = 20
        return n * 21 + m

    def decode_action(self, action: str) -> tuple[int, int]:
        return ACTION1.index(action[0:2]), ACTION2.index(action[2:4])

    def decode_indices(self, indices: T.Tensor) -> tuple[T.Tensor, T.Tensor]:
        n = indices // 21
        m = indices % 21
        return n, m

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

    def train_step(self, batch_size: int, discount_factor: float = 0.99) -> float:
        batch = self.storage.sample_transitions(batch_size)
        loss = self.compute_loss(
            batch["states"],
            batch["actions"],
            batch["rewards"],
            batch["next_states"],
            batch["dones"],
            discount_factor,
        )
        self.nn.optimizer.zero_grad()
        loss.backward()
        self.nn.optimizer.step()
        return float(loss.item())
