import random

from .board import Board
from .card import Card, CardType, CardValue
from .move import Move, OriginType, DestinationType
from .player import Player
from .rules import Rules
# Die Klasse Game beinhaltet alle Daten, die das Spiel selber betreffen.
# Die anfangsanktionen werden hier durchgeführt.(kartendeck erstellung, game_first_move)
# Das Spiel wird hier gestartet und die Aktionen der Spieler werden hier durchgeführt nach dem Algorithmus der Funktion play().
class Game:

    def __init__(self) -> None:
        self.current_player: Player = None
        self.is_running: bool = True
        self.would_be_krips: bool = False
        self.player1: Player = None
        self.player2: Player = None
        self.board:Board = None
        self.rules: Rules = None
        self.stalemate_counter: int = 0
        self.last_player_pile_lengths: list[int] = []

    def play_fist_cards(self) -> None:
        for index ,tableau_list in enumerate(self.board.tableau):
            if index <= 3:
                tableau_list.append(self.player1.player_stock.pop())
            else:
                tableau_list.append(self.player2.player_stock.pop())
            tableau_list[-1].is_face_up = True



    def decide_first_player(self) -> None:
        # Hier wird entschieden wer anfängt. Die Höchste karte auf dem Dreizehner päckchen gewinnt
        # Wenn die karten gleich sind werden die ausgelegten nach unt
        drz1: Card = self.player1.player_reserve[-1]
        drz2: Card = self.player2.player_reserve[-1]


        if (drz1.card_rank.value > drz2.card_rank.value) or (drz1.card_rank.value == 1 and drz2.card_rank.value != 1):  # stimmt wenn player1 die höhere karte hat
            self.current_player = self.player1
            #Hier wird die möglichkeit auf das erste Krips geschaffen.
            self.would_be_krips = self.rules.could_be_krips()
        elif (drz1.card_rank.value < drz2.card_rank.value) or (drz2.card_rank.value == 1 and drz1.card_rank.value != 1):  # stimmt wenn player2 die höhere karte hat
            self.current_player = self.player2
            self.would_be_krips = self.rules.could_be_krips()


        else:
            for index in range(4):  #geht durch die ersten 4 plätze auf jeder seite durch und vergleich sie
                if self.board.tableau[index][-1].card_rank.value == 1 and not self.board.tableau[index+4][-1].card_rank.value == 1:
                    self.current_player = self.player1
                    return None
                elif not self.board.tableau[index][-1].card_rank.value == 1 and self.board.tableau[index+4][-1].card_rank.value == 1:
                    self.current_player = self.player2
                    return None

                if (self.board.tableau[index][-1].card_rank.value > self.board.tableau[index + 4][-1].card_rank.value):
                    print("Schleife engaged player1 ist drann?")
                    self.current_player= self.player1
                    return None
                elif (self.board.tableau[index][-1].card_rank.value < self.board.tableau[index + 4][-1].card_rank.value):
                    print("Schleife engaged player2 ist drann?")
                    self.current_player = self.player2
                    return None
        return None

    def play_move(self, action: Move) -> None:
        #Diese Funktion beinhaltet die Spielregeln und ist der ort an dem das Spielgeschehen stattfindet.

        # action ist ein bis zu 4 stelliger string aus Buchsabe, Zahl, Buchtabe ,Zahl
        # der erste buchstabe bestimmt die art der liste aus der die karte genommen wird oder eine bestimmte aktion
        # der zweite buchstabe bestimmt die art der liste auf die die karte gelegt wird
        # die erste zahl bestimmt die position der karte der Ursprungsliste, also die genaue liste. es wird immer die letzte karte einer Liste genommen.
        # die zweite zahl macht genau das gleiche wie die erste nur für die Ziel liste.

        # Es gibt 4 verschiedene Listenarten: A = Hauptliste, S = Seitenliste, M = Mittelliste, G = Gegnerliste

        # Die Hauptliste ist die Liste der Karten die der Spieler auf der Hand hat. Diese ändert sich je nachdem welcher Spieler an der Reihe ist.
        # Es gibt für jeden Spieler 3 eigene listen. Das Dreizehnerpäckchen, das Normale Packchen und der Haufen.

        # Das Dreizehnerpäckchen ist die Liste der Karten die der Spieler zu beginn des Spiels bekommt. Es sind 13 Karten die nicht auf den Haufen gelegt werden können.

        # Das Normale Packchen ist die Liste der Karten die der Spieler im laufe des Spiels bekommt. Diese Karten können auf den Haufen gelegt werden wenn man nicht mehr kann oder seinen Zug benden möchte.

        # Der Haufen ist ein Päckchen welches alte karten beinhaltet. Die jeweils oberste Karte kann auf die Äußeren felder gelegt werden. Wenn das Packchen leer wird es aufgefüllt mit den Karten die auf dem haufen liegen.

        # Die Seitenliste ist die Liste der Karten die auf den 8 Plätzen liegen.

        # Die Mittelliste ist die Liste der Karten die in der Mitte liegen. Es sind 8 Felder und die ersten karten die darauf gelegt werden können sind Asse. 2 Pik-, 2 Coeur-, 2 Treff- und 2 Karro Asse.
        # Diese werden von Ass zu Zwei bis König der gleichen Karten Art zusammengelegt.

        # Die Gegnerliste hängt von dem Spieler ab welcher am Zug ist. Für Spieler 1 ist die Gegnerliste der Haufen des Spieler 2.
        # Auf diese liste können karten abgelegt werden die von der gleicher Art sind aber von wert sich um 1 hoch oder runter unterscheiden. z.B. auf eine Herz 7 kann eine Herz 6 oder 8 gelegt werden.

        # Zusatz aktionen sind P, K, und R
        # P ist das benden des zuges. K ist das Rufen des Krips und R ist das Umlegen des Haufens wenn das Normale Päckchen leer ist.

        # Das Krips ist eine Aktion die der Gegenspieler ausführen kann währen der Spieler am zug ist. Diese Symbolisiert das der Spieler ein fehler gemacht hat.
        # Die Grundsatzt ist: Immer wenn man etwas in die Mitte legen kann muss man es machen!
        # Wenn man gegen diesen grundsatz verstößt und der gegegner es bemerkt ist er drann.

        match (action.origin_type, action.destination_type):
                case (OriginType.PLAYER,DestinationType.PLAYER):
                    self.play_player_on_player(action)
                case (OriginType.PLAYER,DestinationType.OPPONENT):
                    self.play_player_on_opponent(action)
                case (OriginType.PLAYER,DestinationType.TABLEAU):
                    self.play_player_on_tableau(action)
                case (OriginType.PLAYER,DestinationType.FOUNDATION):
                    self.player_on_foundation(action)
                case (OriginType.TABLEAU,DestinationType.TABLEAU):
                    self.play_tableau_on_tableau(action)
                case (OriginType.TABLEAU,DestinationType.FOUNDATION):
                    self.play_tableau_on_foundation(action)
                case (OriginType.TABLEAU,DestinationType.OPPONENT):
                    self.play_tableau_on_opponent(action)

        self.would_be_krips = self.rules.could_be_krips()
        self.count_stalemate()
        self.stalemate()
    def transfer_card(self, source: list[Card], destination: list[Card], face_up: bool = False) -> None:
        if not source:
            return
        card: Card = source.pop()
        if face_up:
            card.is_face_up = True
        destination.append(card)

    def play_player_on_player(self, action: Move) -> None:

        player: Player = self.current_player
        if action.origin_value == 0 and action.destination_value == 0:
            if player.player_stock:
                player.player_stock[-1].is_face_up = True
            elif player.player_waste:
                self.reset_waste(player)
        elif action.origin_value == 2 and action.destination_value == 2:
            if player.player_reserve:
                player.player_reserve[-1].is_face_up = True
        elif action.origin_value == 0 and action.destination_value == 1:
            if player.player_stock and player.player_stock[-1].is_face_up:
                player.player_waste.append(player.player_stock.pop())
            self.current_player = player.opponent
        #elif action.origin_value == 1 and action.destination_value == 0:
         #   self.reset_waste(player)

    def reset_waste(self, player: Player) -> None:
        for card in reversed(player.player_waste):
            card.is_face_up = False
            player.player_stock.append(card)
        player.player_waste.clear()

    def play_player_on_tableau(self, action: Move) -> None:
        self.transfer_card(self.current_player.player_piles[action.origin_value],
                        self.board.tableau[action.destination_value], face_up=True)

    def player_on_foundation(self, action: Move) -> None:
        self.transfer_card(self.current_player.player_piles[action.origin_value],
                        self.board.foundations[action.destination_value])

    def play_player_on_opponent(self, action: Move) -> None:
        self.transfer_card(self.current_player.player_piles[action.origin_value],
                        self.current_player.opponent.player_waste)

    def play_tableau_on_foundation(self, action: Move) -> None:
        self.transfer_card(self.board.tableau[action.origin_value],
                        self.board.foundations[action.destination_value])

    def play_tableau_on_opponent(self, action: Move) -> None:
        self.transfer_card(self.board.tableau[action.origin_value],
                        self.current_player.opponent.player_waste)

    def play_tableau_on_tableau(self, action: Move) -> None:
        self.transfer_card(self.board.tableau[action.origin_value],
                        self.board.tableau[action.destination_value], face_up=True)

    def count_stalemate(self) -> None:
        current_len: list[int] = [
            len(self.player1.player_reserve),
            len(self.player2.player_reserve),
        ]
        if current_len[0]==0 and current_len[1]==0:
            self.stalemate_counter =0
            return None
        if current_len == self.last_player_pile_lengths:
            self.stalemate_counter += 1
        else:
            self.stalemate_counter = 0
        self.last_player_pile_lengths = current_len
    def stalemate(self):
        if self.stalemate_counter >=30:
            if not self.current_player.player_reserve and self.current_player.opponent.player_reserve:
                self.current_player.won = True
            elif self.current_player.player_reserve and not self.current_player.opponent.player_reserve:
                self.current_player.opponent.won = True