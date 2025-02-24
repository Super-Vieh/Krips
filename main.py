from enum import Enum
import random

import pygame
from datenbank import Datenbank

from Pygame import GUI, MKarte
from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init,play_console,initialize_paechen, play_from_db
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
def main():
    game1 = Spiel()
    db = Datenbank()
    newdeck1 = game1.kartenDeckErstellung()
    newdeck2 = game1.kartenDeckErstellung()

    random.shuffle(newdeck1)
    random.shuffle(newdeck2)

    spieler1 = Spieler(1, newdeck1)
    spieler2 = Spieler(2, newdeck2)
    game1.spieler1 = spieler1
    game1.spieler2 = spieler2

    db.game=game1


    # Mega wichtig initialisiert das Spiel in Spieler sind zwei funktionen. Problem wegen circular import
    # wird über eine quasi setter funktion in der _init_ gemacht
    initialize(game1, spieler1, spieler2)

    db.verbindung_aufbauen()

    spieler1.ersteAktion()
    spieler2.ersteAktion()
    game1.game_first_move()
    initialize_paechen(game1)



    #play_from_db(game1,db)
    #gui = GUI(game1)
    #gui.instance()
    play_console(game1,db)
    #pygame.quit()
    #play_init(game1)
    #Das ist das Spiel in der Consolen ausgabe

    db.verbindung_schliessen()



if __name__ == "__main__":
    main()
