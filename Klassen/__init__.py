from .spieler import Spieler
from Klassen.spiel import Spiel,Karten ,KartenWert, KartenTyp




def seitenKarten(game:Spiel, momentanerspieler:Spieler):
    for liste in game.platzliste:
        for karte in liste:
            print(karte.kartentyp.value,"-", karte.kartenwert,"-",karte.farbe)
        print("----------------")
    print("Momentanerspieler ist :",momentanerspieler.spielernummer)
    if momentanerspieler.spielernummer == 1:
        print("Das Dreizehner Päckchen hat " + str(len(game.spieler1Dreizehner)) + " Karten")

    if momentanerspieler.spielernummer == 2:
        print("Das Dreizehner Päckchen hat " + str(len(game.spieler2Dreizehner)) + " Karten")




def mittlereKarten(game:Spiel):
    for liste in game.mittlereliste:
        for karte in liste:
            print(karte.kartentyp.value, "-", karte.kartenwert)
        print("----------------")