
from .karten import Karten

class Spieler:
    def __init__(self,spielernummer:int, owndeck: list[Karten]):
        self.game:'Spiel' = None
        self.spielernummer=spielernummer
        self.owndeck = owndeck
        self.gegenspieler: 'Spieler' = None
        self.anderreihe = False
    #Funktionen bis jetzt:
    #set_gegemspieler, set_spiel
    #ersteAktion
    #karte_aufdecken
    #mitteHinlegen
    #kannMitteHinlegen
    #kannSeiteHinlegen
    #seiteHinlegen


    def set_gegenspieler(self, gegenspieler: 'Spieler'):
        from .spiel import Spiel
        self.gegenspieler = gegenspieler


    def set_spiel(self, game: 'Spiel'):
        from .spiel import Spiel
        self.game = game


    def ersteAktion(self) -> None:
        drz1 = self.game.spieler1Dreizehner
        drz2 = self.game.spieler2Dreizehner
        if len(self.owndeck) != 52:
            raise ValueError("Deck has less than 52 cards")
        for i in range(13):
            if self.spielernummer == 1:
                drz1.append(self.owndeck.pop())
            if self.spielernummer == 2:
                drz2.append(self.owndeck.pop())

        for i in range(5):
            if i == 0:
                continue
            if self.spielernummer == 1:
                self.seiteHinlegen(i, self.owndeck)
                self.owndeck.pop()
            elif self.spielernummer == 2:
                self.seiteHinlegen(i + 4, self.owndeck)
                self.owndeck.pop()

        if self.spielernummer == 1:
            drz1[len(drz1) - 1].karteOffen = True
            self.game.spieler1Paechen = self.owndeck
        if self.spielernummer == 2:
            drz2[len(drz2) - 1].karteOffen = True
            self.game.spieler2Paechen = self.owndeck





    def karte_aufdecken(self,packchen:int=0):
        drz1= self.game.spieler1Dreizehner
        drz2= self.game.spieler2Dreizehner
        spp1= self.game.spieler1Paechen
        spp2= self.game.spieler2Paechen
        if   packchen == 1:
            if   self.spielernummer == 1 and spp1: drz1[len(drz1) - 1].karteOffen = True # erste karte des Dreizehner wird geöffnet.
            elif self.spielernummer == 2 and spp2: drz2[len(drz2) - 1].karteOffen = True
        elif packchen == 0:
            if   self.spielernummer == 1 and spp1: spp1[len(spp1) - 1].karteOffen = True
            elif self.spielernummer == 2 and spp2: spp2[len(spp2) - 1].karteOffen = True


    def mitteHinlegen(self,stelle:int,origin:list[Karten]):
        midliste = self.game.mittlereliste[stelle-1]#Es wird die liste ausgesucht aus den listen also stelle 1 ist 1
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
            sp2h =self.game.spieler2Haufen
            if len(sp2h) == 0: return False
            elif (karte.kartentyp == sp2h[len(sp2h)-1].kartentyp)and(karte.kartenwert.value == sp2h[len(sp2h)-1].kartenwert.value + 1) or (karte.kartenwert.value == sp2h[len(sp2h)-1].kartenwert.value + 1) :
                return True
        if self.spielernummer == 2:
            sp1h =self.game.spieler1Haufen
            if len(sp1h) == 0: return False
            elif (karte.kartentyp == sp1h[len(sp1h)-1].kartentyp)and(karte.kartenwert.value == sp1h[len(sp1h)-1].kartenwert.value + 1) or (karte.kartenwert.value == sp1h[len(sp1h)-1].kartenwert.value + 1) :
                return True

    def gegener_geben(self,origin:list[Karten])->None:
        if self.spielernummer == 1:
            if origin and self.kann_gegener_geben(origin[len(origin)-1]):
                self.game.spieler2Haufen.append(origin.pop())
        if self.spielernummer == 2:
            if origin and self.kann_gegener_geben(origin[len(origin)-1]):
                self.game.spieler1Haufen.append(origin.pop())
    def resetHaufen(self):
       if self.spielernummer == 1:
        for i in self.game.spieler1Haufen:
            i.karteOffen = False
        self.game.spieler1Paechen = self.game.spieler1Haufen
        self.game.spieler1Haufen = []
       if self.spielernummer == 2:
        for i in self.game.spieler2Haufen:
            i.karteOffen = False
        self.game.spieler2Paechen = self.game.spieler2Haufen
        self.game.spieler2Haufen = []
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
        if self.spielernummer == 2:
            if self.game.spieler2Paechen[-1].karteOffen == True: self.aufhoeren()
            else:
                self.anderreihe== False
                self.gegenspieler.anderreihe==True

    def ist_krips(self )-> bool: # Wenn irgendeine karte hingelegt werden kann wird true zurückgegeben. Auch wenn eine Karte reingelegt wurde
        if self.spielernummer == 1:
            templiste=[self.game.spieler1Paechen,self.game.spieler1Haufen,self.game.spieler1Dreizehner]
            valideliste =[liste for liste in (self.game.platzliste + templiste) if len(liste) > 0] # Heist listcomprehesion elementof x for x in x if(soemthing)
            for slist in valideliste:
                for mliste in self.game.mittlereliste:
                    if slist and mliste:#Check ob die listen leer sind
                        if slist[-1].kartentyp.value == mliste[-1].kartentyp.value and slist[-1].kartenwert.value -1 == mliste[-1].kartenwert.value:
                            return True

        if self.spielernummer == 2:
            templiste=[self.game.spieler2Paechen,self.game.spieler2Haufen,self.game.spieler2Dreizehner]
            valideliste=[liste for liste in (self.game.platzliste + templiste) if len(liste) > 0]
            for slist in valideliste:
                for mliste in self.game.mittlereliste:
                    if slist and mliste:#Check ob die listen leer sind
                        if slist[-1].kartentyp.value == mliste[-1].kartentyp.value and slist[-1].kartenwert.value -1 == mliste[-1].kartenwert.value:
                            return True
        return False