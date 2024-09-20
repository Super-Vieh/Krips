from enum import Enum
import random
from Klassen import Spiel, Karten, Spieler, seitenKarten, mittlereKarten

def main():

        game1 = Spiel()


        newdeck1 = game1.kartenDeckErstellung()
        newdeck2 = game1.kartenDeckErstellung()


        random.shuffle(newdeck1)
        random.shuffle(newdeck2)


        spieler1 = Spieler(1, newdeck1, game1,)
        spieler2 = Spieler(2, newdeck2, game1)
        game1.spieler1=spieler1
        game1.spieler2=spieler2


        spieler1.ersteAktion()
        spieler2.ersteAktion()

        game1.gamemaster()


        seitenKarten(game1, spieler1)
        seitenKarten(game1, spieler2)

        # while(spieler1.anderreihe or spieler2.anderreihe):
        #         if spieler1.anderreihe: spieler1.istAmZug()
        #         if spieler2.anderreihe: spieler2.istAmZug()


if __name__ == "__main__":




    main()
