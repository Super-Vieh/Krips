import torch as T

from .agent import Agent
from .game_pool import GamePool
from .reward_engine import RewardEngine
from .storage import Storage


class AgentTrainer:
    def __init__(
        self,
        agent: Agent,
        storage: Storage,
        batch_size: int = 256,
        discount_factor: float = 0.99,
    ) -> None:
        self.agent: Agent = agent
        self.storage: Storage = storage
        self.batch_size: int = batch_size
        self.discount_factor: float = discount_factor

    def train_step(self, batch_size: int | None = None) -> float:
        size = batch_size if batch_size is not None else self.batch_size
        batch = self.storage.sample_transitions(size)
        loss = self.agent.compute_loss(
            batch["states"],
            batch["actions"],
            batch["rewards"],
            batch["next_states"],
            batch["dones"],
            self.discount_factor,
        )
        self.agent.nn.optimizer.zero_grad()
        loss.backward()
        self.agent.nn.optimizer.step()
        return float(loss.item())

    def train(self, steps: int, batch_size: int | None = None) -> list[float]:
        return [self.train_step(batch_size) for _ in range(steps)]

    def collect(self, pool: GamePool, steps: int, epsilon: float = 0.0) -> int:
        reward_engine = RewardEngine()
        added = 0
        for _ in range(steps):
            indices = pool.active_indices()
            if not indices:
                break
            states = pool.encode()
            players = pool.current_players()
            picks = self.agent.act([pool.games[index] for index in indices], epsilon)
            actions: list[str | None] = [None] * len(pool.games)
            action_indices: list[int] = []
            for index, action in zip(indices, picks):
                actions[index] = action
                n, m = self.agent.decode_action(action)
                action_indices.append(n * 21 + m)
            next_states, terminal_rewards, terminated, active = pool.step(actions)
            rewards = reward_engine.reward(
                states, next_states, T.tensor(players, dtype=T.long)
            )
            index_tensor = T.tensor(indices, dtype=T.long)
            dones = T.tensor([not active[index] for index in indices], dtype=T.float32)
            self.storage.add_transitions(
                states[index_tensor],
                T.tensor(action_indices, dtype=T.long),
                rewards[index_tensor],
                next_states[index_tensor],
                dones,
            )
            added += len(indices)
        return added

    def train_on_pool(
        self,
        pool: GamePool,
        episodes: int,
        steps_per_episode: int,
        epsilon_start: float = 0.9,
        epsilon_decay: float = 0.99995,
        batch_size: int | None = None,
    ) -> list[float]:
        size = batch_size if batch_size is not None else self.batch_size
        epsilon = epsilon_start
        losses: list[float] = []
        for _ in range(episodes):
            self.collect(pool, steps_per_episode, epsilon)
            for _ in range(steps_per_episode):
                if len(self.storage.transitions) < size:
                    break
                losses.append(self.train_step(size))
            epsilon = max(0.01, epsilon * epsilon_decay)
            pool.reset()
        return losses
