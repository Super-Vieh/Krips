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
        self.winner: int = 0 #
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
            self.player1.has_turn = True
            self.current_player = self.player1
            #Hier wird die möglichkeit auf das erste Krips geschaffen.
            self.would_be_krips = self.rules.could_be_krips()
        elif (drz1.card_rank.value < drz2.card_rank.value) or (drz2.card_rank.value == 1 and drz1.card_rank.value != 1):  # stimmt wenn player2 die höhere karte hat
            self.player2.has_turn = True
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
                    print("Schleife engaged player1 ist drann?", self.player1.has_turn)
                    self.current_player= self.player1
                    return None
                elif (self.board.tableau[index][-1].card_rank.value < self.board.tableau[index + 4][-1].card_rank.value):
                    print("Schleife engaged player2 ist drann?", self.player2.has_turn)
                    self.current_player = self.player2
                    return None
        return None

    def execute_move(self, action: Move) -> None:
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

        match (action.origin_type, action.destination_value):
                case (OriginType.PLAYER,DestinationType.PLAYER):
                    return None
                case (OriginType.PLAYER,DestinationType.OPPONENT):
                    return None
                case (OriginType.PLAYER,DestinationType.TABLEAU):
                    return None
                case (OriginType.PLAYER,DestinationType.FOUNDATION):
                    return None
                case (OriginType.TABLEAU,DestinationType.FOUNDATION):
                    return None
                case (OriginType.TABLEAU,DestinationType.OPPONENT):
                    return None