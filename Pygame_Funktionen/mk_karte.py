import pygame
from Klassen import Card
#Die Klasse MKarte ist eine Repräsentation einer Normalen Karte auf dem Bildschirm.
class MKarte:

    def __init__(self,screen:any,x:int,y:int,bild:any,kard_reference:Card):
        self.x = x
        self.y = y
        self.bild = bild
        self.screen = screen
        self.picked_up = False # 0 = nicht hohgehoben, 1 = hochgehoben
        self.bewegbar= False
        self.highlighted = False
        self.kard_reference:Card = kard_reference #Weist eine Karte zu jedem Kartenobjekt zu