from enum import Enum
class KartenTyp(Enum):
    Pik   = "Pik"
    Coeur = "Coeur"
    Treff = "Treff"
    Karro = "Karro"

class KartenWert(Enum):
    Ass     = 1 #Ass muss 14 oder 1 sein noch nicht gelöst
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