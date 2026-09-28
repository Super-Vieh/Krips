import random

from .board import Board
from .card import Card
from .card_property_enum import CardType, CardValue
from .game import Game
from .move import DestinationType, Move, OriginType
from .player import Player
from .rules import Rules

# Die Klasse Game_Orchestor baut das Spiel auf, gibt den Spielstand auf der Konsole aus
# und übersetzt die Zug-Notation (z.B. "A0A0") in Move-Objekte für Game.play_move().
# Die Konsolenausgabe ist identisch zu der alten SpielInitialisierer-Klasse.
class GameOrchestor:

    # Farben der Kartenarten, wie in der alten Ausgabe
    _COLOR: dict[CardType, str] = {
        CardType.Pik: "\033[30m",
        CardType.Coeur: "\033[31m",
        CardType.Treff: "\033[90m",
        CardType.Karro: "\033[35m",
    }
    # Reihenfolge der Stiftungen auf dem Board: Pik, Coeur, Treff, Karro (je 2 Felder)
    _FOUNDATION_SUIT: tuple[CardType, ...] = (CardType.Pik, CardType.Coeur, CardType.Treff, CardType.Karro)

    def __init__(self, seed: int):
        # seed macht die Kartenverteilung reproduzierbar
        self.rng: random.Random = random.Random(seed)

    def create_deck(self) -> list[Card]:
        templist: list[Card] = []  # Speichert die Karten
        card_type = list(CardType)
        card_value = list(CardValue)

        for i in range(len(card_type)):
            for j in range(len(card_value)):
                templist.append(Card(card_type[i], card_value[j]))
        return templist

    def set_up_game(self) -> Game:
        # Entspricht SpielInitialisierer.set_up_game + set_up_fist_moves
        game: Game = Game()
        game.board = Board()

        deck1: list[Card] = self.create_deck()
        deck2: list[Card] = self.create_deck()
        self.rng.shuffle(deck1)
        self.rng.shuffle(deck2)

        player1: Player = Player(1, deck1)
        player2: Player = Player(2, deck2)

        player1.set_opponent(player2)
        player2.set_opponent(player1)
        player1.set_game(game)
        player2.set_game(game)

        game.player1 = player1
        game.player2 = player2
        game.rules = Rules(game)

        player1.distribute_cards_to_decks()
        player2.distribute_cards_to_decks()

        game.play_fist_cards()

        game.decide_first_player()
        return game

    @staticmethod
    def sanitize_notation(notation: str) -> str | None:
        clean: str = notation.strip().upper()
        if clean in ("P", "R", "K", "M"):
            return clean


        if clean in ("A0", "A2"):
            return clean
        if clean in ("A0A0", "A2A2"):
            return clean


        if len(clean) != 4:
            return None
        if not clean[1].isdigit() or not clean[3].isdigit():
            return None

        source: int = int(clean[1])
        destination: int = int(clean[3])


        match clean[0]:
            case "A":
                if source not in (0, 1, 2):
                    return None
            case "S":
                if not 1 <= source <= 8:
                    return None
            case _:
                return None


        match clean[2]:
            case "A":

                if clean[0] == "S":
                    return None
                if destination not in (0, 1, 2):
                    return None
            case "S" | "M":
                if not 1 <= destination <= 8:
                    return None
            case "G":
                pass
            case _:
                return None

        return clean

    @staticmethod
    def notation_to_move(notation: str) -> Move | None:
        # Übersetzt die Zug-Notation in ein Move-Objekt.
        # Die Prüfung der Eingabe macht sanitize_notation, hier wird nur
        # noch von 1-basiert (S, M) auf die 0-basierten Indizes von Move umgerechnet.
        # Für "K" (Krips) gibt es noch kein Move-Objekt, deshalb None.
        clean: str | None = GameOrchestor.sanitize_notation(notation)
        if clean is None:
            return None

        # Krips und die Konsoleneingabe M haben kein Move-Objekt
        if clean in ("K", "M"):
            return None

        # Zug beenden: oberste Karte vom Päckchen auf den Haufen
        if clean == "P":
            return Move(OriginType.PLAYER, 0, DestinationType.PLAYER, 1)

        # Haufen umdrehen, nur wenn das Päckchen leer ist
        if clean == "R":
            return Move(OriginType.PLAYER, 0, DestinationType.PLAYER, 0)

        # Aufdecken: A0 ist das Päckchen, A2 das Dreizehner Päckchen
        if clean in ("A0", "A0A0"):
            return Move(OriginType.PLAYER, 0, DestinationType.PLAYER, 0)
        if clean in ("A2", "A2A2"):
            return Move(OriginType.PLAYER, 2, DestinationType.PLAYER, 2)

        source: int = int(clean[1])
        destination: int = int(clean[3])

        match clean[0]:
            case "A":
                origin_type: OriginType = OriginType.PLAYER  # 0-2 bleibt 0-2
            case "S":
                origin_type: OriginType = OriginType.TABLEAU
                source -= 1  # S1-8 wird zu Index 0-7
            case _:
                return None

        match clean[2]:
            case "A":
                destination_type: DestinationType = DestinationType.PLAYER  # 0-2 bleibt 0-2
            case "S":
                destination_type: DestinationType = DestinationType.TABLEAU
                destination -= 1  # S1-8 wird zu Index 0-7
            case "M":
                destination_type: DestinationType = DestinationType.FOUNDATION
                destination -= 1  # M1-8 wird zu Index 0-7
            case _:
                destination_type: DestinationType = DestinationType.OPPONENT
                destination = 0  # Der Gegner hat nur einen Haufen

        return Move(origin_type, source, destination_type, destination)

    @staticmethod
    def _top_card(pile: list[Card]) -> Card | None:
        # Es kann passieren das die listen kein element haben dann wird null geprintet
        if not pile:
            return None
        return pile[-1]

    @staticmethod
    def print_card(card: Card) -> None:
        # Eine Karte in ihrer Kartenart-Farbe, wie in der alten print_sidesplus
        print(f"{GameOrchestor._COLOR[card.card_type]}{card.card_rank.value}\033[0m", end=",")

    @staticmethod
    def print_middle(board: Board, i: int) -> None:
        # Die beiden Stiftungen einer Kartenart.
        # i = 0 Pik, 1 Coeur, 2 Treff, 3 Karro -> Stiftungen 2*i und 2*i+1
        color: str = GameOrchestor._COLOR[GameOrchestor._FOUNDATION_SUIT[i]]
        foundation1: list[Card] = board.foundations[2 * i]
        foundation2: list[Card] = board.foundations[2 * i + 1]

        if foundation1 and foundation2:
            print(f"___ {color}{foundation1[-1].card_rank.value}\033[0m", end="-")
            print(f"{color}{foundation2[-1].card_rank.value}\033[0m", end="___ ")
        elif not foundation1 and not foundation2:
            print(f"{color}___null-null\033[0m", end="___")
        elif not foundation1 and foundation2:
            print(f"{color}___null-{foundation2[-1].card_rank.value}\033[0m", end="___ ")
        elif foundation1 and not foundation2:
            print(f"{color}___ {foundation1[-1].card_rank.value}-null\033[0m", end="___ ")

    @staticmethod
    def print_sidesplus(board: Board) -> None:
        # Pro Zeile: die Seitenliste von Spieler 1 (von oben nach unten),
        # dann die beiden Stiftungen, dann die Seitenliste von Spieler 2
        for i in range(4):
            player1_pile: list[Card] = board.tableau[i]
            for j in range(len(player1_pile)):
                GameOrchestor.print_card(player1_pile[len(player1_pile) - j - 1])

            GameOrchestor.print_middle(board, i)

            player2_pile: list[Card] = board.tableau[i + 4]
            for j in range(len(player2_pile)):
                GameOrchestor.print_card(player2_pile[j])
            print()

    @staticmethod
    def print_top(player2: Player) -> None:
        print("\nSpieler2:")
        # Es kann passieren das die listen kein ellement haben dann wird null geprintet
        top_stock: Card | None = GameOrchestor._top_card(player2.player_stock)
        top_waste: Card | None = GameOrchestor._top_card(player2.player_waste)
        top_reserve: Card | None = GameOrchestor._top_card(player2.player_reserve)

        if top_stock is None:
            print("null", end="   ")
        elif top_stock.is_face_up:
            print(top_stock.card_rank.value, end="-")
            print(top_stock.card_type.value, end="   ")
        else:
            print("Closed", end="   ")

        if top_waste is None:
            print("null", end="   ")
        elif top_waste.is_face_up:
            print(top_waste.card_rank.value, end="-")
            print(top_waste.card_type.value, end="   ")

        if top_reserve is None:
            print("null", end="   ")
        elif top_reserve.is_face_up:
            print(top_reserve.card_rank.value, end="-")
            print(top_reserve.card_type.value, end="   ")
        else:
            print("Closed", end="")
        print("\n")

    @staticmethod
    def print_bot(player1: Player) -> None:
        print("\n")
        print("Spieler1:")
        # Es kann passieren das die listen kein ellement haben dann wird null geprintet
        top_stock: Card | None = GameOrchestor._top_card(player1.player_stock)
        top_waste: Card | None = GameOrchestor._top_card(player1.player_waste)
        top_reserve: Card | None = GameOrchestor._top_card(player1.player_reserve)

        if top_stock is None:
            print("null", end="   ")
        elif top_stock.is_face_up:
            print(top_stock.card_rank.value, end="-")
            print(top_stock.card_type.value, end="   ")
        else:
            print("Closed", end="   ")

        if top_waste is None:
            print("null", end="   ")
        elif top_waste.is_face_up:
            print(top_waste.card_rank.value, end="-")
            print(top_waste.card_type.value, end="   ")

        if top_reserve is None:
            print("null", end="   ")
        elif top_reserve.is_face_up:
            print(top_reserve.card_rank.value, end="-")
            print(top_reserve.card_type.value, end="   ")
        else:
            print("Closed", end="")

    def play_console(self, game: Game) -> list[str]:
        # Eine Spiel Simulation in der Konsole ohne Gui
        list_of_recordedactions: list[str] = []
        while game.is_running:
            # print_top, print_sidesplus und print_bot geben die Karten auf der Konsole aus
            GameOrchestor.print_top(game.player2)
            GameOrchestor.print_sidesplus(game.board)
            GameOrchestor.print_bot(game.player1)

            action: str = input(f"\nSpieler{game.current_player.player_number} ist drann."
                                "\nWas soll gemacht werden?\n"
                                "Karte aufdecken = A0 oder A2\n"  # Aufgedeckt werden können nur Päckchen und Dreizehner
                                "Karte hilegen = (A0-2,S1-8,)M1-8*S1-8*G0\n"
                                "Runde Aufhören= P,Kartenhaufen umdrehen = R,Krips rufen = K\n"
                                "Stop =M\n")
            # Die Eingabe wird zuerst aufgeräumt und geprüft
            notation: str | None = GameOrchestor.sanitize_notation(action)

            if notation == "M":
                return list_of_recordedactions
            if notation is None:
                print("Ungültige Aktion.")
                continue
            list_of_recordedactions.append(notation)

            if notation == "K":
                print("Krips ist im neuen Game noch nicht angeschlossen.")
                continue

            move: Move | None = GameOrchestor.notation_to_move(notation)
            if move is None:
                print("Ungültige Aktion.")
                continue

            game.play_move(move)
        return list_of_recordedactions
