import numpy as np
import torch as T

from Gymnasium import KripsEnv
from Gymnasium.observation import encode_games


class GamePool:
    def __init__(self, num_envs: int, base_seed: int = 0) -> None:
        self.num_envs: int = num_envs
        self.base_seed: int = base_seed
        self.envs: list[KripsEnv] = []
        self.reset_counter: int = 0
        self.reset(base_seed)

    def reset(self, base_seed: int | None = None) -> T.Tensor:
        if base_seed is not None:
            self.base_seed = base_seed
        self.envs = []
        self.reset_counter = 0
        for index in range(self.num_envs):
            env = KripsEnv()
            env.reset(seed=self.base_seed + index)
            self.envs.append(env)
        return self.encode()

    @property
    def games(self) -> list:
        return [env.game for env in self.envs]

    def encode(self) -> T.Tensor:
        return T.from_numpy(encode_games(self.games))

    def current_players(self) -> np.ndarray:
        return np.array(
            [env.game.current_player.player_number for env in self.envs],
            dtype=np.int64,
        )

    def active(self) -> np.ndarray:
        return np.array([env.game.is_running for env in self.envs], dtype=bool)

    def active_indices(self) -> list[int]:
        return [index for index, env in enumerate(self.envs) if env.game.is_running]

    def step(
        self,
        actions: list,
    ) -> tuple[T.Tensor, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        rewards = np.zeros(self.num_envs, dtype=np.float32)
        terminated = np.zeros(self.num_envs, dtype=bool)
        off_turn = np.zeros(self.num_envs, dtype=bool)
        winners = np.zeros(self.num_envs, dtype=np.int64)

        for index, env in enumerate(self.envs):
            if not env.game.is_running:
                terminated[index] = True
                continue
            action = actions[index] if index < len(actions) else None
            if action is None:
                raise ValueError(f"No action for active env {index}")
            _, reward, term, _, info = env.step(action)
            rewards[index] = reward
            terminated[index] = term
            off_turn[index] = info["off_turn"]
            if term:
                winners[index] = self._winner(env.game)

        return self.encode(), rewards, terminated, off_turn, winners

    def step_off_turn(
        self,
        actions: list,
        next_states: T.Tensor,
    ) -> tuple[T.Tensor, np.ndarray, np.ndarray]:
        terminated = np.zeros(self.num_envs, dtype=bool)
        winners = np.zeros(self.num_envs, dtype=np.int64)
        updated = next_states.clone()

        for index, env in enumerate(self.envs):
            action = actions[index] if index < len(actions) else None
            if action is None or not env.game.is_running:
                continue
            state, term, _ = env.step_off_turn(action)
            updated[index] = T.from_numpy(state)
            terminated[index] = term
            if term:
                winners[index] = self._winner(env.game)

        return updated, terminated, winners

    def reset_finished(self, terminated: np.ndarray) -> None:
        self.reset_counter += 1
        for index, env in enumerate(self.envs):
            if terminated[index]:
                env.reset(
                    seed=self.base_seed + index + self.reset_counter * self.num_envs
                )

    @staticmethod
    def _winner(game) -> int:
        if game.player1.won:
            return 1
        if game.player2.won:
            return 2
        return 0
