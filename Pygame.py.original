import pygame

from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
from Pygame_Funktionen import MKarte
from Pygame_Funktionen import erstelle_sidelist,erstelle_centerlist,erstelle_spieler_packchen,initialisierung_der_bilder,loesche_alle_elemente
from Pygame_Funktionen import finde_die_ursprungsliste,aendere_kartenformat,draw,waehle_karteaus,indize_waehle_karteaus,lege_karte_ab,hebe_karte_auf,definiere_bewegbare_karten,setze_karte_auf_den_zeiger


# Die Klasse GUI ist das Graphical User Interface des Spieles. Das Ziel dieses ist keine Funktionen zum Spiel hinzufügen
# sondern nur die Inputs des Nutzers an die Klasse Spiel und Spieler weiterzugeben.
# Es gibt den Zustand des Spieles wieder und ist im Grunde eine Glorifizierte eingabe konsole.
# Jede Aktion die hier getätig wird, wird in ein String kovertiert und in die Haupt logik eingespeist.


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
        self.placeholder_rueckseite = aendere_kartenformat(self, self.placeholder_rueckseite)# ändert die größe zu einer vorherbestimmten größe
        self.plus = pygame.image.load('Bilder/Plus.png')
        self.plus = aendere_kartenformat(self, self.plus, 50)
        self.current_card = None




    def image(self):
        initialisierung_der_bilder(self)
        erstelle_centerlist(self, self.plus)
        erstelle_sidelist(self)
        erstelle_spieler_packchen(self)

        self.screen.fill((30, 31, 34))
        draw(self, self.gamelist)
        draw(self, self.centerlist)
        self.reset()
        pygame.display.update()
    def instance(self):

        initialisierung_der_bilder(self)

        self.game.game_first_move()

        erstelle_centerlist(self, self.plus)
        erstelle_sidelist(self)
        erstelle_spieler_packchen(self)
        while self.run:
            self.screen.fill((30, 31, 34))  # Alles muss nach dem fill kommen sonst wird es nicht angezeigt

            definiere_bewegbare_karten(self)

            if self.game.spieler1.anderreihe == True: self.game.current = self.game.spieler1
            elif self.game.spieler2.anderreihe == True: self.game.current = self.game.spieler2

            #Utilize Play ist eine Funktion welche die Funktion Play der Klasse Spiel durchführt.
            self.nutze_play()

            draw(self, self.gamelist)
            draw(self, self.centerlist)

            krips_knoepfe = self.erstelle_knopf()
            for button in krips_knoepfe:
                pygame.draw.rect(self.screen, (255, 0, 0), button)


            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.circle(self.screen, (255, 0, 0), mouse_pos, 5)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

                self.rufe_krips(event, krips_knoepfe)
            pygame.display.update()




    def nutze_play(self):
        #Hier wird die Funktion Play() der Klasse Spiel durchgeführt

        temp = waehle_karteaus(self)
        if not temp: return None
        if temp.picked_up == False:
            hebe_karte_auf(self, temp)

        elif temp.picked_up == True:
            #print(temp.kard_reference.kartenwert, temp.kard_reference.kartentyp)
            ergebniss_string =lege_karte_ab(self)
            if ergebniss_string:
                self.game.play(ergebniss_string)
        setze_karte_auf_den_zeiger(self)
        self.reset()






    def reset(self):
        #Es löscht alle Elemente auf dem Bildschirm und erstellt neue nach dem gamestate.
        if self.action_done == True: #action_done hat keinen bezug zu dem hier in der funktion
            loesche_alle_elemente(self)
            erstelle_spieler_packchen(self)
            erstelle_sidelist(self)
            erstelle_centerlist(self, self.plus)
            self.action_done=False

    def erstelle_knopf(self):
        #Der Krips Button wird erstellt
        button_color = (255, 0, 0)  # Red color
        button_rects = [
            pygame.Rect(400, 25, 100, 108),  # Button at (400, 25)
            pygame.Rect(1085, 655, 100, 108)  # Button at (400, 655)
        ]
        return button_rects
    def rufe_krips(self, event, knoepfe_liste):
        # Die interaktion mit dem Krips Button wird hier gesteuert
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect in knoepfe_liste:
                if rect.collidepoint(event.pos):
                    self.game.play("K")

