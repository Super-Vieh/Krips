
from .card import Card
#In der Klasse Player sind alle Funktionen vorhanden welche auf das Spielgeschehen auswirkungen haben.
#Imgrunde ist die Klasse das Werkzeug welches von anhand der Regeln der Klasse Game genutzt wird.
#Die namen der einzelnen Funktionen Beschreiben den Nutzen ziemlich gut.
class Player:
    def __init__(self,player_number:int, own_deck: list[Card]) -> None:
        self.game:'Game' = None
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


    def set_game(self, game: 'Game') -> None:
        # initialisierungs funktion wegen circular imports
        from .game import Game
        self.game = game


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






    def flip_card(self,stock:int=0) -> None:
        reserve1: list[Card] = self.game.player1_reserve
        reserve2: list[Card] = self.game.player2_reserve
        stock1: list[Card] = self.game.player1_stock
        stock2: list[Card] = self.game.player2_stock
        if   stock == 1:
            #Päckchen 1 ist das Dreizehner Päckchen
            if   self.player_number == 1 and reserve1:
                reserve1[-1].is_face_up = True
            elif self.player_number == 2 and reserve2:
                reserve2[-1].is_face_up = True
            else:return None
        elif stock == 0:
            #Päckchen 0 ist das Normale Päckchen
            if   self.player_number == 1 and stock1: stock1[-1].is_face_up = True
            elif self.player_number == 2 and stock2: stock2[-1].is_face_up = True
            else:return None

    def play_to_foundation(self,slot:int,origin:list[Card]) -> None:
        foundations: list[Card] = self.game.foundations[slot-1]#Es wird die liste ausgesucht aus den listen also slot 1 ist [0]
        #Nur wenn das Ass gelegt wird
        if origin and origin[-1].card_rank.value==1:
            #Wenn als erste Karte das Ass gelegt wird muss sichergegangen werden dass, das Ass zum Feld passt
            #Und es wird überprüftt das das ass nicht 2 mal auf das gleiche feld gelegt werden kann
            if slot in [1,2] and origin[-1].card_type.value == "Pik" and len(foundations) == 0:
                foundations.append(origin.pop())
            elif slot in [3,4] and origin[-1].card_type.value == "Coeur" and len(foundations) == 0:
                foundations.append(origin.pop())
            elif slot in [5,6] and origin[-1].card_type.value == "Treff" and len(foundations) == 0:
                foundations.append(origin.pop())
            elif slot in [7,8] and origin[-1].card_type.value == "Karro" and len(foundations) == 0:
                foundations.append(origin.pop())
        #Normale bedingung
        elif origin and self.can_play_on_foundation(origin[len(origin)-1], slot):
            foundations.append(origin.pop())


    def play_to_tableau(self,slot:int,origin:list[Card])->None:
        tableau:list[Card] = self.game.board.tableau[slot-1]
        if origin and len(tableau) == 0:
            tempcard: Card = origin.pop()
            tempcard.is_face_up = True
            tableau.append(tempcard)
            return None
        if origin and (self.can_play_on_tableau(origin[-1], slot)):
            tempcard: Card = origin.pop()
            tempcard.is_face_up = True
            tableau.append(tempcard)
            return None


    def play_to_opponent(self,origin:list[Card])->None:
        if self.player_number == 1:
            if origin and self.can_play_on_opponent(origin[-1]):
                self.game.player2_waste.append(origin.pop())
        if self.player_number == 2:
            if origin and self.can_play_on_opponent(origin[-1]):
                self.game.player1_waste.append(origin.pop())
    def reset_waste(self) -> None:
       if self.player_number == 1:
            for i in self.game.player1_waste:
                i.is_face_up = False
            for card in reversed(self.game.player1_waste):
                self.game.player1_stock.append(card)
            self.game.player1_waste = []
            for i in self.game.player1_waste:
                print(i.is_face_up)
       if self.player_number == 2:
            for i in self.game.player2_waste:
                i.is_face_up = False
            for card in reversed(self.game.player2_waste):
                self.game.player2_stock.append(card)
            self.game.player2_waste = []
            for i in self.game.player2_waste:
                print(i.is_face_up)
    def end_turn(self) -> None:
        if self.player_number ==1 and self.game.player1_stock and self.game.player1_stock[-1].is_face_up == True:
            self.game.player1_waste.append(self.game.player1_stock.pop())
            self.game.current_player = self.game.player2
        if self.player_number ==2 and self.game.player2_stock and self.game.player2_stock[-1].is_face_up == True:
            self.game.player2_waste.append(self.game.player2_stock.pop())
            self.game.current_player = self.game.player1
    def end_turn_due_to_krips(self) -> None:
        if self.player_number == 1:
            if self.game.player1_stock[-1].is_face_up == True: self.end_turn()
            else:
                self.game.current_player = self.game.player2
            self.game.would_be_krips = False
        if self.player_number == 2:
            if self.game.player2_stock[-1].is_face_up == True: self.end_turn()
            else:
                self.game.current_player = self.game.player1
            self.game.would_be_krips = False