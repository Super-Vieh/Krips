
from .card import Card
#In der Klasse Player sind alle Funktionen vorhanden welche auf das Spielgeschehen auswirkungen haben.
#Imgrunde ist die Klasse das Werkzeug welches von anhand der Regeln der Klasse Game genutzt wird.
#Die namen der einzelnen Funktionen Beschreiben den Nutzen ziemlich gut.
class Player:
    def __init__(self,player_number:int, own_deck: list[Card]):
        self.game:'Game' = None
        self.player_number=player_number
        self.own_deck = own_deck
        self.opponent: 'Player' = None
        self.has_turn = False



    def set_opponent(self, opponent: 'Player'):
        #initialisierungs funktion
        from .game import Game
        self.opponent = opponent


    def set_game(self, game: 'Game'):
        # initialisierungs funktion wegen circular imports
        from .game import Game
        self.game = game


    def first_action(self) -> None:

        if len(self.own_deck) != 52:
            raise ValueError("Deck has less than 52 cards")
        # Erstellung des Dreizehner Päckchens
        for i in range(13):
            if self.player_number == 1:
                self.game.player1_reserve.append(self.own_deck.pop())
            if self.player_number == 2:
                self.game.player2_reserve.append(self.own_deck.pop())

        #Hinlegen der ersten 4 Karten aus dem Normalen Päckchen auf die Seitenstreifen
        for i in range(1,5):
            if self.player_number == 1:
                self.play_to_tableau(i, self.own_deck)
                #self.own_deck.pop()
            elif self.player_number == 2:
                self.play_to_tableau(i + 4, self.own_deck)
                #self.own_deck.pop()

        if self.player_number == 1:
            self.game.player1_reserve[-1].is_face_up = True
            self.game.player1_stock = self.own_deck
        if self.player_number == 2:
            self.game.player2_reserve[-1].is_face_up = True
            self.game.player2_stock = self.own_deck





    def flip_card(self,stock:int=0):
        reserve1= self.game.player1_reserve
        reserve2= self.game.player2_reserve
        stock1= self.game.player1_stock
        stock2= self.game.player2_stock
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

    def play_to_foundation(self,slot:int,origin:list[Card]):
        foundations = self.game.foundations[slot-1]#Es wird die liste ausgesucht aus den listen also slot 1 ist [0]
        #Nur wenn das Ass gelegt wird
        if origin and origin[-1].rank.value==1:
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
        foundations = self.game.foundations[slot-1]
        #Es wird die liste ausgesucht aus den listen also slot 1 ist [0]
        # Es wird jetzt von 1-8 nummeriert
        if foundations and (len(foundations) == card.rank.value-1 and foundations[len(foundations)-1].card_type == card.card_type):
            return True
        else:
            return False



    def can_play_on_tableau(self, card: Card, slot: int) -> bool:
        tableau = self.game.tableau[slot-1]
        if (tableau[-1].rank.value == card.rank.value + 1 and tableau[-1].farbe != card.farbe):
            return True
        return False


    def play_to_tableau(self,slot:int,origin:list[Card])->None:
        tableau:list[Card] = self.game.tableau[slot-1]
        if origin and len(tableau) == 0:
            tempcard= origin.pop()
            tempcard.is_face_up = True
            tableau.append(tempcard)
            return None
        if origin and (self.can_play_on_tableau(origin[-1], slot)):
            tempcard= origin.pop()
            tempcard.is_face_up = True
            tableau.append(tempcard)
            return None


    def can_play_on_opponent(self, card: Card) -> bool:
        #kontroliert ob die karte um eins höher oder kleiner ist als die karte auf dem gegner stock und ob die von der gleicher art ist
        if self.player_number == 1:
            p2waste = self.game.player2_waste
            if not p2waste: return False
            elif (card.card_type == p2waste[-1].card_type)and((card.rank.value == p2waste[-1].rank.value + 1) or (card.rank.value == p2waste[-1].rank.value -1)):
                #Es wird zuerst kontroliert ob die Art der Karte die gleiche ist wie die letzte Karte der Liste.
                #Danach wird überprüft ob die karte im karten wert sich um 1 hoch oder runter, unterscheiden. Also wie 7 und 9 sich zu 8 verhalten
                return True
        if self.player_number == 2:
            p1waste =self.game.player1_waste
            if not p1waste: return False
            elif (card.card_type == p1waste[-1].card_type)and((card.rank.value == p1waste[-1].rank.value + 1) or (card.rank.value == p1waste[-1].rank.value -1)) :
                #Es passiert genau das gleiche wie vorher
                return True


    def play_to_opponent(self,origin:list[Card])->None:
        if self.player_number == 1:
            if origin and self.can_play_on_opponent(origin[-1]):
                self.game.player2_waste.append(origin.pop())
        if self.player_number == 2:
            if origin and self.can_play_on_opponent(origin[-1]):
                self.game.player1_waste.append(origin.pop())
    def reset_waste(self):
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
    def end_turn(self):
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
    def end_turn_due_to_krips(self):
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
    def is_krips(self )-> bool:
        # Kontroliert ob ein Krips gelegt werden kann. Die funktion wird in play() aufgerufen
        if self.player_number == 1:
            ownlists=[self.game.player1_stock,self.game.player1_waste,self.game.player1_reserve]
            validlists =[liste for liste in (self.game.tableau + ownlists) if liste] # Alle listen die nicht leer sind werden in die validlists geschrieben. Nur die listen aus tableau und ownlist werden überprüft
            for slist in validlists:
                if slist[-1].rank.value == 1: #Wenn irgenwo ein Ass liegt
                    return True
                for mliste in self.game.foundations:
                    if slist and mliste:#Check ob die listen leer sind
                        if slist[-1].card_type.value == mliste[-1].card_type.value and slist[-1].rank.value -1 == mliste[-1].rank.value:
                            #Hier wird überprüft ob eine karte die gleiche art ist und 1 höher ist als die andren. Wenn irgentwo ein Pik ass ist liegt und eine Pik 2 überprüft wird die bedingung ausgelöst
                            return True

        if self.player_number == 2:
            ownlists=[self.game.player2_stock,self.game.player2_waste,self.game.player2_reserve]
            validlists=[liste for liste in (self.game.tableau + ownlists) if len(liste) > 0]
            for slist in validlists:
                if slist[-1].rank.value == 1: #Wenn irgenwo ein Ass leigt
                    return True
                for mliste in self.game.foundations:
                    if slist and mliste:
                        if slist[-1].card_type.value == mliste[-1].card_type.value and slist[-1].rank.value -1 == mliste[-1].rank.value:
                            return True
        return False
    def krips_card_played(self, list_of_last_card:list[Card]):
        # ist eine Funktion welche kontroliert, ob die gelegte karte nicht das Krips bedient und wenn es das tut wird would_be_krips auf false gesetzt
        # wird in der play() funktion genutzt um Krips zu kontrolieren. Nur in dem Fall das eine Karte in die mitte gelegt wird, wird die funktiomn aufgerufen.
        if self.game.would_be_krips == False or not list_of_last_card:
            return None
        for kripslist in self.game.foundations or not list_of_last_card:
            #die übergebene list_of_last card gibt die zuletzt gelegte karte wieder
            if kripslist and list_of_last_card[-1].card_type == kripslist[-1].card_type and list_of_last_card[-1].rank.value -1 == kripslist[-1].rank.value:
                self.game.would_be_krips = False
