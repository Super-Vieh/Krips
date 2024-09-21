
from .karten import Karten

class Spieler:
    def __init__(self,spielernummer:int, owndeck: list[Karten],game:'Spiel'):
        self.game = game
    def __init__(self,spielernummer:int, owndeck: list[Karten]):
        self.game:'Spiel' = None
        self.spielernummer=spielernummer
        self.owndeck = owndeck
        self.gegenspieler: 'Spieler' = None
        self.anderreihe = False



    def set_gegenspieler(self, gegenspieler: 'Spieler'):
        from .spiel import Spiel
        self.gegenspieler = gegenspieler


    def set_spiel(self, game: 'Spiel'):
        from .spiel import Spiel
        self.game = game


    def ersteAktion(self) -> None:
        drz1 = self.game.spieler1Dreizehner
        drz2 = self.game.spieler2Dreizehner
        if (len(self.owndeck) != 52):
            raise ValueError("Deck has less than 52 cards")
        for i in range(13):
            if self.spielernummer == 1: drz1.append(self.owndeck.pop())
            if self.spielernummer == 2: drz2.append(self.owndeck.pop())

        for i in range(5):  # Die ersten 4 karten werde rausgelegt range(5) weil 0-4
            if i == 0: continue  # Index null wird ignoriert
            if self.spielernummer == 1:  # Beim ersten Spieler werden die ersten 4 und beim zweiten 4-8 plätze belegt
                self.seiteHinlegen(self.owndeck[0], i)
                self.owndeck.remove(self.owndeck[0])
            elif self.spielernummer == 2:
                self.seiteHinlegen(self.owndeck[0], i + 4)
                self.owndeck.remove(self.owndeck[0])

        if self.spielernummer == 1:
           drz1[len(drz1) - 1].karteOffen = True  # erste Dreizehnerkarte wird aufgedeckt
           self.game.spieler1Paechen = self.owndeck #generiert das normale paeckchen
        if self.spielernummer == 2:
           drz2[len(drz2) - 1].karteOffen = True
           self.game.spieler2Paechen = self.owndeck

    #def istAmZug(self): #Wird geloopt solange anderreihe == True
        #if self.anderreihe ==True: self.istAmZug()



    def karte_aufdecken(self,packchen:int=0):
        drz1= self.game.spieler1Dreizehner
        drz2= self.game.spieler2Dreizehner
        spp1=self.game.spieler1Paechen
        spp2=self.game.spieler2Paechen
        if   packchen == 1:
            if   self.spielernummer == 1 : drz1[len(drz1) - 1].karteOffen = True # erste karte des Dreizehner wird geöffnet.
            elif self.spielernummer == 2 : drz2[len(drz2) - 1].karteOffen = True
        elif packchen == 0:
            if   self.spielernummer == 1: spp1[len(spp1) - 1].karteOffen = True
            elif self.spielernummer == 2: spp2[len(spp2) - 1].karteOffen = True


    def mitteHinlegen(self,karte:Karten,stelle:int)->None:

        midliste = self.game.platzliste[stelle-1]
        if (self.kannMitteHinlegen(karte, stelle)):
            midliste.append(karte)
        else:
            return None

    def kannMitteHinlegen(self,karte:Karten,stelle:int)->bool: # Es wird überprüft ob das hinlegen der karte erlaubt , wichtig, in der Mitte
        midliste = self.game.platzliste[stelle-1]
        if (len(midliste) == karte.kartenwert.value-1 and midliste[len(midliste)].kartentyp == karte.kartentyp):
            return True
        else:
            return False
    def kannSeiteHinlegen(self,karte:Karten,stelle:int)->bool:
        aktliste= self.game.platzliste[stelle-1]
        if (len(aktliste) == 0):
            return True
        if (aktliste[len(aktliste)-1].kartenwert.value == karte.kartenwert.value + 1
                and aktliste[len(aktliste)-1].farbe != karte.farbe):
            return True
        else:
            return False


    def seiteHinlegen(self,karte:Karten,stelle:int)->None:

        aktliste:list[Karten] = self.game.platzliste[stelle-1]
        if (self.kannSeiteHinlegen(karte, stelle)):
            aktliste.append(karte)
        else:
            return None

