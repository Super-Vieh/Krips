import torch as T


class RewardEngine:
    def __init__(self, storage=None, game=None) -> None:
        self.storage = storage
        self.game = game

    def reward(
        self,
        states: T.Tensor,
        next_states: T.Tensor,
        player_numbers: T.Tensor,
        previous_states: T.Tensor | None = None,
    ) -> T.Tensor:
        player_numbers = T.as_tensor(player_numbers, device=states.device)
        rewards = T.zeros(states.shape[0], dtype=T.float32, device=states.device)

        changed = (next_states != states).any(dim=1)
        rewards = rewards + (~changed).float() * -5.0

        if previous_states is not None:
            repeated = (next_states == previous_states).all(dim=1)
            rewards = rewards + repeated.float() * -5.0

        middle_changed = (next_states[:, 728:1144] != states[:, 728:1144]).any(dim=1)
        rewards = rewards + middle_changed.float() * 3.0

        player1_changed = (next_states[:, 0:156] != states[:, 0:156]).any(dim=1)
        player2_changed = (next_states[:, 156:312] != states[:, 156:312]).any(dim=1)
        side_changed = (next_states[:, 312:728] != states[:, 312:728]).any(dim=1)
        player1_to_board = (player_numbers == 1) & player1_changed & side_changed
        player2_to_board = (player_numbers == 2) & player2_changed & side_changed
        rewards = rewards + (player1_to_board | player2_to_board).float() * 10.0

        player1_put_card = next_states[:, 0:52].sum(dim=1) == states[:, 0:52].sum(dim=1) - 1
        player1_stock_got_card = next_states[:, 52:104].sum(dim=1) == states[:, 52:104].sum(dim=1) + 1
        player2_put_card = next_states[:, 156:208].sum(dim=1) == states[:, 156:208].sum(dim=1) - 1
        player2_stock_got_card = next_states[:, 208:260].sum(dim=1) == states[:, 208:260].sum(dim=1) + 1
        ended_move = T.where(
            player_numbers == 1,
            player1_put_card & player1_stock_got_card,
            player2_put_card & player2_stock_got_card,
        )
        rewards = T.where(ended_move, T.ones_like(rewards), rewards)

        empty_before = self._count_empty_tableau(states)
        empty_after = self._count_empty_tableau(next_states)
        rewards = rewards + (empty_after - empty_before).clamp(min=0) * 0.15

        return rewards

    def _count_empty_tableau(self, states: T.Tensor) -> T.Tensor:
        counts = T.zeros(states.shape[0], dtype=T.float32, device=states.device)
        for index in range(8):
            block = states[:, 312 + index * 52: 312 + (index + 1) * 52]
            counts = counts + (block.sum(dim=1) == 0).float()
        return counts
