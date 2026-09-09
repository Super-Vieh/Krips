import pygame
from Klassen import Card
#Die Klasse MKarte ist eine Repräsentation einer Normalen Karte auf dem Bildschirm.
class MKarte:

    def __init__(self, screen: pygame.Surface, x: int, y: int, bild: pygame.Surface, kard_reference: Card):
        self.x: int = x
        self.y: int = y
        self.bild: pygame.Surface = bild
        self.screen: pygame.Surface = screen
        self.picked_up: bool = False # 0 = nicht hohgehoben, 1 = hochgehoben
        self.bewegbar: bool = False
        self.highlighted: bool = False
        self.kard_reference: Card = kard_reference #Weist eine Karte zu jedem Kartenobjekt zu