

from .card_property_enum import CardType,CardValue
# Die Kartenklasse ist eine Einzelne Karte auf der die meisten Operation durchgeführt werden.
# Wichtig es ist nicht zu verwechseln mit der Klasse MKarte die die Karte auf dem Bildschirm darstellt.

class Card:
    def __init__(self, card_type: CardType, rank: CardValue) -> None:
        self.card_type: CardType  = card_type
        self.rank: CardValue = rank

    is_face_up:bool = False
    farbe:str


    @property
    def farbe(self) -> str:
        if(self.card_type == CardType.Pik or self.card_type ==CardType.Treff):
            return "Schwarz"
        else:
            return "Rot"
