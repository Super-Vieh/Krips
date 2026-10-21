import torch as T

from Klassen import Karten, Spiel

ACTION1: list[str] = [
    "K0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "A0", "A1", "A2",
]

ACTION2: list[str] = [
    "K0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8",
    "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8",
    "A0", "A1", "A2", "G0",
]


def _top(pile: list[Karten]) -> Karten | None:
    if not pile:
        return None
    return pile[-1]


def _player_piles(game: Spiel) -> list[list[Karten]]:
    if game.current.spielernummer == 1:
        return [game.spieler1Paechen, game.spieler1Haufen, game.spieler1Dreizehner]
    return [game.spieler2Paechen, game.spieler2Haufen, game.spieler2Dreizehner]


def _own_haufen(game: Spiel) -> list[Karten]:
    if game.current.spielernummer == 1:
        return game.spieler1Haufen
    return game.spieler2Haufen


def _can_place_on_tableau(game: Spiel, card: Karten, slot: int) -> bool:
    pile = game.platzliste[slot - 1]
    if not pile:
        return True
    top = pile[-1]
    return top.kartenwert.value == card.kartenwert.value + 1 and top.farbe != card.farbe


def _can_place_on_foundation(game: Spiel, card: Karten, slot: int) -> bool:
    pile = game.mittlereliste[slot - 1]
    if card.kartenwert.value == 1:
        if slot in (1, 2):
            return card.kartentyp.value == "Pik" and not pile
        if slot in (3, 4):
            return card.kartentyp.value == "Coeur" and not pile
        if slot in (5, 6):
            return card.kartentyp.value == "Treff" and not pile
        return card.kartentyp.value == "Karro" and not pile
    if not pile:
        return False
    top = pile[-1]
    return top.kartenwert.value + 1 == card.kartenwert.value and top.kartentyp == card.kartentyp


def _moves_from_card(game: Spiel, card: Karten, prefix: str) -> list[str]:
    moves: list[str] = []
    for slot in range(1, 9):
        if _can_place_on_tableau(game, card, slot):
            moves.append(f"{prefix}S{slot}")
        if _can_place_on_foundation(game, card, slot):
            moves.append(f"{prefix}M{slot}")
    return moves


def legal_moves(game: Spiel) -> list[str]:
    moves: list[str] = []
    piles = _player_piles(game)
    paechen, haufen, dreizehner = piles
    top_p = _top(paechen)
    top_d = _top(dreizehner)

    if top_p is not None and not top_p.karteOffen:
        moves.append("A0A0")
    if top_d is not None and not top_d.karteOffen:
        moves.append("A2A2")
    if (top_p is not None and top_p.karteOffen) or (top_p is None and haufen):
        moves.append("A0A1")

    for origin, pile in enumerate(piles):
        top = _top(pile)
        if top is None or not top.karteOffen:
            continue
        moves.extend(_moves_from_card(game, top, f"A{origin}"))
        if game.current.kann_gegener_geben(top):
            moves.append(f"A{origin}G0")

    own_haufen = _own_haufen(game)
    for origin, pile in enumerate(game.platzliste, start=1):
        top = _top(pile)
        if top is None or not top.karteOffen:
            continue
        moves.extend(_moves_from_card(game, top, f"S{origin}"))
        if own_haufen and game.current.kann_gegener_geben(top):
            moves.append(f"S{origin}G0")

    return moves


def action_to_pair(action: str) -> tuple[int, int]:
    return ACTION1.index(action[0:2]), ACTION2.index(action[2:4])


def pair_to_action(n: int, m: int) -> str:
    return ACTION1[n] + ACTION2[m]


def legal_mask(game: Spiel) -> T.Tensor:
    mask = T.zeros((12, 21), dtype=T.bool)
    if not game.gameon:
        return mask
    for action in legal_moves(game):
        n, m = action_to_pair(action)
        mask[n, m] = True
    return mask


def legal_masks(games: list[Spiel]) -> T.Tensor:
    if not games:
        return T.zeros((0, 12, 21), dtype=T.bool)
    return T.stack([legal_mask(game) for game in games])


def off_turn_mask(game: Spiel) -> T.Tensor:
    return T.tensor([True, bool(game.wouldbeKrips)], dtype=T.bool)
