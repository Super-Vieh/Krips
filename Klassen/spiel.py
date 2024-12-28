from .karten import Karten, KartenTyp, KartenWert
from .spieler import Spieler


class Spiel:
    current: Spieler = None
    gameon = True
    wouldbeKrips=False

    spieler1: Spieler
    spieler2: Spieler
    pik1: list[Karten] = []
    pik2: list[Karten] = []
    coeur1: list[Karten] = []
    coeur2: list[Karten] = []
    treff1: list[Karten] = []
    treff2: list[Karten] = []
    karro1: list[Karten] = []
    karro2: list[Karten] = []
    mittlereliste = [pik1, pik2, coeur1, coeur2, treff1, treff2, karro1, karro2]

    platzliste1: list[Karten] = []
    platzliste2: list[Karten] = []
    platzliste3: list[Karten] = []
    platzliste4: list[Karten] = []
    platzliste5: list[Karten] = []
    platzliste6: list[Karten] = []
    platzliste7: list[Karten] = []
    platzliste8: list[Karten] = []
    platzliste = [platzliste1, platzliste2, platzliste3, platzliste4, platzliste5, platzliste6, platzliste7,
                  platzliste8]

    spieler1Haufen: list[Karten] = []
    spieler1Paechen: list[Karten] = []
    spieler1Dreizehner: list[Karten] = []
    spieler1listen = []

    spieler2Haufen: list[Karten] = []
    spieler2Paechen: list[Karten] = []
    spieler2Dreizehner: list[Karten] = []
    spieler2listen = []

    def kartenDeckErstellung(self) -> list[Karten]:
        templist = []  # Speichert die Karten
        kartentyp = list(KartenTyp)
        kartenwert = list(KartenWert)

        for i in range(len(kartentyp)):
            for j in range(len(kartenwert)):
                templist.append(Karten(kartentyp[i], kartenwert[j]))
        return templist

    def game_first_move(self):
        objdrz1 = self.spieler1Dreizehner[
            len(self.spieler1Dreizehner) - 1]  #erstezt das lezte objekt des ersten Dreizehnerpaeckchen
        objdrz2 = self.spieler2Dreizehner[
            len(self.spieler2Dreizehner) - 1]  #erstezt das lezte objekt des zweiten Dreizehnerpaeckchen

        if (objdrz1.karteOffen == True and self.spieler2Dreizehner[
            len(self.spieler2Dreizehner) - 1].karteOffen == True):  #Wenn die längen gleich sind
            # Hier wird entschieden wer anfängt die Höhere Karte im Dreizehnerpäckchen gewinnt. Ausnahme ist wenn ein Ass kommt
            if (objdrz1.kartenwert.value > objdrz2.kartenwert.value) or (objdrz1.kartenwert.value == 1 and objdrz2.kartenwert.value != 1):  # stimmt wenn spieler1 die höhere karte hat
                self.spieler1.anderreihe = True
                self.current = self.spieler1
                #Hier wird die möglichkeit auf das erste Krips geschaffen.
                if self.current.anderreihe == True and self.current.spielernummer==1 and self.current.ist_krips() == True:
                    self.wouldbeKrips = True

            elif (objdrz1.kartenwert.value < objdrz2.kartenwert.value) or (objdrz2.kartenwert.value == 1 and objdrz1.kartenwert.value != 1):  # stimmt wenn spieler2 die höhere karte hat
                self.spieler2.anderreihe = True
                self.current = self.spieler2
                if self.current.anderreihe == True and self.current.spielernummer==2 and self.current.ist_krips() == True:
                    self.wouldbeKrips = True

            else:
                for karte in range(4):  #geht durch die ersten 4 plätze auf jeder seite durch und vergleich sie

                    if (self.platzliste[karte][0].kartenwert.value > self.platzliste[karte + 4][0].kartenwert.value):
                        self.spieler1.anderreihe = True
                        print("Schleife engaged Spieler1 ist drann?", self.spieler1.anderreihe)
                        return None
                    elif (self.platzliste[karte][0].kartenwert.value < self.platzliste[karte + 4][0].kartenwert.value):
                        self.spieler2.anderreihe = True
                        print("Schleife engaged Spieler2 ist drann?", self.spieler2.anderreihe)
                        return None

    def play(self,action):
        # karte kann von  den 3 spieler päckchen und 8 Seitenstreifen gelegt werden.
        # karte kann auf die 8 Mittlerenpäckchen, die 8 Seitenstreifen und den gegner Haufen gelegt werden.
        #action: str = input(f"\nSpieler{self.current.spielernummer} ist drann.")
                # "\nWas soll gemacht werden?\n"
                # "Karte aufdecken = A0 oder A2\n"  # Aufgedeckt werden können nur Päckchen und Dreizehner
                # "Karte hilegen = (A0-2,S1-8,)M1-8*S1-8*G0\n"
                # "Runde Aufhören= P,Kartenhaufen umdrehen = R\n")
        #action:str = input()
        print(action)
        #test sollte gelöscht werden

        # bis hier

        lenaction = len(action)
        print(f"{self.current.spielernummer} ist drann")
        print(f"{self.current.ist_krips()} current is krips")
        print(f"{self.wouldbeKrips} wouldbeKrips")
        #print(self.wouldbeKrips)
        #print(self.current.ist_krips(),"Hello")
        if lenaction == 1 and action == "P": self.current.aufhoeren();return None
        if lenaction == 1 and action == "R": self.current.resetHaufen();return None
        if lenaction == 1 and action == "K":
            if self.wouldbeKrips== True:
                self.current.wegen_krips_aufhoeren()
            return None
        elif lenaction == 2 and action == "A0" or lenaction == 4 and action == "A0A0":
            self.wouldbeKrips = self.current.ist_krips()
            self.current.karte_aufdecken(0)
            return None
        elif lenaction == 2 and action == "A2" or lenaction == 4 and action == "A2A2":
            self.wouldbeKrips = self.current.ist_krips()
            self.current.karte_aufdecken(1)

            return None  # Dreizehner
        if action == "A1":
            if not self.spieler1Paechen and self.spieler1Haufen and self.current.spielernummer == 1:
                self.wouldbeKrips = self.current.ist_krips()
                self.current.resetHaufen()


        if not self.spieler2Paechen and self.spieler2Haufen and self.current.spielernummer == 2:
            self.wouldbeKrips = self.current.ist_krips()
            self.current.resetHaufen()



        try: first = action[0]  #Herkunftslistentyp
        except IndexError:return None
        try: second = int(action[1])  #herkuftsliste
        except ValueError: return None
        except IndexError: return None
        try: third = action[2]  #Ziellistentyp
        except IndexError: return None
        try:fourth = int(action[3])  #zielliste
        except ValueError: return None
        except IndexError: return None

        match (first, third):  # M = Mitte, S = Seite, G = Gegner, A=Haupt
            case ("A","A"):
                if second==0 and fourth == 1:
                    self.current.aufhoeren()
            case ("A", "M"):
                if self.current.spielernummer == 1:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.mitteHinlegen(fourth, self.spieler1listen[second])
                    self.current.krips_karte_gespielt(self.spieler1listen[second])
                if self.current.spielernummer == 2:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.mitteHinlegen(fourth, self.spieler2listen[second])
                    self.current.krips_karte_gespielt(self.spieler1listen[second])
            case ("A", "S"):
                if self.current.spielernummer == 1:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.seiteHinlegen(fourth, self.spieler1listen[second])
                if self.current.spielernummer == 2:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.seiteHinlegen(fourth, self.spieler2listen[second])

            case ("A", "G"):
                if self.current.spielernummer == 1:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.gegener_geben(self.spieler1listen[second])

                if self.current.spielernummer == 2:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.gegener_geben(self.spieler2listen[second])
            case ("S", "M"):
                if self.current.spielernummer == 1:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.mitteHinlegen(fourth, self.platzliste[second - 1])
                    self.current.krips_karte_gespielt(self.platzliste[second - 1])
                if self.current.spielernummer == 2:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.mitteHinlegen(fourth, self.platzliste[second - 1])
                    self.current.krips_karte_gespielt(self.platzliste[second - 1])
            case ("S", "S"):
                if self.current.spielernummer == 1:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.seiteHinlegen(fourth, self.platzliste[second - 1])
                if self.current.spielernummer == 2:
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.seiteHinlegen(fourth, self.platzliste[second - 1])
            case ("S", "G"):
                print("test for S G")
                if self.current.spielernummer == 1:
                    self.wouldbeKrips = self.current.ist_krips()
                    print("test for S G player 1")
                    self.current.gegener_geben(self.platzliste[second - 1])
                if self.current.spielernummer == 2:
                    self.wouldbeKrips = self.current.ist_krips()
                    print("test for S G player 2")
                    self.current.gegener_geben(self.platzliste[second - 1])
            case ("A", "R"):
                if second == fourth:
                    self.current.resetHaufen()
            case ("K", "K"):
                if second == fourth:
                    self.current.wegen_krips_aufhoeren()
            case _:
                print("Ungültige Aktion.")
#
