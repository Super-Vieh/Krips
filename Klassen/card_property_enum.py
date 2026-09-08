from enum import Enum
class CardType(Enum):
    Pik   = "Pik"
    Coeur = "Coeur"
    Treff = "Treff"
    Karro = "Karro"

class CardValue(Enum):
    ACE     = 1
    TWO     = 2
    THREE   = 3
    FOUR    = 4
    FIVE    = 5
    SIX     = 6
    SEVEN   = 7
    EIGHT   = 8
    NINE    = 9
    TEN     = 10
    JACK    = 11
    QUEEN   = 12
    KING    = 13
