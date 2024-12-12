from enum import Enum
import random
from Pygame import GUI, MKarte
from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init,initialize_paechen
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
def main():
    game1 = Spiel()

    newdeck1 = game1.kartenDeckErstellung()
    newdeck2 = game1.kartenDeckErstellung()

    random.shuffle(newdeck1)
    random.shuffle(newdeck2)

    spieler1 = Spieler(1, newdeck1)
    spieler2 = Spieler(2, newdeck2)
    game1.spieler1 = spieler1
    game1.spieler2 = spieler2
    karte1 = Karten(KartenTyp.Pik, KartenWert.Ass)


    # Mega wichtig initialisiert das Spiel in Spieler sind zwei funktionen. Problem wegen circular import
    # wird über eine quasi setter funktion in der _init_ gemacht
    initialize(game1, spieler1, spieler2)


    spieler1.ersteAktion()
    spieler2.ersteAktion()
    game1.game_first_move()
    initialize_paechen(game1)


    game1.mittlereliste[0].append(karte1)


   # play_init(game1)
    gui = GUI(game1)
    gui.instance()


if __name__ == "__main__":
    main()
