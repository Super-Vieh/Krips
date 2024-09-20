import tkinter as tk

from tkinter import ttk
from enum import Enum
import Klassen
import itertools,random
class KartenTyp(Enum):
    Pik   = "Pik "
    Coeur = "Coeur"
    Treff = "Treff"
    Karro = "Karro"

class KartenWert(Enum):
    Ass     = 1
    Zwei    = 2
    Drei    = 3
    Vier    = 4
    Fuenf   = 5
    Sechs   = 6
    Sieben  = 7
    Acht    = 8
    Neun    = 9
    Zehn    = 10
    Bube    = 11
    Dame    = 12
    Koenig  = 13
# class Paeckchen(Enum):
#     pik1   = []
#     pik2   = []
#     coeur1 = []
#     coeur2 = []
#     treff1 = []
#     treff2 = []
#     karro1 = []
#     karro2 = []

class Karten:
    def __init__(self, kartenTyp: KartenTyp, kartenWert: KartenWert):
        self.kartentyp  = kartenTyp
        self.kartenwert = kartenWert

    @property
    def farbe(self) -> str:
        if(self.kartentyp == KartenTyp.Pik or self.kartentyp ==KartenTyp.Treff):
            return "Schwarz"
        else:
            return "Rot"






class Spiel:
    pik1:list[Karten]   =[]
    pik2:list[Karten]   =[]
    coeur1:list[Karten] =[]
    coeur2:list[Karten] =[]
    treff1:list[Karten] =[]
    treff2:list[Karten] =[]
    karro1:list[Karten] =[]
    karro2:list[Karten] =[]
    mittlereliste = [pik1,pik2,coeur1,coeur2,treff1,treff2,karro1,karro2]


    platzliste1:list[Karten]=[]
    platzliste2:list[Karten]=[]
    platzliste3:list[Karten]=[]
    platzliste4:list[Karten]=[]
    platzliste5:list[Karten]=[]
    platzliste6:list[Karten]=[]
    platzliste7:list[Karten]=[]
    platzliste8:list[Karten]=[]
    platzliste = [platzliste1,platzliste2,platzliste3,platzliste4,platzliste5,platzliste6,platzliste7,platzliste8]

    spieler1Haufen:     list[Karten] = []
    spieler1Paechen:    list[Karten] = []
    spieler1Dreizehner: list[Karten] = []

    spieler2Haufen:     list[Karten] = []
    spieler2Paechen:    list[Karten] = []
    spieler2Dreizehner: list[Karten] = []

    def kartenDeckErstellung(self) -> list[Karten]:
        templist=[] # Speichert die Karten
        kartentyp = list(KartenTyp)
        kartenwert= list(KartenWert)

        for i in range(len(kartentyp)):
            for j in range(len(kartenwert)):
                templist.append(Karten(kartentyp[i],kartenwert[j]))
        return templist




    def mitteHinlegen(self,karte:Karten,stelle:int)->None:
        switcher= {
            1: self.pik1,
            2: self.pik2,
            3: self.coeur1,
            4: self.coeur2,
            5: self.treff1,
            6: self.treff2,
            7: self.karro1,
            8: self.karro2
        }
        aktliste = switcher.get(stelle)
        if (self.kannMitteHinlegen(karte, stelle)):
            aktliste.append(karte)
        else:
            return None




    def kannMitteHinlegen(self,karte:Karten,stelle:int)->bool: # Es wird überprüft ob das hinlegen der karte erlaubt , wichtig, in der Mitte
        switcher = {
            1: self.pik1,
            2: self.pik2,
            3: self.coeur1,
            4: self.coeur2,
            5: self.treff1,
            6: self.treff2,
            7: self.karro1,
            8: self.karro2
             }
        listof= switcher.get(stelle)
        if (len(listof) == karte.kartenwert.value-1 and listof[len(listof)-1].kartentyp == karte.kartentyp):
            return True
        else:
            return False


    def seiteHinlegen(self,karte:Karten,stelle:int)->None:
        switcher= {
            1: self.platzliste1,
            2: self.platzliste2,
            3: self.platzliste3,
            4: self.platzliste4,
            5: self.platzliste5,
            6: self.platzliste6,
            7: self.platzliste7,
            8: self.platzliste8
        }
        aktliste = switcher.get(stelle)
        if (self.kannSeiteHinlegen(karte, stelle)):
            aktliste.append(karte)
        else:
            return None

    def kannSeiteHinlegen(self,karte:Karten,stelle:int)->bool:
        switcher = {
                 1: self.platzliste1,
                 2: self.platzliste2,
                 3: self.platzliste3,
                 4: self.platzliste4,
                 5: self.platzliste5,
                 6: self.platzliste6,
                 7: self.platzliste7,
                 8: self.platzliste8
             }
        listof= switcher.get(stelle)
        if (listof[len(listof) - 1].kartenwert.value == karte.kartenwert.value + 1 and listof[len(listof)-1].farbe != karte.farbe):
            return True
        else:
            return False

class Spieler:
    def __init__(self,spielernummer:int, owndeck: list[Karten],game:Spiel):
        self.anderreihe = False
        self.spielernummer=spielernummer
        self.owndeck = owndeck
        self.game = game

    dreizehner      :list[Karten] =[]
    eigablage       :list[Karten] =[]
    normalpaekchen  :list[Karten] =[]
    def ersteAktion(self) -> None:
        if(len(self.owndeck)!=52):
            raise ValueError("Deck has less than 52 cards")
        for i in range(13):
            self.dreizehner.append(self.owndeck[len(self.owndeck)-1])
            self.owndeck.remove(self.owndeck[len(self.owndeck)-1])
        for i in range(4):
            if self.spielernummer==1:
                self.game.seiteHinlegen(self.owndeck[0],i)
                self.owndeck.remove(self.owndeck[0])
            elif self.spielernummer==2:
                self.game.seiteHinlegen(self.eigablage[0],i+4)
                self.owndeck.remove(self.owndeck[0])











# def main():
#
#     game1 = Spiel()
#     newdeck1 = game1.kartenDeckErstellung()
#     newdeck2 = game1.kartenDeckErstellung()
#     random.shuffle(newdeck1)
#     random.shuffle(newdeck2)
#
#
#
#
#
#     # card2 = Karten(KartenTyp.Karro,KartenWert.Koenig)
#     # card3 = Karten(KartenTyp.Treff,KartenWert.Dame)
#     # game1.platzliste1.append(card2)
#     # print(game1.seiteHinlegen(card3,1))
#     # print(game1.kannSeiteHinlegen(card3,1))
#     # print(game1.platzliste1)
#
#
#
#
# if __name__ == "__main__":
#     main()
