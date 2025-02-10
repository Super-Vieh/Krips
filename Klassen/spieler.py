
from .karten import Karten
#In der Klasse Spieler sind alle Funktionen vorhanden welche auf das Spielgeschehen auswirkungen haben.
#Imgrunde ist die Klasse das Werkzeug welches von anhand der Regeln der Klasse Spiel genutzt wird.
#Die namen der einzelnen Funktionen Beschreiben den Nutzen ziemlich gut.
class Spieler:
    def __init__(self,spielernummer:int, owndeck: list[Karten]):
        self.game:'Spiel' = None
        self.spielernummer=spielernummer
        self.owndeck = owndeck
        self.gegenspieler: 'Spieler' = None
        self.anderreihe = False



    def set_gegenspieler(self, gegenspieler: 'Spieler'):
        #initialisierungs funktion
        from .spiel import Spiel
        self.gegenspieler = gegenspieler


    def set_spiel(self, game: 'Spiel'):
        # initialisierungs funktion wegen circular imports
        from .spiel import Spiel
        self.game = game


    def ersteAktion(self) -> None:

        if len(self.owndeck) != 52:
            raise ValueError("Deck has less than 52 cards")
        # Erstellung des Dreizehner Päckchens
        for i in range(13):
            if self.spielernummer == 1:
                self.game.spieler1Dreizehner.append(self.owndeck.pop())
            if self.spielernummer == 2:
                self.game.spieler2Dreizehner.append(self.owndeck.pop())

        #Hinlegen der ersten 4 Karten aus dem Normalen Päckchen auf die Seitenstreifen
        for i in range(1,5):
            if self.spielernummer == 1:
                self.seiteHinlegen(i, self.owndeck)
                #self.owndeck.pop()
            elif self.spielernummer == 2:
                self.seiteHinlegen(i + 4, self.owndeck)
                #self.owndeck.pop()

        if self.spielernummer == 1:
            self.game.spieler1Dreizehner[-1].karteOffen = True
            self.game.spieler1Paechen = self.owndeck
        if self.spielernummer == 2:
            self.game.spieler2Dreizehner[-1].karteOffen = True
            self.game.spieler2Paechen = self.owndeck





    def karte_aufdecken(self,packchen:int=0):
        drz1= self.game.spieler1Dreizehner
        drz2= self.game.spieler2Dreizehner
        spp1= self.game.spieler1Paechen
        spp2= self.game.spieler2Paechen
        if   packchen == 1:
            #Päckchen 1 ist das Dreizehner Päckchen
            if   self.spielernummer == 1 and spp1: drz1[-1].karteOffen = True
            elif self.spielernummer == 2 and spp2: drz2[-1].karteOffen = True
        elif packchen == 0:
            #Päckchen 0 ist das Normale Päckchen
            if   self.spielernummer == 1 and spp1: spp1[-1].karteOffen = True
            elif self.spielernummer == 2 and spp2: spp2[-1].karteOffen = True


    def mitteHinlegen(self,stelle:int,origin:list[Karten]):
        midliste = self.game.mittlereliste[stelle-1]#Es wird die liste ausgesucht aus den listen also stelle 1 ist [0]
        #Nur wenn das Ass gelegt wird
        if origin and origin[-1].kartenwert.value==1:
            #Wenn als erste Karte das Ass gelegt wird muss sichergegangen werden dass, das Ass zum Feld passt
            if stelle in [1,2] and origin[-1].kartentyp.value == "Pik":
                midliste.append(origin.pop())
            elif stelle in [3,4] and origin[-1].kartentyp.value == "Coeur":
                midliste.append(origin.pop())
            elif stelle in [5,6] and origin[-1].kartentyp.value == "Treff":
                midliste.append(origin.pop())
            elif stelle in [7,8] and origin[-1].kartentyp.value == "Karro":
                midliste.append(origin.pop())
        #Normale bedingung
        elif origin and self.kannMitteHinlegen(origin[len(origin)-1], stelle):
            midliste.append(origin.pop())



    def kannMitteHinlegen(self,karte:Karten,stelle:int)->bool: # Es wird überprüft ob das hinlegen der karte erlaubt , wichtig, in der Mitte
        midliste = self.game.mittlereliste[stelle-1]
        #Es wird die liste ausgesucht aus den listen also stelle 1 ist [0]
        # Es wird jetzt von 1-8 nummeriert
        if midliste and (len(midliste) == karte.kartenwert.value-1 and midliste[len(midliste)-1].kartentyp == karte.kartentyp):
            return True
        else:
            return False



    def kannSeiteHinlegen(self, karte: Karten, stelle: int) -> bool:
        aktliste = self.game.platzliste[stelle-1]
        if (aktliste[-1].kartenwert.value == karte.kartenwert.value + 1 and aktliste[-1].farbe != karte.farbe):
            return True
        return False


    def seiteHinlegen(self,stelle:int,origin:list[Karten])->None:
        aktliste:list[Karten] = self.game.platzliste[stelle-1]
        if origin and len(aktliste) == 0:
            tempkarte= origin.pop()
            tempkarte.karteOffen = True
            aktliste.append(tempkarte)
            return None
        if origin and (self.kannSeiteHinlegen(origin[-1], stelle)):
            tempkarte= origin.pop()
            tempkarte.karteOffen = True
            aktliste.append(tempkarte)
            return None


    def kann_gegener_geben(self, karte: Karten) -> bool:
        #kontroliert ob die karte um eins höher oder kleiner ist als die karte auf dem gegner packchen und ob die von der gleicher art ist
        if self.spielernummer == 1:
            sp2h = self.game.spieler2Haufen
            if not sp2h: return False
            elif (karte.kartentyp == sp2h[-1].kartentyp)and((karte.kartenwert.value == sp2h[-1].kartenwert.value + 1) or (karte.kartenwert.value == sp2h[-1].kartenwert.value -1)):
                #Es wird zuerst kontroliert ob die Art der Karte die gleiche ist wie die letzte Karte der Liste.
                #Danach wird überprüft ob die karte im karten wert sich um 1 hoch oder runter, unterscheiden. Also wie 7 und 9 sich zu 8 verhalten
                return True
        if self.spielernummer == 2:
            sp1h =self.game.spieler1Haufen
            if not sp1h: return False
            elif (karte.kartentyp == sp1h[-1].kartentyp)and((karte.kartenwert.value == sp1h[-1].kartenwert.value + 1) or (karte.kartenwert.value == sp1h[-1].kartenwert.value -1)) :
                #Es passiert genau das gleiche wie vorher
                return True


    def gegener_geben(self,origin:list[Karten])->None:
        if self.spielernummer == 1:
            if origin and self.kann_gegener_geben(origin[-1]):
                self.game.spieler2Haufen.append(origin.pop())
        if self.spielernummer == 2:
            if origin and self.kann_gegener_geben(origin[-1]):
                self.game.spieler1Haufen.append(origin.pop())
    def resetHaufen(self):
       if self.spielernummer == 1:
            for i in self.game.spieler1Haufen:
                i.karteOffen = False
            for kard in reversed(self.game.spieler1Haufen):
                self.game.spieler1Paechen.append(kard)
            self.game.spieler1Haufen = []
            for i in self.game.spieler1Haufen:
                print(i.karteOffen)
       if self.spielernummer == 2:
            for i in self.game.spieler2Haufen:
                i.karteOffen = False
            for kard in reversed(self.game.spieler2Haufen):
                self.game.spieler2Paechen.append(kard)
            self.game.spieler2Haufen = []
            for i in self.game.spieler2Haufen:
                print(i.karteOffen)
    def aufhoeren(self):
        if self.spielernummer ==1 and self.game.spieler1Paechen and self.game.spieler1Paechen[-1].karteOffen == True:
            self.game.spieler1Haufen.append(self.game.spieler1Paechen.pop())
            self.anderreihe= False
            self.gegenspieler.anderreihe = True
        if self.spielernummer ==2 and self.game.spieler2Paechen and self.game.spieler2Paechen[-1].karteOffen == True:
            self.game.spieler2Haufen.append(self.game.spieler2Paechen.pop())
            self.anderreihe= False
            self.gegenspieler.anderreihe= True
    def wegen_krips_aufhoeren(self):
        if self.spielernummer == 1:
            if self.game.spieler1Paechen[-1].karteOffen == True: self.aufhoeren()
            else:
                self.anderreihe== False
                self.gegenspieler.anderreihe==True
            self.game.wouldbeKrips = False
        if self.spielernummer == 2:
            if self.game.spieler2Paechen[-1].karteOffen == True: self.aufhoeren()
            else:
                self.anderreihe== False
                self.gegenspieler.anderreihe==True
            self.game.wouldbeKrips = False
    def ist_krips(self )-> bool:
        # Kontroliert ob ein Krips gelegt werden kann. Die funktion wird in play() aufgerufen
        if self.spielernummer == 1:
            ownliste=[self.game.spieler1Paechen,self.game.spieler1Haufen,self.game.spieler1Dreizehner]
            valideliste =[liste for liste in (self.game.platzliste + ownliste) if liste] # Alle listen die nicht leer sind werden in die valideliste geschrieben. Nur die listen aus platztlsite und ownlist werden überprüft
            for slist in valideliste:
                if slist[-1].kartenwert.value == 1: #Wenn irgenwo ein Ass liegt
                    return True
                for mliste in self.game.mittlereliste:
                    if slist and mliste:#Check ob die listen leer sind
                        if slist[-1].kartentyp.value == mliste[-1].kartentyp.value and slist[-1].kartenwert.value -1 == mliste[-1].kartenwert.value:
                            #Hier wird überprüft ob eine karte die gleiche art ist und 1 höher ist als die andren. Wenn irgentwo ein Pik ass ist liegt und eine Pik 2 überprüft wird die bedingung ausgelöst
                            return True

        if self.spielernummer == 2:
            ownliste=[self.game.spieler2Paechen,self.game.spieler2Haufen,self.game.spieler2Dreizehner]
            valideliste=[liste for liste in (self.game.platzliste + ownliste) if len(liste) > 0]
            for slist in valideliste:
                if slist[-1].kartenwert.value == 1: #Wenn irgenwo ein Ass leigt
                    return True
                for mliste in self.game.mittlereliste:
                    if slist and mliste:
                        if slist[-1].kartentyp.value == mliste[-1].kartentyp.value and slist[-1].kartenwert.value -1 == mliste[-1].kartenwert.value:
                            return True
        return False
    def krips_karte_gespielt(self, list_of_second:list[Karten]):
        # ist eine Funktion welche kontroliert, ob die gelegte karte nicht das Krips bedient und wenn es das tut wird wouldbekrips auf false gesetzt
        # wird in der play() funktion genutzt um Krips zu kontrolieren. Nur in dem Fall das eine Karte in die mitte gelegt wird, wird die funktiomn aufgerufen.
        if self.game.wouldbeKrips == False or not list_of_second:
            return None
        for kripslist in self.game.mittlereliste or not list_of_second:
            #die übergebene list_of second gibt die zuletzt gelegte karte wieder
            if kripslist and list_of_second[-1].kartentyp == kripslist[-1].kartentyp and list_of_second[-1].kartenwert.value -1 == kripslist[-1].kartenwert.value:
                self.game.wouldbeKrips = False





