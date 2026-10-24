import numpy as np

from Klassen import Card, CardType, Game

VECTOR_SIZE: int = 1144

SUIT_INDEX: dict[CardType, int] = {
    CardType.Pik: 0,
    CardType.Coeur: 1,
    CardType.Treff: 2,
    CardType.Karro: 3,
}


def game_piles(game: Game) -> list[list[Card]]:
    return [
        game.player1.player_stock,
        game.player1.player_waste,
        game.player1.player_reserve,
        game.player2.player_stock,
        game.player2.player_waste,
        game.player2.player_reserve,
        *game.board.tableau,
        *game.board.foundations,
    ]


def encode_game(game: Game, out: np.ndarray | None = None) -> np.ndarray:
    target = np.zeros(VECTOR_SIZE, dtype=np.float32) if out is None else out
    for index, pile in enumerate(game_piles(game)):
        if not pile:
            continue
        offset = index * 52
        top_hidden = not pile[-1].is_face_up
        for card in pile:
            if not card.is_face_up:
                if top_hidden:
                    break
                continue
            target[offset + SUIT_INDEX[card.card_type] * 13 + card.card_rank.value - 1] = 1.0
    return target


def encode_games(games: list[Game]) -> np.ndarray:
    states = np.zeros((len(games), VECTOR_SIZE), dtype=np.float32)
    for index, game in enumerate(games):
        encode_game(game, states[index])
    return states
