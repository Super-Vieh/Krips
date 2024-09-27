from enum import Enum
import random
from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init
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
    game1.pik2.append(karte10)

    play_init(game1)




    print(f"Spieler 1 ist dran:{spieler1.anderreihe}")


if __name__ == "__main__":
    main()
