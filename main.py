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
    karte2 = Karten(KartenTyp.Coeur, KartenWert.Ass)
    karte3 = Karten(KartenTyp.Treff, KartenWert.Ass)
    karte4 = Karten(KartenTyp.Karro, KartenWert.Ass)


    # Mega wichtig initialisiert das Spiel in Spieler sind zwei funktionen. Problem wegen circular import
    # wird über eine quasi setter funktion in der _init_ gemacht
    initialize(game1, spieler1, spieler2)


    spieler1.ersteAktion()
    spieler2.ersteAktion()
    game1.game_first_move()
    initialize_paechen(game1)


    #game1.mittlereliste[0].append(karte1)
    #game1.platzliste[1].append(karte1)
    #game1.spieler2Haufen.append(karte1)
    # game1.mittlereliste[0].append(karte1)
    # game1.mittlereliste[2].append(karte2)
    # game1.mittlereliste[4].append(karte3)
    # game1.mittlereliste[6].append(karte4)
    # game1.mittlereliste[1].append(karte1)
    # game1.mittlereliste[3].append(karte2)
    # game1.mittlereliste[5].append(karte3)
    # game1.mittlereliste[7].append(karte4)


    gui = GUI(game1)
    gui.instance()
    #print(game1.current.spielernummer)
    #play_init(game)

if __name__ == "__main__":
    main()
