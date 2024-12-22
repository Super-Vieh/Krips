import pygame

from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init,initialize_paechen
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
from Pygame_Funktionen import MKarte
from Pygame_Funktionen import create_sidelist,create_centerlist,create_player_packages,initate_cards,delete_kard_from_gamelist
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
        self.centerlist:list[MKarte] = []
        self.gamelist:list[MKarte] = []
        self.movable_list:list[MKarte]=[]
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
        create_sidelist(self)
        create_player_packages(self)
        initate_cards(self)
        while self.run:
            self.screen.fill((30, 31, 34))  # Alles muss nach dem fill kommen sonst wird es nicht angezeigt

            define_movable(self)

            self.untilize_play()
            draw(self, self.gamelist)
            draw(self, self.centerlist)

            # Get the current mouse position
            mouse_pos = pygame.mouse.get_pos()
            # Draw a point at the mouse position
            pygame.draw.circle(self.screen, (255, 0, 0), mouse_pos, 5)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            pygame.display.update()




    def untilize_play(self):
        #action: str = input(f"\nSpieler{self.game.current.spielernummer if self.game.current else "None"} ist drann.")
                        # "\nWas soll gemacht werden?\n"
                        # "Karte aufdecken = A0 oder A2\n"  # Aufgedeckt werden können nur Päckchen und Dreizehner
                        # "Karte hilegen = (A0-2,S1-8,)M1-8*S1-8*G0\n"
                        # "Runde Aufhören= P,Kartenhaufen umdrehen = R\n")

        #if self.game.gameon:
         #   if self.game.spieler1.anderreihe == True: self.game.current =  self.game.spieler1
          #  elif  self.game.spieler2.anderreihe == True:  self.game.current =  self.game.spieler2
        #if self. game.current.anderreihe == True:
        temp = waehle_karteaus(self)
        if not temp: print("Keine Karte ausgewählt")
        if temp.state == False:
            hebe_karte_auf(self, temp)
        elif temp.state == True:
            #print(temp.kard_reference.kartenwert, temp.kard_reference.kartentyp)
            lege_karte_ab(self, temp)
        set_card_at_center(self, temp)
        self.reset()




        #self.game.play(action)

    def reset(self):
        if self.action_done == True: #action_done hat keinen bezug zu dem hier in der funktion
            delete_kard_from_gamelist(self)
            create_player_packages(self)
            create_sidelist(self)
            self.action_done=False




