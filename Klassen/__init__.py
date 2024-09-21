
from .spieler import Spieler
from Klassen.spiel import Spiel,Karten ,KartenWert, KartenTyp

def initialize(game:Spiel,spielerimport1,spielerimport2): #Spiel wird für den Spieler initialisiert
    spielerimport1.set_spiel(game)
    spielerimport2.set_spiel(game)
    spielerimport1.set_gegenspieler(spielerimport2)
    spielerimport2.set_gegenspieler(spielerimport1)




def seitenKarten(game:Spiel, momentanerspieler:Spieler):
    for liste in game.platzliste:
        for karte in liste:
            print(karte.kartentyp.value,"-", karte.kartenwert,"-",karte.farbe)
        print("----------------")



def mittlereKarten(game:Spiel):
    for liste in game.mittlereliste:
        for karte in liste:
            print(karte.kartentyp.value, "-", karte.kartenwert)
        print("----------------")
