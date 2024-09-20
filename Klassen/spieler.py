from alternate import Spieler
from .spiel import Spiel,Karten
class Spieler:
    def __init__(self,spielernummer:int, owndeck: list[Karten],game:Spiel):
        self.game = game
        self.spielernummer=spielernummer
        self.owndeck = owndeck
    anderreihe = False
    dreizehner      :list[Karten] =[]
    eigablage       :list[Karten] =[]
    normalpaekchen  :list[Karten] =[]
    gegenspieler :Spieler
    @property
    def anderreihe(self):
        if self.gegenspieler.anderreihe== True and self.anderreihe == True: raise ValueError("Beider Spieler sind sind an der Reihe")
        if self.gegenspieler.anderreihe == False and self.anderreihe == False: raise ValueError("Beider Spieler sind sind an der Reihe")




    def ersteAktion(self) -> None:

        if(len(self.owndeck)!=52):
            raise ValueError("Deck has less than 52 cards")
        for i in range(13):
            if self.spielernummer == 1: self.game.spieler1Dreizehner.append(self.owndeck.pop())
            if self.spielernummer == 2: self.game.spieler2Dreizehner.append(self.owndeck.pop())


        for i in range(5): # Die ersten 4 karten werde rausgelegt range(5) weil 0-4
            if i == 0: continue#Index null wird ignoriert
            if   self.spielernummer==1:# Beim ersten Spieler werden die ersten 4 und beim zweiten 4-8 plätze belegt
                 self.game.seiteHinlegen(self.owndeck[0],i)
                 self.owndeck.remove(self.owndeck[0])
            elif self.spielernummer==2:
                 self.game.seiteHinlegen(self.owndeck[0],i+4)
                 self.owndeck.remove(self.owndeck[0])

        if self.spielernummer == 1: self.game.spieler1Dreizehner[len(self.game.spieler1Dreizehner) -1].karteOffen  = True  # erste Dreizehnerkarte wird aufgedeckt
        if self.spielernummer == 2: self.game.spieler2Dreizehner[len(self.game.spieler2Dreizehner) -1].karteOffen  = True



    #def istAmZug(self): #Wird geloopt solange anderreihe == True


