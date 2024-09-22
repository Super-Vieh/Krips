
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
            if   self.spielernummer == 1 : drz1[len(drz1) - 1].karteOffen = True # erste Karte des Dreizehner wird geöffnet.
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

    def kannMitteHinlegen(self,karte:Karten,stelle:int)->bool: # Es wird überprüft, ob das Hinlegen der karte erlaubt , wichtig, in der Mitte
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

    def kanngegnergeben(self,karte:Karten)->bool:
        hf1 = self.game.spieler1Haufen
        hf2 = self.game.spieler2Haufen
        if   self.spielernummer == 1 :
            if(karte.kartentyp == hf2[len(hf2)-1].kartentyp) and (karte.kartenwert.value == hf2[len(hf2)-1].kartenwert.value + 1) or  (karte.kartenwert.value == hf2[len(hf2)-1].kartenwert.value -1):
                return True
                # es wird überprüft, ob die karte auf dem Gegener haufen um eins größer oder kleiner ist als die karte die man hinlegen kann

        elif self.spielernummer == 2 :
            if (karte.kartentyp == hf1[len(hf1) - 1].kartentyp) and (karte.kartenwert.value == hf1[len(hf1) - 1].kartenwert.value + 1) or (karte.kartenwert.value == hf1[len(hf1) - 1].kartenwert.value - 1):
                return True
                # es wird überprüft, ob die karte auf dem Gegener haufen um eins größer oder kleiner ist als die karte die man hinlegen kann
        else: return False

    def gegnergeben(self, karte: Karten) -> None:
        hf1 = self.game.spieler1Haufen
        hf2 = self.game.spieler2Haufen
        if self.spielernummer == 1 and self.kanngegnergeben(karte):
                hf2.append(karte)
        elif self.spielernummer == 2 and self.kanngegnergeben(karte):
                hf1.append(karte)



    # Die nächsten drei methoden
    # überprüfen welcher spieler drann ist und ob die liste leer ist
    # Dann wird überprüft, ob es auf den Mitte-, Seiten- oder Gegnerhauften soll
    # Die Stelle wird hoffetlich berücksichtigt
    def haufen_kartehinlegen(self,karte:Karten,stelle:int,ort:str = "Mitte")->None:
        if self.spielernummer == 1:
            if len(self.game.spieler1Haufen)!= 0:
                if   ort == "Mitte" and self.kannMitteHinlegen(karte, stelle):
                    self.mitteHinlegen(karte, stelle)
                    self.game.spieler1Haufen.pop()
                elif ort == "Seite" and self.kannSeiteHinlegen(karte, stelle):
                    self.seiteHinlegen(karte, stelle)
                    self.game.spieler1Haufen.pop()
                elif ort == "Gegner"and self.kanngegnergeben(karte):
                    self.gegnergeben(karte)
                    self.game.spieler1Haufen.pop()
        if self.spielernummer == 2:
            if len(self.game.spieler2Haufen)!= 0:
                if   ort == "Mitte" and self.kannMitteHinlegen(karte, stelle):
                    self.mitteHinlegen(karte, stelle)
                    self.game.spieler2Haufen.pop()
                elif ort == "Seite" and self.kannSeiteHinlegen(karte, stelle):
                    self.seiteHinlegen(karte, stelle)
                    self.game.spieler2Haufen.pop()
                elif ort == "Gegner"and self.kanngegnergeben(karte):
                    self.gegnergeben(karte)
                    self.game.spieler2Haufen.pop()


    def dreizehner_karte_hinlegen(self,karte:Karten,stelle:int,ort:str = "Mitte")->None:
        if self.spielernummer == 1:
            if len(self.game.spieler1Dreizehner) != 0:
                if ort == "Mitte" and self.kannMitteHinlegen(karte, stelle):
                    self.mitteHinlegen(karte, stelle)
                    self.game.spieler1Dreizehner.pop()
                elif ort == "Seite" and self.kannSeiteHinlegen(karte, stelle):
                    self.seiteHinlegen(karte, stelle)
                    self.game.spieler1Dreizehner.pop()
                elif ort == "Gegner" and self.kanngegnergeben(karte):
                    self.gegnergeben(karte)
                    self.game.spieler1Dreizehner.pop()
        elif self.spielernummer == 2:
            if len(self.game.spieler2Dreizehner) != 0:
                if ort == "Mitte" and self.kannMitteHinlegen(karte, stelle):
                    self.mitteHinlegen(karte, stelle)
                    self.game.spieler2Dreizehner.pop()
                elif ort == "Seite" and self.kannSeiteHinlegen(karte, stelle):
                    self.seiteHinlegen(karte, stelle)
                    self.game.spieler2Dreizehner.pop()
                elif ort == "Gegner" and self.kanngegnergeben(karte):
                    self.gegnergeben(karte)
                    self.game.spieler2Dreizehner.pop()

    def paeckchen_karte_hinlegen(self,karte:Karten,stelle:int,ort:str = "Mitte")->None:
        if self.spielernummer == 1:
            if len(self.game.spieler1Paechen)!= 0:
                if   ort == "Mitte" and self.kannMitteHinlegen(karte, stelle):
                    self.mitteHinlegen(karte, stelle)
                    self.game.spieler1Paechen.pop()
                elif ort == "Seite" and self.kannSeiteHinlegen(karte, stelle):
                    self.seiteHinlegen(karte, stelle)
                    self.game.spieler1Paechen.pop()
                elif ort == "Gegner"and self.kanngegnergeben(karte):
                    self.gegnergeben(karte)
                    self.game.spieler1Paechen.pop()
        if self.spielernummer == 2:
            if len(self.game.spieler2Paechen)!= 0:
                if   ort == "Mitte" and self.kannMitteHinlegen(karte, stelle):
                    self.mitteHinlegen(karte, stelle)
                    self.game.spieler2Paechen.pop()
                elif ort == "Seite" and self.kannSeiteHinlegen(karte, stelle):
                    self.seiteHinlegen(karte, stelle)
                    self.game.spieler2Paechen.pop()
                elif ort == "Gegner"and self.kanngegnergeben(karte):
                    self.gegnergeben(karte)
                    self.game.spieler2Paechen.pop()



