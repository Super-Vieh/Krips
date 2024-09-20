from msilib.schema import Property

from .karteneigenschaftenenum import KartenTyp,KartenWert
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
