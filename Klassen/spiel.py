from .karten import Karten,KartenTyp,KartenWert
from .spieler import Spieler

class Spiel:


    spieler1:Spieler
    spieler2:Spieler
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


    def game_first_move(self):
        objdrz1 = self.spieler1Dreizehner[len(self.spieler1Dreizehner)-1] #erstezt das lezte objekt des ersten Dreizehnerpaeckchen
        objdrz2 = self.spieler2Dreizehner[len(self.spieler2Dreizehner)-1] #erstezt das lezte objekt des zweiten Dreizehnerpaeckchen

        if(objdrz1.karteOffen ==True and self.spieler2Dreizehner[len(self.spieler2Dreizehner)-1].karteOffen== True): #Wenn die längen gleich sind
            if  (objdrz1.kartenwert.value > objdrz2.kartenwert.value):# stimmt wenn spieler1 die höhere karte hat
                self.spieler1.anderreihe = True
            elif(objdrz1.kartenwert.value < objdrz2.kartenwert.value):# stimmt wenn spieler2 die höhere karte hat
                self.spieler2.anderreihe = True
            else:


                for karte in range(4):  #geht durch die ersten 4 plätze auf jeder seite durch und vergleich sie

                    if  (self.platzliste[karte][0].kartenwert.value > self.platzliste[karte+4][0].kartenwert.value):
                        self.spieler1.anderreihe = True
                        print("Schleife engaged Spieler1 ist drann?",self.spieler1.anderreihe)
                        return None
                    elif(self.platzliste[karte][0].kartenwert.value < self.platzliste[karte+4][0].kartenwert.value):
                        self.spieler2.anderreihe = True
                        print("Schleife engaged Spieler2 ist drann?", self.spieler2.anderreihe)
                        return None





    #
    # def mitteHinlegen(self,karte:Karten,stelle:int)->None:
    #
    #     midliste = self.platzliste[stelle-1]
    #     if (self.kannMitteHinlegen(karte, stelle)):
    #         midliste.append(karte)
    #     else:
    #         return None
    #
    #
    #
    #
    # def kannMitteHinlegen(self,karte:Karten,stelle:int)->bool: # Es wird überprüft ob das hinlegen der karte erlaubt , wichtig, in der Mitte
    #     midliste = self.platzliste[stelle-1]
    #     if (len(midliste) == karte.kartenwert.value-1 and midliste[len(midliste)].kartentyp == karte.kartentyp):
    #         return True
    #     else:
    #         return False
    #
    #
    #
    #
    #
    #
    #
    # def kannSeiteHinlegen(self,karte:Karten,stelle:int)->bool:
    #     aktliste= self.platzliste[stelle-1]
    #     if (len(aktliste) == 0):
    #         return True
    #     if (aktliste[len(aktliste)-1].kartenwert.value == karte.kartenwert.value + 1
    #             and aktliste[len(aktliste)-1].farbe != karte.farbe):
    #         return True
    #     else:
    #         return False
    #
    #
    # def seiteHinlegen(self,karte:Karten,stelle:int)->None:
    #
    #     aktliste:list[Karten] = self.platzliste[stelle-1]
    #     if (self.kannSeiteHinlegen(karte, stelle)):
    #         aktliste.append(karte)
    #     else:
    #         return None

