
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

def print_top(game:Spiel):
    print("Spieler2:")
    #Es kann passieren das die listen kein ellement haben dann wird null geprintet
    try:sp2pl = game.spieler2Paechen[len(game.spieler2Paechen) - 1]
    except IndexError:sp2pl = None

    try:sp2hl = game.spieler2Haufen[len(game.spieler2Haufen) - 1]
    except IndexError:sp2hl = None

    try:sp2dl = game.spieler2Dreizehner[len(game.spieler2Dreizehner) - 1]
    except IndexError:sp2dl = None


    if(sp2pl is None):
        print("null",end="   ")
    else:
        if sp2pl.karteOffen == True:
            print(sp2pl.kartenwert.value,end="-")
            print(sp2pl.kartentyp.value,end="   ")
        else:print("Closed",end="   ")
    if sp2hl is None:
        print("null",end="   ")
    else:
        if sp2hl.karteOffen == True:
            print(sp2pl.kartenwert.value,end="-")
            print(sp2pl.kartentyp.value,end="   ")
    if sp2dl is None:
        print("null",end="   ")
    else:
        if sp2dl.karteOffen == True:
            print(sp2dl.kartenwert.value,end="-")
            print(sp2dl.kartentyp.value,end="   ")
        else:print("Closed",end="")
    print("\n")
def print_bot(game:Spiel):
    print("\n")
    print("Spieler1:")
    #Es kann passieren das die listen kein ellement haben dann wird null geprintet
    try:sp1pl = game.spieler1Paechen[len(game.spieler1Paechen) - 1]
    except IndexError:sp1pl = None

    try:sp1hl = game.spieler1Haufen[len(game.spieler1Haufen) - 1]
    except IndexError:sp1hl = None

    try:sp1dl = game.spieler1Dreizehner[len(game.spieler1Dreizehner) - 1]
    except IndexError:sp1dl = None

    if(sp1pl is None):
        print("null",end="   ")
    else:
        if sp1pl.karteOffen == True:
            print(sp1pl.kartenwert.value,end="-")
            print(sp1pl.kartentyp.value,end="   ")
        else:print("Closed",end="   ")
    if sp1hl is None:
        print("null",end="   ")
    else:
        if sp1hl.karteOffen == True:
            print(sp1pl.kartenwert.value,end="-")
            print(sp1pl.kartentyp.value,end="   ")
    if sp1dl is None:
        print("null",end="   ")
    else:
        if sp1dl.karteOffen == True:
            print(sp1dl.kartenwert.value,end="-")
            print(sp1dl.kartentyp.value,end="   ")
        else:print("Closed",end="")


def print_middle(game:Spiel,i :int):
    if(i == 0):
        ml1l = len(game.pik1)
        ml5l = len(game.pik2)
        if ml1l != 0 and ml5l != 0:
            print("___",game.pik1[ml1l-1].kartenwert.value,end="-")
            print(game.pik2[ml5l-1].kartenwert.value,end="___ ")
        elif ml1l == 0 and ml5l == 0:
            print("___null-null",end="___")
        elif ml1l == 0 and ml5l != 0:
            print(f"___null-{game.pik2[ml5l-1].kartenwert.value}",end="___ ")
        elif ml1l != 0 and ml5l == 0:
            print(f"___ {game.pik1[ml1l-1].kartenwert.value}-null",end="___ ")
    if(i == 1):
        ml2l = len(game.coeur1)
        ml6l = len(game.coeur2)
        if ml2l != 0 and ml6l != 0:
            print("___",game.coeur1[ml2l-1].kartenwert.value,end="-")
            print(game.coeur2[ml6l-1].kartenwert.value,end="___ ")
        elif ml2l == 0 and ml6l == 0:
            print("___null-null",end="___")
        elif ml2l == 0 and ml6l != 0:
            print(f"___null-{game.coeur2[ml6l-1].kartenwert.value}",end="___ ")
        elif ml2l != 0 and ml6l == 0:
            print(f"___ {game.coeur1[ml2l-1].kartenwert.value}-null",end="___ ")
    if(i == 2):
        ml3l = len(game.treff1)
        ml7l = len(game.treff2)
        if ml3l != 0 and ml7l != 0:
            print("___", game.treff1[ml3l-1].kartenwert.value, end="-")
            print(game.treff2[ml7l-1].kartenwert.value, end="___ ")
        elif ml3l == 0 and ml7l == 0:
            print("___null-null", end="___")
        elif ml3l == 0 and ml7l != 0:
            print(f"___null-{game.treff2[ml7l-1].kartenwert.value}", end="___ ")
        elif ml3l != 0 and ml7l == 0:
            print(f"___ {game.treff1[ml3l-1].kartenwert.value}-null", end="___ ")
    if(i == 3):
        ml4l = len(game.karro1)
        ml8l = len(game.karro2)

        if ml4l != 0 and ml8l != 0:
            print("___", game.karro1[ml4l-1].kartenwert.value, end="-")
            print(game.karro2[ml8l-1].kartenwert.value, end="___ ")
        elif ml4l == 0 and ml8l == 0:
            print("___null-null", end="___")
        elif ml4l == 0 and ml8l != 0:
            print(f"___null-{game.karro2[ml8l-1].kartenwert.value}", end="___ ")
        elif ml4l != 0 and ml8l == 0:
            print(f"___ {game.karro1[ml4l-1].kartenwert.value}-null", end="___ ")

def print_sidesplus(game:Spiel):
    for i in range(4):
        if i == 0:
            pl1l = len(game.platzliste1)# pl1l ist die menge der karten
            pl5l = len(game.platzliste5)
            for j in range(pl1l): #für jede karte wird der zugehörige platz angezeigt
                print(game.platzliste1[pl1l-j-1].kartenwert.value,end=",") # Es wird die länge subtrahiert von dem mal. -1 ist da pl1l ein Int ist und deswegen bei 1 anfängt
            print_middle(game,i)
            for j in range(pl5l): #für jede karte auf der anderen seite wird der zugehörige platz angezeigt
                print(game.platzliste5[j].kartenwert.value,end=",")
            print()
        if i == 1:
            pl2l = len(game.platzliste2)
            pl6l = len(game.platzliste6)
            for j in range(pl2l):
                print(game.platzliste2[pl2l-j-1].kartenwert.value,end=",")
            print_middle(game,i)
            for j in range(pl6l):
                print(game.platzliste6[j].kartenwert.value,end=",")
            print()
        if i == 2:
            pl3l = len(game.platzliste3)
            pl7l = len(game.platzliste7)
            for j in range(pl3l):
                print(game.platzliste3[pl3l-j-1].kartenwert.value,end=",")
            print_middle(game,i)
            for j in range(pl7l):
                print(game.platzliste7[j].kartenwert.value,end=",")
            print()
        if i == 3:
            pl4l = len(game.platzliste4)
            pl8l = len(game.platzliste8)
            for j in range(pl4l):
                print(game.platzliste4[pl4l-j-1].kartenwert.value,end=",")
            print_middle(game,i)
            for j in range(pl8l):
                print(game.platzliste8[j].kartenwert.value,end=",")