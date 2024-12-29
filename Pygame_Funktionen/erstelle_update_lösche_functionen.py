# Funktionen die zu der Klasse GUI gehören
import pygame
import Pygame # kann aucbh nicht genutzt werden
from .mk_karte import MKarte
from Klassen import Karten, KartenWert, KartenTyp
from .unterstuezungs_und_navigations_funktionen_ import aendere_kartenformat,draw,waehle_karteaus,indize_waehle_karteaus,lege_karte_ab,hebe_karte_auf


# Diese Datei beinhaltet Teile der Funktion der Klasse GUI und wurde erstellt um die Datei kürzer zu gestallten.
# Die funktionen in dieser Datei sind: erstelle_spieler_packchen, loesche_alle_elemente, mache_die_packete, mache_die_haufen,
# mache_die_dreizehner, fuege_karte_der_gamelist_hinzu, erstelle_centerlist, erstelle_sidelist, kartendarstellungs_listen_funktion, initialisierung_der_bilder

#Die drei Wichtigsten funktionen sind erstelle_spieler_packchen, erstelle_centerlist und erstelle_sidelist
#Sie positionieren und erstellen die MKarten Objekte welche dann auf dem Bildschirm ausgegebemn werden.
#Sie werden nach jeder aktion ausgeführt. Alle Objekte werden mit jeder Aktion auf dem Bildschirm gelöscht und erstellt. Dieser Ansatz hätte eventuel noch sehr hohes optimierungspotenzial
def erstelle_spieler_packchen(self):
    bild = self.placeholder_rueckseite
    for i in range(3):
        index = i
        x_wert = 575
        y_wert1 = 25
        y_wert2 = 655
        match(index):
            case 0:
                mache_die_packete(self, x_wert, y_wert1, y_wert2, bild)
            case 1:
                mache_die_haufen(self, x_wert, y_wert1, y_wert2, index)
            case 2:
                mache_die_dreizehner(self, x_wert, y_wert1, y_wert2, index, bild)

def loesche_alle_elemente(self):
    self.gamelist = []
def mache_die_packete(self, x_wert, y_wert1, y_wert2, bild):
    if self.game.spieler1Paechen:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler1Paechen[-1], x_wert, y_wert1, bild)
        self.gamelist.append(MKarte(self.screen, x_wert , y_wert1,self.placeholder_rueckseite, None))
    else: self.gamelist.append(MKarte(self.screen,x_wert,y_wert1,self.plus,None))
    if self.game.spieler2Paechen:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler2Paechen[-1], x_wert, y_wert2, bild)
        self.gamelist.append(MKarte(self.screen, x_wert , y_wert2,self.placeholder_rueckseite, None))
    else: self.gamelist.append(MKarte(self.screen,x_wert,y_wert2,self.plus,None))
def mache_die_haufen(self, x_wert, y_wert1, y_wert2, index):
    if self.game.spieler1Haufen:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler1Haufen[-1], x_wert + index * 180, y_wert1)
    else: self.gamelist.append(MKarte(self.screen, x_wert + index * 180, y_wert1, self.plus, None))
    if self.game.spieler2Haufen:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler2Haufen[-1], x_wert + index * 180, y_wert2)
    else: self.gamelist.append(MKarte(self.screen, x_wert + index * 180, y_wert2, self.plus, None))
def mache_die_dreizehner(self, x_wert, y_wert1, y_wert2, index, bild):
    if self.game.spieler1Dreizehner:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler1Dreizehner[-1], x_wert + index * 180, y_wert1, bild)
        self.gamelist.append(MKarte(self.screen, x_wert + index * 180, y_wert1,self.placeholder_rueckseite, None))
    if self.game.spieler2Dreizehner:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler2Dreizehner[-1], x_wert + index * 180, y_wert2, bild)
        self.gamelist.append(MKarte(self.screen, x_wert+ index * 180 , y_wert2,self.placeholder_rueckseite, None))


def fuege_karte_der_gamelist_hinzu(self, card, x_wert, y_wert, bild=None):
        if not card.karteOffen:
            self.gamelist.append(MKarte(self.screen, x_wert, y_wert,  self.placeholder_rueckseite, card))
        else:
            geholtes_bild_liste = kartendarstellungs_listen_funktion(self, card)
            dargestelltes_bild = geholtes_bild_liste[card.kartenwert.value - 1]
            self.gamelist.append(MKarte(self.screen, x_wert, y_wert, dargestelltes_bild, card))
def erstelle_centerlist(self, bild):
    x_wert1 = 700
    x_wert2 = 800

    for i in range(8):
        y_wert = (i*108)/2 + i*12.5 if i%2==0 else ((i-1)*108)/2 + (i-1)*12.5    #karten höhe ist 108 || i%4 * 108
        y_wert+= 140
        current_list= self.game.mittlereliste[i]

        if current_list:
            kartendarstellung = kartendarstellungs_listen_funktion(self, current_list[-1])
            geholtes_bild = kartendarstellung[current_list[-1].kartenwert.value - 1]
        if i % 2 == 0:
            if not current_list:

                self.centerlist.append(MKarte(self.screen, x_wert1, y_wert, bild, None))
            else:
                self.centerlist.append(MKarte(self.screen, x_wert1, y_wert, geholtes_bild, current_list[-1]))
        elif i % 2 == 1:
            if not current_list:
                self.centerlist.append(MKarte(self.screen, x_wert2, y_wert, bild, None))
            else:

                self.centerlist.append(MKarte(self.screen, x_wert2, y_wert, geholtes_bild, current_list[-1]))



def erstelle_sidelist(self):
    for i in range(8):
        it = 0
        y_wert = i * 133 if i < 4 else (i - 4) * 133 # gekürze funktion

        y_wert+=140

        if not self.game.platzliste[i]:

            x_wert = 600 if i < 4 else 900
            self.gamelist.append(MKarte(self.screen, x_wert, y_wert, self.plus, None))
        for k in self.game.platzliste[i]:
            kartendarstellung = kartendarstellungs_listen_funktion(self, k)
            geholtes_bild = kartendarstellung[k.kartenwert.value - 1]


            #hard coded values
            x_wert = 700 + (-100 if i < 4 else 200) + (-it if i < 4 else it) * geholtes_bild.get_width() / 2
            self.gamelist.append(MKarte(self.screen, x_wert, y_wert, geholtes_bild, k))
            it += 1

def kartendarstellungs_listen_funktion(self, karte: Karten):
    match(karte.kartentyp.value):
        case "Pik":
            kartendarstellung = self.Kartentypen[0]
        case "Coeur":
            kartendarstellung = self.Kartentypen[1]
        case "Treff":
            kartendarstellung = self.Kartentypen[2]
        case "Karro":
            kartendarstellung = self.Kartentypen[3]
    return kartendarstellung



def initialisierung_der_bilder(self):
    placeholder_rueckseite = pygame.image.load('Bilder/Placeholder.png')
    placeholder_rueckseite = aendere_kartenformat(self, placeholder_rueckseite)

    pik2 = pygame.image.load('Bilder/2_of_spades.png')
    pik2 = aendere_kartenformat(self, pik2)
    couer2 = pygame.image.load('Bilder/2_of_hearts.png')
    couer2 = aendere_kartenformat(self, couer2)
    treff2 = pygame.image.load('Bilder/2_of_clubs.png')
    treff2 = aendere_kartenformat(self, treff2)
    karro2 = pygame.image.load('Bilder/2_of_diamonds.png')
    karro2 = aendere_kartenformat(self, karro2)

    pik3 = pygame.image.load('Bilder/3_of_spades.png')
    pik3 = aendere_kartenformat(self, pik3)
    couer3 = pygame.image.load('Bilder/3_of_hearts.png')
    couer3 = aendere_kartenformat(self, couer3)
    treff3 = pygame.image.load('Bilder/3_of_clubs.png')
    treff3 = aendere_kartenformat(self, treff3)
    karro3 = pygame.image.load('Bilder/3_of_diamonds.png')
    karro3 = aendere_kartenformat(self, karro3)

    pik4 = pygame.image.load('Bilder/4_of_spades.png')
    pik4 = aendere_kartenformat(self, pik4)
    couer4 = pygame.image.load('Bilder/4_of_hearts.png')
    couer4 = aendere_kartenformat(self, couer4)
    treff4 = pygame.image.load('Bilder/4_of_clubs.png')
    treff4 = aendere_kartenformat(self, treff4)
    karro4 = pygame.image.load('Bilder/4_of_diamonds.png')
    karro4 = aendere_kartenformat(self, karro4)

    pik5 = pygame.image.load('Bilder/5_of_spades.png')
    pik5 = aendere_kartenformat(self, pik5)
    couer5 = pygame.image.load('Bilder/5_of_hearts.png')
    couer5 = aendere_kartenformat(self, couer5)
    treff5 = pygame.image.load('Bilder/5_of_clubs.png')
    treff5 = aendere_kartenformat(self, treff5)
    karro5 = pygame.image.load('Bilder/5_of_diamonds.png')
    karro5 = aendere_kartenformat(self, karro5)

    pik6 = pygame.image.load('Bilder/6_of_spades.png')
    pik6 = aendere_kartenformat(self, pik6)
    couer6 = pygame.image.load('Bilder/6_of_hearts.png')
    couer6 = aendere_kartenformat(self, couer6)
    treff6 = pygame.image.load('Bilder/6_of_clubs.png')
    treff6 = aendere_kartenformat(self, treff6)
    karro6 = pygame.image.load('Bilder/6_of_diamonds.png')
    karro6 = aendere_kartenformat(self, karro6)

    pik7 = pygame.image.load('Bilder/7_of_spades.png')
    pik7 = aendere_kartenformat(self, pik7)
    couer7 = pygame.image.load('Bilder/7_of_hearts.png')
    couer7 = aendere_kartenformat(self, couer7)
    treff7 = pygame.image.load('Bilder/7_of_clubs.png')
    treff7 = aendere_kartenformat(self, treff7)
    karro7 = pygame.image.load('Bilder/7_of_diamonds.png')
    karro7 = aendere_kartenformat(self, karro7)

    pik8 = pygame.image.load('Bilder/8_of_spades.png')
    pik8 = aendere_kartenformat(self, pik8)
    couer8 = pygame.image.load('Bilder/8_of_hearts.png')
    couer8 = aendere_kartenformat(self, couer8)
    treff8 = pygame.image.load('Bilder/8_of_clubs.png')
    treff8 = aendere_kartenformat(self, treff8)
    karro8 = pygame.image.load('Bilder/8_of_diamonds.png')
    karro8 = aendere_kartenformat(self, karro8)

    pik9 = pygame.image.load('Bilder/9_of_spades.png')
    pik9 = aendere_kartenformat(self, pik9)
    couer9 = pygame.image.load('Bilder/9_of_hearts.png')
    couer9 = aendere_kartenformat(self, couer9)
    treff9 = pygame.image.load('Bilder/9_of_clubs.png')
    treff9 = aendere_kartenformat(self, treff9)
    karro9 = pygame.image.load('Bilder/9_of_diamonds.png')
    karro9 = aendere_kartenformat(self, karro9)

    pik10 = pygame.image.load('Bilder/10_of_spades.png')
    pik10 = aendere_kartenformat(self, pik10)
    couer10 = pygame.image.load('Bilder/10_of_hearts.png')
    couer10 = aendere_kartenformat(self, couer10)
    treff10 = pygame.image.load('Bilder/10_of_clubs.png')
    treff10 = aendere_kartenformat(self, treff10)
    karro10 = pygame.image.load('Bilder/10_of_diamonds.png')
    karro10 = aendere_kartenformat(self, karro10)

    pik11 = pygame.image.load('Bilder/Jack_of_spades2.png')
    pik11 = aendere_kartenformat(self, pik11)
    couer11 = pygame.image.load('Bilder/Jack_of_hearts2.png')
    couer11 = aendere_kartenformat(self, couer11)
    treff11 = pygame.image.load('Bilder/Jack_of_clubs2.png')
    treff11 = aendere_kartenformat(self, treff11)
    karro11 = pygame.image.load('Bilder/Jack_of_diamonds2.png')
    karro11 = aendere_kartenformat(self, karro11)

    pik12 = pygame.image.load('Bilder/Queen_of_spades2.png')
    pik12 = aendere_kartenformat(self, pik12)
    couer12 = pygame.image.load('Bilder/Queen_of_hearts2.png')
    couer12 = aendere_kartenformat(self, couer12)
    treff12 = pygame.image.load('Bilder/Queen_of_clubs2.png')
    treff12 = aendere_kartenformat(self, treff12)
    karro12 = pygame.image.load('Bilder/Queen_of_diamonds2.png')
    karro12 = aendere_kartenformat(self, karro12)

    pik13 = pygame.image.load('Bilder/King_of_spades2.png')
    pik13 = aendere_kartenformat(self, pik13)
    couer13 = pygame.image.load('Bilder/King_of_hearts2.png')
    couer13 = aendere_kartenformat(self, couer13)
    treff13 = pygame.image.load('Bilder/King_of_clubs2.png')
    treff13 = aendere_kartenformat(self, treff13)
    karro13 = pygame.image.load('Bilder/King_of_diamonds2.png')
    karro13 = aendere_kartenformat(self, karro13)

    pik1 = pygame.image.load('Bilder/Ace_of_spades2.png')
    pik1 = aendere_kartenformat(self, pik1)
    couer1 = pygame.image.load('Bilder/Ace_of_hearts.png')
    couer1 = aendere_kartenformat(self, couer1)
    treff1 = pygame.image.load('Bilder/Ace_of_clubs.png')
    treff1 = aendere_kartenformat(self, treff1)
    karro1 = pygame.image.load('Bilder/Ace_of_diamonds.png')
    karro1 = aendere_kartenformat(self, karro1)

    #Hier werden die Jeweiligen karten zugeteilt zu den Kartentypen
    self.Kartentypen.append([pik1, pik2, pik3, pik4, pik5, pik6, pik7, pik8, pik9, pik10, pik11, pik12, pik13])
    self.Kartentypen.append([couer1, couer2, couer3, couer4, couer5, couer6, couer7, couer8, couer9, couer10, couer11, couer12, couer13])
    self.Kartentypen.append([treff1, treff2, treff3, treff4, treff5, treff6, treff7, treff8, treff9, treff10, treff11, treff12, treff13])
    self.Kartentypen.append([karro1, karro2, karro3, karro4, karro5, karro6, karro7, karro8, karro9, karro10, karro11, karro12, karro13])