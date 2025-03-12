from .karten import Karten, KartenTyp, KartenWert
from .spieler import Spieler
# Die Klasse Spiel beinhaltet alle Daten, die das Spiel selber betreffen.
# Die anfangsanktionen werden hier durchgeführt.(kartendeck erstellung, game_first_move)
# Das Spiel wird hier gestartet und die Aktionen der Spieler werden hier durchgeführt nach dem Algorithmus der Funktion play().
class Spiel:
    current: Spieler = None
    gameon = True
    wouldbeKrips = False
    winner = 0 #
    spieler1: Spieler
    spieler2: Spieler
    #Mitte listen
    pik1: list[Karten] = []
    pik2: list[Karten] = []
    coeur1: list[Karten] = []
    coeur2: list[Karten] = []
    treff1: list[Karten] = []
    treff2: list[Karten] = []
    karro1: list[Karten] = []
    karro2: list[Karten] = []
    mittlereliste = [pik1, pik2, coeur1, coeur2, treff1, treff2, karro1, karro2]
    #Seitenlisten
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
    #Spielerlisten
    spieler1Haufen: list[Karten] = []
    spieler1Paechen: list[Karten] = []
    spieler1Dreizehner: list[Karten] = []
    spieler1listen = []

    spieler2Haufen: list[Karten] = []
    spieler2Paechen: list[Karten] = []
    spieler2Dreizehner: list[Karten] = []
    spieler2listen = []

    stalemate_counter=0
    last_playerpackages_length=[]
    def kartenDeckErstellung(self) -> list[Karten]:
        templist = []  # Speichert die Karten
        kartentyp = list(KartenTyp)
        kartenwert = list(KartenWert)

        for i in range(len(kartentyp)):
            for j in range(len(kartenwert)):
                templist.append(Karten(kartentyp[i], kartenwert[j]))
        return templist

    def game_first_move(self):
        # Hier wird entschieden wer anfängt. Die Höchste karte auf dem Dreizehner päckchen gewinnt
        # Wenn die karten gleich sind werden die ausgelegten nach unt
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
        #Diese Funktion beinhaltet die Spielregeln und ist der ort an dem das Spielgeschehen stattfindet.

        # action ist ein bis zu 4 stelliger string aus Buchsabe, Zahl, Buchtabe ,Zahl
        # der erste buchstabe bestimmt die art der liste aus der die karte genommen wird oder eine bestimmte aktion
        # der zweite buchstabe bestimmt die art der liste auf die die karte gelegt wird
        # die erste zahl bestimmt die position der karte der Ursprungsliste, also die genaue liste. es wird immer die letzte karte einer Liste genommen.
        # die zweite zahl macht genau das gleiche wie die erste nur für die Ziel liste.

        # Es gibt 4 verschiedene Listenarten: A = Hauptliste, S = Seitenliste, M = Mittelliste, G = Gegnerliste

        # Die Hauptliste ist die Liste der Karten die der Spieler auf der Hand hat. Diese ändert sich je nachdem welcher Spieler an der Reihe ist.
        # Es gibt für jeden Spieler 3 eigene listen. Das Dreizehnerpäckchen, das Normale Packchen und der Haufen.

        # Das Dreizehnerpäckchen ist die Liste der Karten die der Spieler zu beginn des Spiels bekommt. Es sind 13 Karten die nicht auf den Haufen gelegt werden können.

        # Das Normale Packchen ist die Liste der Karten die der Spieler im laufe des Spiels bekommt. Diese Karten können auf den Haufen gelegt werden wenn man nicht mehr kann oder seinen Zug benden möchte.

        # Der Haufen ist ein Päckchen welches alte karten beinhaltet. Die jeweils oberste Karte kann auf die Äußeren felder gelegt werden. Wenn das Packchen leer wird es aufgefüllt mit den Karten die auf dem haufen liegen.

        # Die Seitenliste ist die Liste der Karten die auf den 8 Plätzen liegen.

        # Die Mittelliste ist die Liste der Karten die in der Mitte liegen. Es sind 8 Felder und die ersten karten die darauf gelegt werden können sind Asse. 2 Pik-, 2 Coeur-, 2 Treff- und 2 Karro Asse.
        # Diese werden von Ass zu Zwei bis König der gleichen Karten Art zusammengelegt.

        # Die Gegnerliste hängt von dem Spieler ab welcher am Zug ist. Für Spieler 1 ist die Gegnerliste der Haufen des Spieler 2.
        # Auf diese liste können karten abgelegt werden die von der gleicher Art sind aber von wert sich um 1 hoch oder runter unterscheiden. z.B. auf eine Herz 7 kann eine Herz 6 oder 8 gelegt werden.

        # Zusatz aktionen sind P, K, und R
        # P ist das bennden des zuges. K ist das Rufen des Krips und R ist das Umlegen des Haufens wenn das Normale Päckchen leer ist.

        # Das Krips ist eine Aktion die der Gegenspieler ausführen kann währen der Spieler am zug ist. Diese Symbolisiert das der Spieler ein fehler gemacht hat.
        # Die Grundsatzt ist: Immer wenn man etwas in die Mitte legen kann muss man es machen!
        # Wenn man gegen diesen grundsatz verstößt und der gegegner es bemerkt ist er drann.

        lenaction = len(action)
        print(f"{self.current.spielernummer} ist drann")
        print(self.spieler1Haufen)
        #print(f"{self.current.ist_krips()} current is rufe_krips")
        #print(f"{self.wouldbeKrips} wouldbeKrips")
        print(action)
        match (lenaction, action):
                case (1, "P"):
                    self.current.aufhoeren()
                    return None
                case (1, "R"):
                    self.current.resetHaufen()
                    return None
                case (1, "K"):
                    if self.wouldbeKrips:
                        self.current.wegen_krips_aufhoeren()
                    return None
                case (2, "A0") | (4, "A0A0"):
                    print("test")
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.karte_aufdecken(0)
                    return None
                case (2, "A2") | (4, "A2A2"):
                    self.wouldbeKrips = self.current.ist_krips()
                    self.current.karte_aufdecken(1)
                    return None

        if action == "A1":
            if not self.spieler1Paechen and self.spieler1Haufen and self.current.spielernummer == 1:
                self.wouldbeKrips = self.current.ist_krips()
                self.current.resetHaufen()


        if not self.spieler2Paechen and self.spieler2Haufen and self.current.spielernummer == 2:
            self.wouldbeKrips = self.current.ist_krips()
            self.current.resetHaufen()


        # Hier wird sichergestellt das keine fehler entstehen wenn auf die Zeichen der Aktion zugegriffen wird.
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

    def console_play(self,action):
        if(action=="A0"):
            self.wouldbeKrips = self.current.ist_krips()
            self.current.karte_aufdecken(0)
            return None
        elif action=="A2":
            self.wouldbSeKrips = self.current.ist_krips()
            self.current.karte_aufdecken(1)
            return None
        try:
            first = action[0]  # Herkunftslistentyp
            print(action)
            second = int(action[1])  # Herkunftsliste
            third = action[2]  # Ziellistentyp
            fourth = int(action[3])  # Zielliste
        except (IndexError, ValueError):
            return None



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
                    self.current.krips_karte_gespielt(self.spieler2listen[second])
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
            case _:
                if first=="R":
                    self.current.resetHaufen()
                if first=="K":
                    self.current.wegen_krips_aufhoeren()
                if first!="K" and first!="R":
                    print("Ungültige Aktion.")


   # die funktion current_playerpackage_length() überprüft die länge aller spielerlisten. wenn die länger aller spielerlisten gleich ist dann wird der stalemate_counter um 1 erhöht
    def current_playerpackage_length(self):
        current_len = [len(self.spieler1Haufen),len(self.spieler1Paechen),len(self.spieler1Dreizehner),len(self.spieler2Haufen),len(self.spieler2Paechen),len(self.spieler2Dreizehner)]
        if current_len == self.last_playerpackages_length:
            self.stalemate_counter+=1
        else:
            self.stalemate_counter=0
        self.last_playerpackages_length=current_len
    def is_stalemate(self)->bool: # wenn der stalemate_counter 30 erreicht hat wird die funktion True zurückgeben
        self.current_playerpackage_length()
        if self.stalemate_counter>=30:
            if len(self.spieler1Dreizehner)!=0:
                self.winner=1
            elif len(self.spieler2Dreizehner)!=0:
                self.winner=2
            else:
                self.winner=0
            return True
        else:return False


    def game_ended(self):
        if not self.spieler1Haufen and not self.spieler1Paechen and not self.spieler1Dreizehner:
            self.winner = 1
            self.gameon = False
        if not self.spieler2Haufen and not self.spieler2Paechen and not self.spieler2Dreizehner:
            self.winner = 2
            self.gameon = False
        if self.is_stalemate():
            self.gameon = False
    def return_state(self):
        spieler1listen = [self.spieler1Paechen,self.spieler1Haufen,self.spieler1Dreizehner]
        spieler2listen = [self.spieler2Paechen,self.spieler2Haufen,self.spieler2Dreizehner]
        return (spieler1listen,spieler2listen,self.platzliste,self.mittlereliste)