from enum import Enum
import random
from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert


def main():
    game1 = Spiel()

    newdeck1 = game1.kartenDeckErstellung()
    newdeck2 = game1.kartenDeckErstellung()

    random.shuffle(newdeck1)
    random.shuffle(newdeck2)

    spieler1 = Spieler(1, newdeck1)
    spieler2 = Spieler(2, newdeck2)
    spieler1 = Spieler(1, newdeck1)
    spieler2 = Spieler(2, newdeck2)
    game1.spieler1 = spieler1
    game1.spieler2 = spieler2
    karte10 = Karten(KartenTyp.Pik, KartenWert.Ass)
    karte11 = Karten(KartenTyp.Pik, KartenWert.Zwei)

    # Mega wichtig initialisiert das Spiel in Spieler sind zwei funktionen. Problem wegen circular import
    # wird über eine quasi setter funktion in der _init_ gemacht
    initialize(game1, spieler1, spieler2)

    spieler1.ersteAktion()
    spieler2.ersteAktion()


    game1.game_first_move()
    game1.pik1.append(karte10)
    game1.pik1.append(karte11)

    #seitenKarten(game1, spieler1)

    print_top(game1)
    print_sidesplus(game1)
    print_bot(game1)

if __name__ == "__main__":
    main()