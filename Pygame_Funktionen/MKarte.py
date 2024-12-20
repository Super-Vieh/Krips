import pygame
from Klassen import Karten
class MKarte:

    def __init__(self,screen:any,x:int,y:int,bild:any,kard_reference:Karten):
        self.x = x
        self.y = y
        self.bild = bild
        self.screen = screen
        self.state = False # 0 = nicht ausgewaehlt, 1 = ausgewaehlt
        self.bewegbar= False
        self.highlighted = False
        self.kard_reference:Karten = kard_reference#