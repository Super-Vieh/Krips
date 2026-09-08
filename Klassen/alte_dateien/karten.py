

from .karteneigenschaftenenum import KartenTyp,KartenWert
# Die Kartenklasse ist eine Einzelne Karte auf der die meisten Operation durchgeführt werden.
# Wichtig es ist nicht zu verwechseln mit der Klasse MKarte die die Karte auf dem Bildschirm darstellt.

class Karten:
    def __init__(self, kartenTyp: KartenTyp, kartenWert: KartenWert):
        self.kartentyp  = kartenTyp
        self.kartenwert = kartenWert

    karteOffen:bool = False
    farbe:str


    @property
    def farbe(self) -> str:
        if(self.kartentyp == KartenTyp.Pik or self.kartentyp ==KartenTyp.Treff):
            return "Schwarz"
        else:
            return "Rot"
