
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
        self.has_turn: bool = False
        self.player_stock: list[Card] = []
        self.player_waste: list[Card] = []
        self.player_reserve: list[Card] = []
        self.player_piles = [self.player_stock, self.player_waste, self.player_reserve]



    def set_opponent(self, opponent: 'Player') -> None:
        #initialisierungs funktion
        from .game import Game
        self.opponent = opponent


    def set_game(self, game: 'Game') -> None:
        # initialisierungs funktion wegen circular imports
        from .game import Game
        self.game = game


    def first_action(self) -> None:

        if len(self.own_deck) != 52:
            raise ValueError("Deck has less than 52 cards")
        # Erstellung des Dreizehner Päckchens
        for _ in range(13):
            self.player_reserve.append(self.own_deck.pop())

        #Hinlegen der ersten 4 Karten aus dem Normalen Päckchen auf die Seitenstreifen
        start = 1 if self.player_number == 1 else 5
        for i in range(start, start + 4):
            self.play_to_tableau(i, self.own_deck)

        self.player_reserve[-1].is_face_up = True
        self.player_stock = self.own_deck







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
        if origin and origin[-1].value.value==1:
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


    def can_play_on_foundation(self,card:Card,slot:int)->bool: # Es wird überprüft ob das hinlegen der karte erlaubt , wichtig, in der Mitte
        foundations: list[Card] = self.game.foundations[slot-1]
        #Es wird die liste ausgesucht aus den listen also slot 1 ist [0]
        # Es wird jetzt von 1-8 nummeriert
        if foundations and (len(foundations) == card.value.value - 1 and foundations[len(foundations) - 1].card_type == card.card_type):
            return True
        else:
            return False



    def can_play_on_tableau(self, card: Card, slot: int) -> bool:
        tableau: list[Card] = self.game.board.tableau[slot-1]
        if (tableau[-1].value.value == card.value.value + 1 and tableau[-1].farbe != card.farbe):
            return True
        return False


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


    def can_play_on_opponent(self, card: Card) -> bool:
        #kontroliert ob die karte um eins höher oder kleiner ist als die karte auf dem gegner stock und ob die von der gleicher art ist
        if self.player_number == 1:
            p2waste: list[Card] = self.game.player2_waste
            if not p2waste: return False
            elif (card.card_type == p2waste[-1].card_type)and((card.value.value == p2waste[-1].value.value + 1) or (card.value.value == p2waste[-1].value.value - 1)):
                #Es wird zuerst kontroliert ob die Art der Karte die gleiche ist wie die letzte Karte der Liste.
                #Danach wird überprüft ob die karte im karten wert sich um 1 hoch oder runter, unterscheiden. Also wie 7 und 9 sich zu 8 verhalten
                return True
        if self.player_number == 2:
            p1waste: list[Card] =self.game.player1_waste
            if not p1waste: return False
            elif (card.card_type == p1waste[-1].card_type)and((card.value.value == p1waste[-1].value.value + 1) or (card.value.value == p1waste[-1].value.value - 1)) :
                #Es passiert genau das gleiche wie vorher
                return True


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
            self.has_turn= False
            self.opponent.has_turn = True
            self.game.current_player = self.game.player2
        if self.player_number ==2 and self.game.player2_stock and self.game.player2_stock[-1].is_face_up == True:
            self.game.player2_waste.append(self.game.player2_stock.pop())
            self.has_turn= False
            self.opponent.has_turn= True
            self.game.current_player = self.game.player1
    def end_turn_due_to_krips(self) -> None:
        if self.player_number == 1:
            if self.game.player1_stock[-1].is_face_up == True: self.end_turn()
            else:
                self.has_turn= False
                self.opponent.has_turn=True
                self.game.current_player = self.game.player2
            self.game.would_be_krips = False
        if self.player_number == 2:
            if self.game.player2_stock[-1].is_face_up == True: self.end_turn()
            else:
                self.has_turn= False
                self.opponent.has_turn=True
                self.game.current_player = self.game.player1
            self.game.would_be_krips = False