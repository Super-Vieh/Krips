import copy

import numpy as np
import torch as T
import torch.nn.functional as F

from Gymnasium import KripsEnv
from Gymnasium.observation import encode_game
from Klassen.move import DestinationType, Move, OriginType

from .qualing_q_learning import DualingQNetwork, DTQNNetwork
from .storage import SequenceStorage, Storage

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


class DTQNAgent(Agent):
    def __init__(
        self,
        nn: DTQNNetwork,
        storage: SequenceStorage | None = None,
        player_number: int = 1,
        seed: int = 0,
        target_update_freq: int = 1000,
        tau: float | None = None,
        action_count: int = 252,
    ) -> None:
        super().__init__(nn, storage, player_number, seed)
        self.action_count: int = action_count
        self.target_nn: DTQNNetwork = copy.deepcopy(nn)
        for parameter in self.target_nn.parameters():
            parameter.requires_grad = False
        self.target_nn.eval()
        self.target_update_freq: int = target_update_freq
        self.tau: float | None = tau
        self.update_counter: int = 0

    @staticmethod
    def legal_mask(game) -> np.ndarray:
        mask = np.zeros(252, dtype=bool)
        if not game.is_running or game.current_player is None:
            return mask
        for move in game.rules.get_all_valid_moves():
            mask[Agent.move_to_index(move)] = True
        return mask

    def act(self, game, epsilon: float = 0.0) -> Move:
        state = encode_game(game)[None, None, :]
        window = np.repeat(state, self.nn.sequence_length, axis=1)
        masks = T.from_numpy(self.legal_mask(game)[None, :])
        index = self.select_action(epsilon, T.from_numpy(window).float(), masks)[0]
        return self.index_to_move(index)

    def select_action(
        self,
        epsilon: float,
        states: T.Tensor,
        masks: T.Tensor,
    ) -> list[int]:
        with T.no_grad():
            q_values = self.nn.q_values(states)[:, -1]
        flat_q = q_values.reshape(q_values.shape[0], -1)
        masks = masks.to(flat_q.device).bool()
        flat_q = flat_q.masked_fill(~masks, T.finfo(flat_q.dtype).min)
        greedy = flat_q.argmax(dim=1).tolist()

        indices: list[int] = []
        for row, best in zip(masks.cpu().numpy(), greedy):
            legal = np.flatnonzero(row)
            if epsilon > 0.0 and legal.size and self.rng.random() < epsilon:
                indices.append(int(self.rng.choice(legal)))
            else:
                indices.append(int(best))
        return indices

    def compute_loss(
        self,
        states: T.Tensor,
        actions: T.Tensor,
        rewards: T.Tensor,
        next_states: T.Tensor,
        dones: T.Tensor,
        next_masks: T.Tensor,
        valid: T.Tensor,
        discount_factor: float = 0.99,
        masks: T.Tensor | None = None,
        expert: T.Tensor | None = None,
        bc_weight: float = 0.0,
    ) -> T.Tensor:
        device = self.nn.device
        actions = actions.to(device)
        rewards = rewards.to(device)
        dones = dones.to(device)
        next_masks = next_masks.to(device).bool()
        valid = valid.to(device)
        states = states.to(device)
        next_states = next_states.to(device)

        q_values = self.nn.q_values(states).reshape(states.shape[0], states.shape[1], -1)
        predicted = q_values.gather(2, actions.unsqueeze(2)).squeeze(2)

        with T.no_grad():
            online_next = self.nn.q_values(next_states)
            online_next = online_next.reshape(next_states.shape[0], next_states.shape[1], -1)
            online_next = online_next.masked_fill(
                ~next_masks, T.finfo(online_next.dtype).min
            )
            best_action = online_next.argmax(dim=2, keepdim=True)
            target_next = self.target_nn.q_values(next_states)
            target_next = target_next.reshape(next_states.shape[0], next_states.shape[1], -1)
            target_value = target_next.gather(2, best_action).squeeze(2)
            target = rewards + discount_factor * target_value * (1.0 - dones)

        elementwise = F.smooth_l1_loss(predicted, target, reduction="none")
        loss = (elementwise * valid).sum() / valid.sum().clamp(min=1.0)

        if bc_weight > 0.0 and masks is not None and expert is not None:
            masks = masks.to(device).bool()
            expert = expert.to(device)
            supervised = ((expert >= 0).float() * valid)
            logits = q_values.masked_fill(~masks, -1e9)
            crossed = F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]),
                expert.clamp(min=0).reshape(-1),
                reduction="none",
            ).reshape(expert.shape)
            loss = loss + bc_weight * (crossed * supervised).sum() / supervised.sum().clamp(min=1.0)
        return loss

    def update_target(self) -> None:
        if self.tau is not None:
            with T.no_grad():
                for target_parameter, parameter in zip(
                    self.target_nn.parameters(), self.nn.parameters()
                ):
                    target_parameter.mul_(1.0 - self.tau).add_(parameter, alpha=self.tau)
        else:
            if self.update_counter % self.target_update_freq == 0:
                self.target_nn.load_state_dict(self.nn.state_dict())

    def train_step(
        self,
        batch_size: int,
        discount_factor: float = 0.99,
        bc_weight: float = 0.0,
    ) -> float:
        batch = self.storage.sample(batch_size)
        loss = self.compute_loss(
            batch["states"],
            batch["actions"],
            batch["rewards"],
            batch["next_states"],
            batch["dones"],
            batch["next_masks"],
            batch["valid"],
            discount_factor,
            masks=batch["masks"],
            expert=batch["expert"],
            bc_weight=bc_weight,
        )
        self.nn.optimizer.zero_grad()
        loss.backward()
        T.nn.utils.clip_grad_norm_(self.nn.parameters(), 1.0)
        self.nn.optimizer.step()
        self.update_counter += 1
        self.update_target()
        return float(loss.item())
