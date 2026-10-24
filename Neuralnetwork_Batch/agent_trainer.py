import numpy as np
import torch as T

from .agent import Agent
from .game_pool import GamePool
from .qualing_q_learning import DualingQNetwork
from .reward_engine import RewardEngine
from .storage import Storage
from .tensor_metric_board import TensorMetricBoard


class AgentTrainer:
    def __init__(
        self,
        batch_size: int = 256,
        buffer_capacity: int = 100_000,
        n_envs: int = 8,
        seed: int = 0,
        updates_per_round: int = 1,
        log_to_tensorboard: bool = True,
    ) -> None:
        self.batch_size: int = batch_size
        self.buffer_capacity: int = buffer_capacity
        self.n_envs: int = n_envs
        self.seed: int = seed
        self.updates_per_round: int = updates_per_round
        self.log_to_tensorboard: bool = log_to_tensorboard
        self.agent1: Agent = Agent(
            DualingQNetwork(0.001, "BatchAgent1.txt"),
            Storage(buffer_capacity),
            player_number=1,
            seed=seed,
        )
        self.agent2: Agent = Agent(
            DualingQNetwork(0.001, "BatchAgent2.txt"),
            Storage(buffer_capacity),
            player_number=2,
            seed=seed + 1,
        )
        self.reward_engine: RewardEngine = RewardEngine()
        self.tensorboard: TensorMetricBoard | None = None
        self.pool: GamePool = GamePool(n_envs, seed)

    def load_nn(
        self,
        file_path1: str,
        file_path2: str,
        learning_rate: float = 0.001,
    ) -> None:
        self.agent1.nn = DualingQNetwork(learning_rate, file_path1)
        self.agent1.nn.load_savestate()
        self.agent2.nn = DualingQNetwork(learning_rate, file_path2)
        self.agent2.nn.load_savestate()

    def train_agents(
        self,
        nr_epochs: int,
        episodes_per_epoch: int,
        steps: int,
        start_epsilon: float = 0.9,
        discount_factor: float = 0.9,
        epsilon_decay: float = 0.99995,
        n_envs: int | None = None,
        opponent=None,
        updates_per_round: int | None = None,
    ) -> None:
        if n_envs is not None and n_envs != self.n_envs:
            self.n_envs = n_envs
            self.pool = GamePool(n_envs, self.seed)
        if updates_per_round is not None:
            self.updates_per_round = updates_per_round

        epsilon = start_epsilon
        global_step = 0
        self.tensorboard = (
            TensorMetricBoard() if self.log_to_tensorboard else None
        )
        try:
            for epoch in range(nr_epochs):
                epoch_stats: list[dict] = []
                for _ in range(episodes_per_epoch):
                    self.pool.reset(self.seed + global_step)
                    stats = self._run_episode(
                        steps,
                        epsilon,
                        discount_factor,
                        epsilon_decay,
                        opponent,
                        global_step,
                    )
                    global_step += stats["rounds"]
                    epsilon = stats["epsilon"]
                    epoch_stats.append(stats)
                if self.tensorboard is not None:
                    self.tensorboard.log_epoch(
                        epoch, self._aggregate(epoch_stats)
                    )
        finally:
            self.agent1.nn.save_savestate()
            if opponent is None:
                self.agent2.nn.save_savestate()
            if self.tensorboard is not None:
                self.tensorboard.close()

    def _run_episode(
        self,
        steps: int,
        epsilon: float,
        discount_factor: float,
        epsilon_decay: float,
        opponent,
        global_step: int,
    ) -> dict:
        stats: dict = {
            "rounds": 0,
            "reward_a1": [],
            "reward_a2": [],
            "loss_a1": [],
            "loss_a2": [],
            "win_a1": 0,
            "win_a2": 0,
            "draw": 0,
            "games": 0,
            "epsilon": epsilon,
        }
        history: list[T.Tensor] = []
        rounds = 0

        for _ in range(steps):
            states = self.pool.encode()
            previous_states = history[-2] if len(history) >= 2 else None
            players = self.pool.current_players()
            active = self.pool.active()
            idx1 = [i for i in range(self.n_envs) if active[i] and players[i] == 1]
            idx2 = [i for i in range(self.n_envs) if active[i] and players[i] == 2]

            actions: list = [None] * self.n_envs
            indices: dict[int, int] = {}

            if idx1:
                moves = self.agent1.act_batch(
                    [self.pool.games[i] for i in idx1], epsilon
                )
                for index, move in zip(idx1, moves):
                    actions[index] = move
                    indices[index] = self.agent1.move_to_index(move)

            if idx2:
                if opponent is None:
                    moves = self.agent2.act_batch(
                        [self.pool.games[i] for i in idx2], epsilon
                    )
                    for index, move in zip(idx2, moves):
                        actions[index] = move
                        indices[index] = self.agent2.move_to_index(move)
                else:
                    for index in idx2:
                        actions[index] = opponent.act(self.pool.games[index])

            next_states, _, terminated, off_turn, winners = self.pool.step(actions)

            if off_turn.any():
                responses: list = [None] * self.n_envs
                for index in np.flatnonzero(off_turn):
                    responder = 2 if players[index] == 1 else 1
                    if responder == 1:
                        responses[index] = self.agent1.act_off_turn(
                            self.pool.games[index], epsilon
                        )
                    elif opponent is None:
                        responses[index] = self.agent2.act_off_turn(
                            self.pool.games[index], epsilon
                        )
                    else:
                        responses[index] = opponent.act_off_turn(
                            self.pool.games[index]
                        )
                next_states, off_terminated, off_winners = self.pool.step_off_turn(
                    responses, next_states
                )
                terminated = terminated | off_terminated
                winners = np.where(off_winners > 0, off_winners, winners)

            for winner in winners[terminated]:
                if winner == 1:
                    stats["win_a1"] += 1
                elif winner == 2:
                    stats["win_a2"] += 1
                else:
                    stats["draw"] += 1
            stats["games"] += int(terminated.sum())
            self.pool.reset_finished(terminated)

            rewards = self.reward_engine.reward(
                states,
                next_states,
                T.tensor(players, dtype=T.long),
                previous_states,
            )
            history.append(states)
            if len(history) > 2:
                history.pop(0)

            made = len(idx1) + len(idx2)
            changed = (next_states != states).any(dim=1)
            valid = int(changed[idx1 + idx2].sum()) if made else 0
            dones = T.from_numpy(terminated.astype(np.float32))

            if idx1:
                idx_tensor = T.tensor(idx1, dtype=T.long)
                actions_tensor = T.tensor(
                    [indices[index] for index in idx1], dtype=T.long
                )
                self.agent1.storage.add_transitions(
                    states[idx_tensor],
                    actions_tensor,
                    rewards[idx_tensor],
                    next_states[idx_tensor],
                    dones[idx_tensor],
                )
                stats["reward_a1"].append(float(rewards[idx_tensor].mean()))

            if idx2 and opponent is None:
                idx_tensor = T.tensor(idx2, dtype=T.long)
                actions_tensor = T.tensor(
                    [indices[index] for index in idx2], dtype=T.long
                )
                self.agent2.storage.add_transitions(
                    states[idx_tensor],
                    actions_tensor,
                    rewards[idx_tensor],
                    next_states[idx_tensor],
                    dones[idx_tensor],
                )
                stats["reward_a2"].append(float(rewards[idx_tensor].mean()))

            losses1: list[float] = []
            losses2: list[float] = []
            for _ in range(self.updates_per_round):
                if len(self.agent1.storage) >= self.batch_size:
                    losses1.append(
                        self.agent1.train_step(self.batch_size, discount_factor)
                    )
                if (
                    idx2
                    and opponent is None
                    and len(self.agent2.storage) >= self.batch_size
                ):
                    losses2.append(
                        self.agent2.train_step(self.batch_size, discount_factor)
                    )

            loss1: float | None = (
                float(np.mean(losses1)) if losses1 else None
            )
            loss2: float | None = (
                float(np.mean(losses2)) if losses2 else None
            )
            if loss1 is not None:
                stats["loss_a1"].append(loss1)
            if loss2 is not None:
                stats["loss_a2"].append(loss2)

            round_losses = [value for value in (loss1, loss2) if value is not None]
            total_loss = float(np.mean(round_losses)) if round_losses else 0.0
            total_reward = (
                float(rewards[idx1 + idx2].mean()) if made else 0.0
            )
            reward_loss_ratio = (
                total_reward / (-total_loss) if total_loss != 0 else 0.0
            )
            valid_moves_ratio = valid / made if made else 0.0
            if self.tensorboard is not None:
                self.tensorboard.log_turn(
                    global_step + rounds,
                    made,
                    valid,
                    epsilon,
                    total_reward,
                    total_loss,
                    reward_loss_ratio,
                    valid_moves_ratio,
                )
                self.tensorboard.log_step(
                    global_step + rounds,
                    {
                        "loss_a1": loss1 if loss1 is not None else 0.0,
                        "loss_a2": loss2 if loss2 is not None else 0.0,
                        "buffer_a1": len(self.agent1.storage),
                        "buffer_a2": len(self.agent2.storage),
                    },
                )

            rounds += 1
            if epsilon > 0.5:
                epsilon = epsilon * (epsilon_decay ** self.updates_per_round)

        stats["rounds"] = rounds
        stats["epsilon"] = epsilon
        return stats

    def _aggregate(self, episodes: list[dict]) -> dict:
        metrics: dict[str, float] = {}
        for key in ("reward_a1", "reward_a2", "loss_a1", "loss_a2"):
            values = [value for episode in episodes for value in episode[key]]
            metrics[key] = float(np.mean(values)) if values else 0.0
        metrics["epsilon"] = float(episodes[-1]["epsilon"]) if episodes else 0.0
        metrics["win_a1"] = int(sum(episode["win_a1"] for episode in episodes))
        metrics["win_a2"] = int(sum(episode["win_a2"] for episode in episodes))
        metrics["draw"] = int(sum(episode["draw"] for episode in episodes))
        metrics["games"] = int(sum(episode["games"] for episode in episodes))
        metrics["steps"] = int(sum(episode["rounds"] for episode in episodes))
        metrics["buffer_a1"] = len(self.agent1.storage)
        metrics["buffer_a2"] = len(self.agent2.storage)
        return metrics
