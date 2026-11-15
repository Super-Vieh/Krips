
from .card import Card
#In der Klasse Player sind alle Funktionen vorhanden welche auf das Spielgeschehen auswirkungen haben.
#Imgrunde ist die Klasse das Werkzeug welches von anhand der Regeln der Klasse Game genutzt wird.
#Die namen der einzelnen Funktionen Beschreiben den Nutzen ziemlich gut.
class Player:
    def __init__(self,player_number:int, own_deck: list[Card]) -> None:
        self.player_number: int = player_number
        self.own_deck: list[Card] = own_deck
        self.opponent: 'Player' = None
        self.player_stock: list[Card] = []
        self.player_waste: list[Card] = []
        self.player_reserve: list[Card] = []
        self.player_piles = [self.player_stock, self.player_waste, self.player_reserve]
        self.won : bool = False


    def set_opponent(self, opponent: 'Player') -> None:
        #initialisierungs funktion
        from .game import Game
        self.opponent = opponent

    def distribute_cards_to_decks(self) -> None:

        if len(self.own_deck) != 52:
            raise ValueError("Deck has less than 52 cards")
        # Erstellung des Dreizehner Päckchens
        for _ in range(13):
            self.player_reserve.append(self.own_deck.pop())

        self.player_reserve[-1].is_face_up = True
        for card in self.own_deck:
            self.player_stock.append(card)
        self.own_deck.clear()

    def flip_last_card(self, list:int) -> None:
        self.player_piles[list][-1].is_face_up = True
    def receive_card(self,card:Card,list:int):
        self.player_piles[list].append(card)



    def extract_card(self,list:int)->Card:
        if not self.player_piles[list]:
            raise ValueError("von Leerer Liste sollte entfernt werden")
        return self.player_piles[list].pop()
