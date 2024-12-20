import pygame

from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init,initialize_paechen
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
from Pygame_Funktionen import MKarte
from Pygame_Funktionen import create_sidelist,create_centerlist,create_player_packages,initate_cards
from Pygame_Funktionen import sizeofkards,draw,waehle_karteaus,indize_waehle_karteaus,lege_karte_ab,hebe_karte_auf,define_movable,set_card_at_center



#Todo
# schreibe eine Funktion welche die Spieler päckchen positioniert
# schreibe eine Funktion die die karten dynamik des aufdeckens erlaubt / konflikt mit karte aufheben
# schreibe eine funktion die die karten korrekt darstellt offen zu
# kreire immaginäre felder 1/2 der x achse nach links oder nach rechts von der Letzen karte der liste
# schreibe eine weitere funktion die die Karten nur auf diese immaginären felder legen lässt
# Implementier die Spiel regeln



class GUI:
    def __init__(self,game:Spiel):
        pygame.init()
        self.run = True
        self.screen =pygame.display.set_mode((1540,  790))
        self.movable_cards:list[MKarte]= []
        self.centerlist = []
        self.sidelist = []
        self.gamelist:list[MKarte] = []
        self.game = game
        self.Kartentypen = []
        self.action_done = False
        self.placeholder_rueckseite = pygame.image.load('Bilder/Placeholder.png')
        self.placeholder_rueckseite = sizeofkards(self,self.placeholder_rueckseite)# ändert die größe zu einer vorherbestimmten größe





    def instance(self):
        plus = pygame.image.load('Bilder/Plus.png')
        plus = sizeofkards(self,plus, 50)
        initate_cards(self)

        destination = (100, 100)
        destination2 = (200, 200)
        create_centerlist(self, plus)
        create_sidelist(self, self.placeholder_rueckseite)
        create_player_packages(self)
        initate_cards(self)
        while self.run:
            self.screen.fill((30, 31, 34))  # Alles muss nach dem fill kommen sonst wird es nicht angezeigt

            define_movable(self)
            draw(self, self.centerlist)
            draw(self, self.sidelist)
            draw(self, self.gamelist)
            temp = waehle_karteaus(self)

            if temp.state == False:
                hebe_karte_auf(self, temp)
            elif temp.state == True:
                print(temp.kard_reference.kartenwert, temp.kard_reference.kartentyp)
                lege_karte_ab(self, temp)
            set_card_at_center(self, temp)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            pygame.display.update()




    def untilize_play(self):
        #action: str = input(f"\nSpieler{self.game.current.spielernummer} ist drann."
        #                         "\nWas soll gemacht werden?\n"
        #                        "Karte aufdecken = A0 oder A2\n"  # Aufgedeckt werden können nur Päckchen und Dreizehner
        #                       "Karte hilegen = (A0-2,S1-8,)M1-8*S1-8*G0\n"
        #                      "Runde Aufhören= P,Kartenhaufen umdrehen = R\n")
        if self.action_done == True: #action_done hat keinen bezug zu dem hier in der funktion
            self.create_player_packages(self)
            self.create_sidelist(self)

        #self.game.play(action)





