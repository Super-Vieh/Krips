
from .spieler import Spieler
from Klassen.spiel import Spiel,Karten ,KartenWert, KartenTyp
# Die Init Datei ist dazu da um die Klassen zu importieren und die Funktionen zu definieren
# Ausßerdem hat es den Sin, Sachen für das Spiel selber(Spieler, Spiel) zu initialisieren.

def initialize(game:Spiel,spielerimport1,spielerimport2):
    #Spiel wird für den Spieler initialisiert
    spielerimport1.set_spiel(game)
    spielerimport2.set_spiel(game)
    spielerimport1.set_gegenspieler(spielerimport2)
    spielerimport2.set_gegenspieler(spielerimport1)


def initialize_paechen(game:Spiel):
    # initialisierung der Karten packchen
    game.spieler1listen.append(game.spieler1Paechen)
    game.spieler1listen.append(game.spieler1Haufen)
    game.spieler1listen.append(game.spieler1Dreizehner)
    game.spieler2listen.append(game.spieler2Paechen)
    game.spieler2listen.append(game.spieler2Haufen)
    game.spieler2listen.append(game.spieler2Dreizehner)
def play_init(game:Spiel):
    # Eine Spiel Simmulation in der Konsole ohne Gui
    while game.gameon:
        if game.spieler1.anderreihe == True: game.current = game.spieler1
        elif game.spieler2.anderreihe == True: game.current = game.spieler2
        while game.current.anderreihe == True:
            # print_top(game),print_bot(game) und print_sidesplus(game) sind Funktionen die die Karten auf der Konsole ausgeben
            print_top(game)
            print_sidesplus(game)
            print_bot(game)
            action: str = input(f"\nSpieler{game.current.spielernummer} ist drann."
                    "\nWas soll gemacht werden?\n"
                    "Karte aufdecken = A0 oder A2\n"  # Aufgedeckt werden können nur Päckchen und Dreizehner
                    "Karte hilegen = (A0-2,S1-8,)M1-8*S1-8*G0\n"
                    "Runde Aufhören= P,Kartenhaufen umdrehen = R,Krips rufen = K\n")
            if action=="M": return None
            game.play_nn(action)
def play_console(game:Spiel,db:'Datenbank'):
    zugwechsel_ID =0
    db.erstelle_neuen_spieldatensatz()
    db.erstelle_kartendatensatz()
    ergtuple = convertiere_spielkartenstand(game)
    db.erstelle_ein_kartendatensatz(ergtuple[0],ergtuple[1],ergtuple[2],ergtuple[3],ergtuple[4],ergtuple[5])
    while game.gameon:

        alle_actions:str = ""
        zugwechsel_ID+=1
        if game.spieler1.anderreihe == True: game.current = game.spieler1
        elif game.spieler2.anderreihe == True: game.current = game.spieler2
        while game.current.anderreihe == True:
            # print_top(game),print_bot(game) und print_sidesplus(game) sind Funktionen die die Karten auf der Konsole ausgeben
            print_top(game)
            print_sidesplus(game)
            print_bot(game)
            action: str = input(f"\nSpieler{game.current.spielernummer} ist drann."
                    "\nWas soll gemacht werden?\n"
                    "Karte aufdecken = A0 oder A2\n"  # Aufgedeckt werden können nur Päckchen und Dreizehner
                    "Karte hilegen = (A0-2,S1-8,)M1-8*S1-8*G0\n"
                    "Runde Aufhören= P,Kartenhaufen umdrehen = R,Krips rufen = K\n"
                    "Stop =M\n")
            if action=="M": return None
            game.console_play(action)
            alle_actions= alle_actions+","+action

        if game.current== game.spieler1: lezterspieler=1
        else:lezterspieler=2
        db.erstelle_ein_spieldatensatz(zugwechsel_ID, alle_actions, lezterspieler)
def play_from_db(game:Spiel, db:'Datenbank',whatgamenr:int):
    clear_game_lists(game)
    #hier wird der Anfangskartenstand aus der Datenbank geladen
    convertiere_spielkartenstand_aus_db(db.extrahiere_spielkarten(whatgamenr),game)

    actions = db.extrahiere_spiel(whatgamenr)
    while game.gameon:

        if game.spieler1.anderreihe == True:
            game.current = game.spieler1
        elif game.spieler2.anderreihe == True:
            game.current = game.spieler2
        while game.current.anderreihe == True:
            print_top(game)
            print_sidesplus(game)
            print_bot(game)
            (action, actions)= take_first_action(actions)

            print(action)
            game.console_play(action)
            if actions== "" or None:
                #die ausgabe wird ein letztes mall noch ausgegeben
                print_top(game)
                print_sidesplus(game)
                print_bot(game)
                print("Game Complete")
                return None



def take_first_action(actions:str)-> tuple[str,str]:
    action=""
    try: actions[0]
    except IndexError:
        return("M","")
    if actions[0]==",": actions= actions[1:]
    for buchstabe in actions[:]:
        if buchstabe==",":
            actions= actions[1:]
            return action,actions
        action+=buchstabe
        actions= actions[1:]#stringsslicing
    return action,""
def convertiere_spielkartenstand(game:Spiel):
    sp1_paeckchen =""
    for karte in game.spieler1Paechen:
        sp1_paeckchen+= str(karte.kartenwert.value)
        sp1_paeckchen+= karte.kartentyp.value
        sp1_paeckchen+=","
    sp1_dreizehner=""
    for karte in game.spieler1Dreizehner:
        sp1_dreizehner += str(karte.kartenwert.value)
        sp1_dreizehner += karte.kartentyp.value
        sp1_dreizehner += ","
    sp2_paeckchen=""
    for karte in game.spieler2Paechen:
        sp2_paeckchen += str(karte.kartenwert.value)
        sp2_paeckchen += karte.kartentyp.value
        sp2_paeckchen += ","
    sp2_dreizehner=""
    for karte in game.spieler2Dreizehner:
        sp2_dreizehner += str(karte.kartenwert.value)
        sp2_dreizehner += karte.kartentyp.value
        sp2_dreizehner += ","
    sp1_4karten=""
    sp2_4karten=""
    for liste in range(0,8):
        if liste<= 3:
            sp1_4karten+= str(game.platzliste[liste][0].kartenwert.value)
            sp1_4karten+= game.platzliste[liste][0].kartentyp.value
            sp1_4karten+=","
        else:
            sp2_4karten += str(game.platzliste[liste][0].kartenwert.value)
            sp2_4karten += game.platzliste[liste][0].kartentyp.value
            sp2_4karten += ","
    return (sp1_paeckchen,sp2_paeckchen,sp1_dreizehner,sp2_dreizehner,sp1_4karten,sp2_4karten)

def convertiere_spielkartenstand_aus_db(allekarten:tuple[tuple[int,str,str,str]],game:Spiel):
    for zeile in allekarten:
        (aktion,rest)=("",zeile[1])
        while (aktion,rest)!=("M",""):
            aktion,rest=take_first_action(rest)
            if aktion=="M": break
            fuege_karte_zueiner_liste_hinzu(stringzukarte(aktion),zeile[0],"Paeckchen",game)
        (aktion,rest)=("",zeile[2])
        while (aktion,rest)!=("M",""):
            (aktion,rest)=take_first_action(rest)#kann "M" zurückgeben
            if aktion=="M": break
            fuege_karte_zueiner_liste_hinzu(stringzukarte(aktion),zeile[0],"Dreizehner",game)
        (aktion,rest)=("",zeile[3])
        while (aktion,rest)!=("M",""):
            (aktion,rest)=take_first_action(rest)#kann "M" zurückgeben
            if aktion=="M": break
            fuege_karte_zueiner_liste_hinzu(stringzukarte(aktion),zeile[0],"4Karten",game)
    game.spieler1Dreizehner[-1].karteOffen=True
    game.spieler2Dreizehner[-1].karteOffen=True


#Achtung wie die reihnfolge ist des eingebens. Es kann passieren das die karten verkehrtherumm eingesetzt werden
def fuege_karte_zueiner_liste_hinzu(karte:Karten,spieler:int,liste:str,game:Spiel):
    if spieler==1:
        match(liste):
            case("Paeckchen"):
                game.spieler1Paechen.insert(0, karte)
            case("Dreizehner"):
                game.spieler1Dreizehner.append( karte)
            case("4Karten"):
                for i in range(0,4):
                    if game.platzliste[i] == []:
                        game.platzliste[i].append(karte)
                        return  None
            case _:
                    print("Fehler bei fuege_karte_zueiner_liste_hinzu")
    if spieler==2:
        match(liste):
            case("Paeckchen"):
                game.spieler2Paechen.insert(0, karte)
            case("Dreizehner"):
                game.spieler2Dreizehner.append( karte)
            case("4Karten"):
                for i in range(4,8):
                    if game.platzliste[i] == []:
                        game.platzliste[i].append(karte)
                        return None
            case _:
                print("Fehler bei fuege_karte_zueiner_liste_hinzu")


def stringzukarte(kartenstr:str)->Karten:
    typ=kartenstr
    wert = kartenstr[0]
    #Der erste buchstabe ist immer eine Zahl, der zweite kann
    try :
        #kontrolle ob die zweite zahl zu int konvertierbar ist
        int(typ[1])
        wert+=typ[1]
    except (IndexError,ValueError):
        pass
    wert = int(wert)
    if wert<=9:
        typ=typ[1:]
    else:
        typ=typ[2:]

    wert=KartenWert(wert)
    typ=KartenTyp[typ]


    return Karten(typ,wert)

def clear_game_lists(game:Spiel):
    for list in game.platzliste:
        list.clear()
    for list in game.spieler1listen:
        list.clear()
    for list in game.spieler2listen:
        list.clear()
























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

def print_top(game:Spiel): #Folgende Print ausgaben waren mit "!Hilfe" von Chat GPT erstellt
    print("\nSpieler2:")
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
            print(sp2hl.kartenwert.value,end="-")
            print(sp2hl.kartentyp.value,end="   ")
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
    try:sp1pl = game.spieler1Paechen[- 1]
    except IndexError:sp1pl = None

    try:sp1hl = game.spieler1Haufen[len(game.spieler1Haufen) - 1]
    except IndexError:sp1hl = None

    try:sp1dl = game.spieler1Dreizehner[- 1]
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
        if game.spieler1Haufen[-1].karteOffen == True:
            print(sp1hl.kartenwert.value,end="-")
            print(sp1hl.kartentyp.value,end="   ")
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
            print(f"___ \033[30m{game.pik1[ml1l-1].kartenwert.value}\033[0m", end="-")
            print(f"\033[30m{game.pik2[ml5l-1].kartenwert.value}\033[0m", end="___ ")
        elif ml1l == 0 and ml5l == 0:
            print("\033[30m___null-null\033[0m", end="___")
        elif ml1l == 0 and ml5l != 0:
            print(f"\033[30m___null-{game.pik2[ml5l-1].kartenwert.value}\033[0m", end="___ ")
        elif ml1l != 0 and ml5l == 0:
            print(f"\033[30m___ {game.pik1[ml1l-1].kartenwert.value}-null\033[0m", end="___ ")

    if(i == 1):
        ml2l = len(game.coeur1)
        ml6l = len(game.coeur2)
        if ml2l != 0 and ml6l != 0:
            print(f"___ \033[31m{game.coeur1[ml2l-1].kartenwert.value}\033[0m", end="-")
            print(f"\033[31m{game.coeur2[ml6l-1].kartenwert.value}\033[0m", end="___ ")
        elif ml2l == 0 and ml6l == 0:
            print("\033[31m___null-null\033[0m", end="___")
        elif ml2l == 0 and ml6l != 0:
            print(f"\033[31m___null-{game.coeur2[ml6l-1].kartenwert.value}\033[0m", end="___ ")
        elif ml2l != 0 and ml6l == 0:
            print(f"\033[31m___ {game.coeur1[ml2l-1].kartenwert.value}-null\033[0m", end="___ ")

    if(i == 2):
        ml3l = len(game.treff1)
        ml7l = len(game.treff2)
        if ml3l != 0 and ml7l != 0:
            print(f"___ \033[90m{game.treff1[ml3l-1].kartenwert.value}\033[0m", end="-")
            print(f"\033[90m{game.treff2[ml7l-1].kartenwert.value}\033[0m", end="___ ")
        elif ml3l == 0 and ml7l == 0:
            print("\033[90m___null-null\033[0m", end="___")
        elif ml3l == 0 and ml7l != 0:
            print(f"\033[90m___null-{game.treff2[ml7l-1].kartenwert.value}\033[0m", end="___ ")
        elif ml3l != 0 and ml7l == 0:
            print(f"\033[90m___ {game.treff1[ml3l-1].kartenwert.value}-null\033[0m", end="___ ")

    if(i == 3):
        ml4l = len(game.karro1)
        ml8l = len(game.karro2)
        if ml4l != 0 and ml8l != 0:
            print(f"___ \033[35m{game.karro1[ml4l-1].kartenwert.value}\033[0m", end="-")
            print(f"\033[35m{game.karro2[ml8l-1].kartenwert.value}\033[0m", end="___ ")
        elif ml4l == 0 and ml8l == 0:
            print("\033[35m___null-null\033[0m", end="___")
        elif ml4l == 0 and ml8l != 0:
            print(f"\033[35m___null-{game.karro2[ml8l-1].kartenwert.value}\033[0m", end="___ ")
        elif ml4l != 0 and ml8l == 0:
            print(f"\033[35m___ {game.karro1[ml4l-1].kartenwert.value}-null\033[0m", end="___ ")


def print_sidesplus(game:Spiel):
    for i in range(4):
        if i == 0:
            pl1l = len(game.platzliste1)
            pl5l = len(game.platzliste5)
            for j in range(pl1l):
                if game.platzliste1[pl1l-j-1].kartentyp.value == "Pik":
                    print(f"\033[30m{game.platzliste1[pl1l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste1[pl1l-j-1].kartentyp.value == "Coeur":
                    print(f"\033[31m{game.platzliste1[pl1l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste1[pl1l-j-1].kartentyp.value == "Treff":
                    print(f"\033[90m{game.platzliste1[pl1l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste1[pl1l-j-1].kartentyp.value == "Karro":
                    print(f"\033[35m{game.platzliste1[pl1l-j-1].kartenwert.value}\033[0m", end=",")
            print_middle(game, i)
            for j in range(pl5l):
                if game.platzliste5[j].kartentyp.value == "Pik":
                    print(f"\033[30m{game.platzliste5[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste5[j].kartentyp.value == "Coeur":
                    print(f"\033[31m{game.platzliste5[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste5[j].kartentyp.value == "Treff":
                    print(f"\033[90m{game.platzliste5[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste5[j].kartentyp.value == "Karro":
                    print(f"\033[35m{game.platzliste5[j].kartenwert.value}\033[0m", end=",")
            print()

        if i == 1:
            pl2l = len(game.platzliste2)
            pl6l = len(game.platzliste6)
            for j in range(pl2l):
                if game.platzliste2[pl2l-j-1].kartentyp.value == "Pik":
                    print(f"\033[30m{game.platzliste2[pl2l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste2[pl2l-j-1].kartentyp.value == "Coeur":
                    print(f"\033[31m{game.platzliste2[pl2l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste2[pl2l-j-1].kartentyp.value == "Treff":
                    print(f"\033[90m{game.platzliste2[pl2l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste2[pl2l-j-1].kartentyp.value == "Karro":
                    print(f"\033[35m{game.platzliste2[pl2l-j-1].kartenwert.value}\033[0m", end=",")
            print_middle(game, i)
            for j in range(pl6l):
                if game.platzliste6[j].kartentyp.value == "Pik":
                    print(f"\033[30m{game.platzliste6[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste6[j].kartentyp.value == "Coeur":
                    print(f"\033[31m{game.platzliste6[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste6[j].kartentyp.value == "Treff":
                    print(f"\033[90m{game.platzliste6[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste6[j].kartentyp.value == "Karro":
                    print(f"\033[35m{game.platzliste6[j].kartenwert.value}\033[0m", end=",")
            print()

        if i == 2:
            pl3l = len(game.platzliste3)
            pl7l = len(game.platzliste7)
            for j in range(pl3l):
                if game.platzliste3[pl3l-j-1].kartentyp.value == "Pik":
                    print(f"\033[30m{game.platzliste3[pl3l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste3[pl3l-j-1].kartentyp.value == "Coeur":
                    print(f"\033[31m{game.platzliste3[pl3l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste3[pl3l-j-1].kartentyp.value == "Treff":
                    print(f"\033[90m{game.platzliste3[pl3l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste3[pl3l-j-1].kartentyp.value == "Karro":
                    print(f"\033[35m{game.platzliste3[pl3l-j-1].kartenwert.value}\033[0m", end=",")
            print_middle(game, i)
            for j in range(pl7l):
                if game.platzliste7[j].kartentyp.value == "Pik":
                    print(f"\033[30m{game.platzliste7[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste7[j].kartentyp.value == "Coeur":
                    print(f"\033[31m{game.platzliste7[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste7[j].kartentyp.value == "Treff":
                    print(f"\033[90m{game.platzliste7[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste7[j].kartentyp.value == "Karro":
                    print(f"\033[35m{game.platzliste7[j].kartenwert.value}\033[0m", end=",")
            print()

        if i == 3:
            pl4l = len(game.platzliste4)
            pl8l = len(game.platzliste8)
            for j in range(pl4l):
                if game.platzliste4[pl4l-j-1].kartentyp.value == "Pik":
                    print(f"\033[30m{game.platzliste4[pl4l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste4[pl4l-j-1].kartentyp.value == "Coeur":
                    print(f"\033[31m{game.platzliste4[pl4l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste4[pl4l-j-1].kartentyp.value == "Treff":
                    print(f"\033[90m{game.platzliste4[pl4l-j-1].kartenwert.value}\033[0m", end=",")
                elif game.platzliste4[pl4l-j-1].kartentyp.value == "Karro":
                    print(f"\033[35m{game.platzliste4[pl4l-j-1].kartenwert.value}\033[0m", end=",")
            print_middle(game, i)
            for j in range(pl8l):
                if game.platzliste8[j].kartentyp.value == "Pik":
                    print(f"\033[30m{game.platzliste8[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste8[j].kartentyp.value == "Coeur":
                    print(f"\033[31m{game.platzliste8[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste8[j].kartentyp.value == "Treff":
                    print(f"\033[90m{game.platzliste8[j].kartenwert.value}\033[0m", end=",")
                elif game.platzliste8[j].kartentyp.value == "Karro":
                    print(f"\033[35m{game.platzliste8[j].kartenwert.value}\033[0m", end=",")
