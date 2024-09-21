from enum import Enum
import random

from Klassen import Spiel, Karten, Spieler, seitenKarten, mittlereKarten,initialize

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
        game1.spieler1=spieler1
        game1.spieler2=spieler2

        # Mega wichtig initialisiert das Spiel in Spieler sind zwei funktionen. Problem wegen circular import
        # wird über eine quasi setter funktion in der _init_ gemacht
        initialize(game1, spieler1, spieler2)


        spieler1.ersteAktion()
        spieler2.ersteAktion()
        spieler1.karte_aufdecken()

        game1.game_first_move()

        seitenKarten(game1, spieler1)




if __name__ == "__main__":




    main()
