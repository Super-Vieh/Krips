
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
        self.opponent = opponent
    def set_won(self,won):
        self.won=won

    def distribute_cards_to_decks(self) -> None:

        if len(self.own_deck) != 52:
            raise ValueError("Deck has less than 52 cards")
        # Erstellung des Dreizehner Päckchens
        for _ in range(13):
            self.receive_card(self.own_deck.pop(), 2)

        self.flip_last_card(2)
        for card in self.own_deck:
            self.receive_card(card, 0)


    def flip_last_card(self, list:int) -> None:
        self.player_piles[list][-1].is_face_up = True
    def reset_waste(self):
        if not self.player_stock and self.player_waste:
            while self.player_waste:
                card = self.extract_card(1)
                card.is_face_up=False
                self.receive_card(card, 0)
    def receive_card(self,card:Card,list:int):
        self.player_piles[list].append(card)



    def extract_card(self,list:int)->Card:
        if not self.player_piles[list]:
            raise ValueError("von Leerer Liste sollte entfernt werden")
        return self.player_piles[list].pop()
