
from .karten import Karten

class Spieler:
    def __init__(self,spielernummer:int, owndeck: list[Karten],game:'Spiel'):
        self.game = game
    def __init__(self,spielernummer:int, owndeck: list[Karten]):
        self.game:'Spiel' = None
        self.spielernummer=spielernummer
        self.owndeck = owndeck
        self.gegenspieler: 'Spieler' = None


    realanderreihe = False
    dreizehner      :list[Karten] =[]
    eigablage       :list[Karten] =[]
    normalpaekchen: list[Karten] = []
    gegenspieler: 'Spieler'


    @property
    def anderreihe(self, realanderreihe: bool) -> bool:
        return realanderreihe


    @anderreihe.setter
    def anderreihe(self, value: bool):
            realanderreihe = value


    def set_gegenspieler(self, gegenspieler: 'Spieler'):
        from .spiel import Spiel
        self.gegenspieler = gegenspieler


    def set_spiel(self, game: 'Spiel'):
        from .spiel import Spiel
        self.game = game


    def ersteAktion(self) -> None:
        if (len(self.owndeck) != 52):
            raise ValueError("Deck has less than 52 cards")
        for i in range(13):
            if self.spielernummer == 1: self.game.spieler1Dreizehner.append(self.owndeck.pop())
            if self.spielernummer == 2: self.game.spieler2Dreizehner.append(self.owndeck.pop())

        for i in range(5):  # Die ersten 4 karten werde rausgelegt range(5) weil 0-4
            if i == 0: continue  # Index null wird ignoriert
            if self.spielernummer == 1:  # Beim ersten Spieler werden die ersten 4 und beim zweiten 4-8 plätze belegt
                self.game.seiteHinlegen(self.owndeck[0], i)
                self.owndeck.remove(self.owndeck[0])
            elif self.spielernummer == 2:
                self.game.seiteHinlegen(self.owndeck[0], i + 4)
                self.owndeck.remove(self.owndeck[0])

        if self.spielernummer == 1: self.game.spieler1Dreizehner[
            len(self.game.spieler1Dreizehner) - 1].karteOffen = True  # erste Dreizehnerkarte wird aufgedeckt
        if self.spielernummer == 2: self.game.spieler2Dreizehner[len(self.game.spieler2Dreizehner) - 1].karteOffen = True

    # def istAmZug(self): #Wird geloopt solange anderreihe == True