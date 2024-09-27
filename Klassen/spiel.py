from .karten import Karten,KartenTyp,KartenWert
from .spieler import Spieler

class Spiel:

    current:Spieler=None
    gameon = True

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
    spieler1listen = [spieler1Paechen,spieler1Haufen,spieler1Dreizehner]

    spieler2Haufen:     list[Karten] = []
    spieler2Paechen:    list[Karten] = []
    spieler2Dreizehner: list[Karten] = []
    spieler2listen = [spieler2Paechen,spieler2Haufen,spieler2Dreizehner]

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
    def play(self):
            # karte kann von  den 3 spieler päckchen und 8 Seitenstreifen gelegt werden.
            # karte kann auf die 8 Mittlerenpäckchen, die 8 Seitenstreifen und den gegner Haufen gelegt werden.
            action:str = input(f"\nSpieler{self.current.spielernummer} ist drann."
                               "\nWas soll gemacht werden?\n"
                       "Karte aufdecken = A0 oder A1\n" # Aufgedeckt werden können nur Päckchen und Dreizehner 
                       "Karte hilegen = (A0-2,S0-7,)M0-7*S0-7*G0\n"
                       "Runde Aufhören= P\n")
            lenaction = len(action)

            if lenaction == 1 and action == "P": self.current.aufhören()
            if lenaction == 2 and action == "A0": self.current.karte_aufdecken(0) ;return None
            elif lenaction == 2 and action == "A1": self.current.karte_aufdecken(1); return None
            first= action[0]#Herkunftslistentyp
            second= int(action[1])#herkuftsliste
            third= action[2]#Ziellistentyp
            fourth= int(action[3])#zielliste
            match (first, third):# M = Mitte, S = Seite, G = Gegner, A=Haupt
                case ("A", "M"):
                    if self.current.spielernummer == 1:
                        self.current.mitteHinlegen(fourth,self.spieler1listen[second])
                        #fourth ist ein int welcher den index der zielliste anzeigt an dem die karte hingelegt werden muss.
                        #spieler1listen ist eine liste mit den listen der spieler welcher als origin verändert wird.
                    if self.current.spielernummer == 2:
                        self.current.mitteHinlegen(fourth,self.spieler2listen[second])
                case ("A", "S"):
                    if self.current.spielernummer == 1:
                        self.current.seiteHinlegen(fourth,self.spieler1listen[second])
                    if self.current.spielernummer == 2:
                        self.current.seiteHinlegen(fourth,self.spieler2listen[second])
                case ("A", "G"):
                    if self.current.spielernummer == 1:
                        self.current.gegener_geben(self.spieler1listen[second])
                    if self.current.spielernummer == 2:
                        self.current.gegener_geben(self.spieler2listen[second])
                case ("S", "M"):
                    if self.current.spielernummer == 1:
                        self.current.mitteHinlegen(fourth,self.platzliste[second])
                    if self.current.spielernummer == 2:
                        self.current.mitteHinlegen(fourth,self.platzliste[second])
                case ("S", "S"):
                    if self.current.spielernummer == 1:
                        self.current.seiteHinlegen(fourth,self.platzliste[second])
                    if self.current.spielernummer == 2:
                        self.current.seiteHinlegen(fourth,self.platzliste[second])
                case ("S", "G"):
                    if self.current.spielernummer == 1:
                        self.current.gegener_geben(self.platzliste[second])
                    if self.current.spielernummer == 2:
                        self.current.gegener_geben(self.platzliste[second])
                case _:
                    print("Ungültige Aktion.")





