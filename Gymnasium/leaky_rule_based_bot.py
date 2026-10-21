import random

from Klassen.card import Card
from Klassen.game import Game
from Klassen.move import DestinationType, Move, OriginType

#Von der Ki Implementiert
class LeakyRuleBasedBot:

    BASE_SCORE: dict[tuple[OriginType, DestinationType], int] = {
        (OriginType.PLAYER, DestinationType.FOUNDATION): 400,
        (OriginType.TABLEAU, DestinationType.FOUNDATION): 500,
        (OriginType.TABLEAU, DestinationType.TABLEAU): -300,
        (OriginType.PLAYER, DestinationType.OPPONENT): 300,
        (OriginType.TABLEAU, DestinationType.OPPONENT): 300,
    }

    RANK_FACTORS: dict[tuple[OriginType, DestinationType], int] = {
        (OriginType.PLAYER, DestinationType.TABLEAU): 20,
        (OriginType.TABLEAU, DestinationType.TABLEAU): 2,
        (OriginType.PLAYER, DestinationType.OPPONENT): 20,
        (OriginType.TABLEAU, DestinationType.OPPONENT): 20,
    }

    PLAYER_SOURCE_BONUS: dict[DestinationType, int] = {
        DestinationType.TABLEAU: 150,
    }

    RESERVE_BONUS: dict[DestinationType, int] = {
        DestinationType.TABLEAU: 600,
        DestinationType.OPPONENT: 400,
    }

    PLAYER_MOVE_SCORE: dict[tuple[int, int], int] = {
        (0, 0): 200,
        (0, 1): -100,
        (2, 2): 500,
    }

    FOUNDATION_FREES_PILE_BONUS: int = 3000
    STOCK_FLIP_BONUS: int = 50

    def __init__(self, seed: int, mistake_rate: float = 0.1, krips_miss_rate: float = 0.1):
        self.rng: random.Random = random.Random(seed)
        self.mistake_rate: float = mistake_rate
        self.krips_miss_rate: float = krips_miss_rate

    def act(self, game: Game) -> Move:
        legal_moves: list[Move] = game.rules.get_all_valid_moves()
        if not legal_moves:
            raise ValueError("No legal moves available")
        if self.rng.random() < self.mistake_rate:
            return self.rng.choice(legal_moves)
        foundation_moves: list[Move] = game.rules.possible_moves_to_foundation()
        scores: list[int] = [self._score_move(game, move, foundation_moves) for move in legal_moves]
        best_score: int = max(scores)
        best_moves: list[Move] = [move for move, score in zip(legal_moves, scores) if score == best_score]
        return self.rng.choice(best_moves)

    def act_off_turn(self, game: Game) -> Move:
        legal_moves: list[Move] = game.rules.get_valid_moves_when_not_playing()
        if not legal_moves:
            raise ValueError("No legal off-turn moves available")
        krips_call = Move(OriginType.KRIPS, 1, DestinationType.KRIPS, 1)
        if krips_call in legal_moves:
            if self.rng.random() < self.krips_miss_rate:
                return Move(OriginType.KRIPS, 0, DestinationType.KRIPS, 0)
            return krips_call
        return legal_moves[0]

    def _source_pile(self, game: Game, move: Move) -> list[Card]:
        if move.origin_type == OriginType.PLAYER:
            return game.current_player.player_piles[move.origin_value]
        if move.origin_type == OriginType.TABLEAU:
            return game.board.tableau[move.origin_value]
        return []

    def _krips_penalty(self, game: Game, move: Move, foundation_moves: list[Move]) -> int:
        if not game.would_be_krips or not foundation_moves:
            return 0
        tableau_foundation_exists: bool = any(
            possible.origin_type == OriginType.TABLEAU for possible in foundation_moves
        )
        if move not in foundation_moves:
            return -100000
        if tableau_foundation_exists and move.origin_type == OriginType.PLAYER:
            return -100000
        return 0

    def _score_player_move(self, game: Game, move: Move) -> int:
        key = (move.origin_value, move.destination_value)
        score: int = self.PLAYER_MOVE_SCORE.get(key, 0)
        player = game.current_player
        if key == (0, 0) and player.player_stock and not player.player_stock[-1].is_face_up:
            score += self.STOCK_FLIP_BONUS
        return score

    def _score_move(self, game: Game, move: Move, foundation_moves: list[Move]) -> int:
        score: int = self._krips_penalty(game, move, foundation_moves)
        source: list[Card] = self._source_pile(game, move)
        rank: int = source[-1].card_rank.value if source else 0
        key = (move.origin_type, move.destination_type)

        if move.destination_type == DestinationType.PLAYER:
            return score + self._score_player_move(game, move)

        score += self.BASE_SCORE.get(key, 0)
        score += rank * self.RANK_FACTORS.get(key, 0)

        if move.destination_type == DestinationType.FOUNDATION and len(source) == 1:
            score += self.FOUNDATION_FREES_PILE_BONUS
        if move.origin_type == OriginType.PLAYER:
            if move.origin_value == 2:
                score += self.RESERVE_BONUS.get(move.destination_type, 0)
            else:
                score += self.PLAYER_SOURCE_BONUS.get(move.destination_type, 0)

        return score
