# Funktionen die zu der Klasse GUI gehören
import pygame
from .MKarte import MKarte

def sizeofkards(self,placeholder_bild,neue_breite=75)->any: # verändert die karte adequat zur eingegebenen breite
    neue_hoehe = placeholder_bild.get_height() * neue_breite/placeholder_bild.get_width()
    kleines_bild = pygame.transform.scale(placeholder_bild, (int(neue_breite), int(neue_hoehe)))
    return kleines_bild
def draw(self, list):
    highpriority = []
    lowpriority = []
    #differenzierung in haupbilder und bilder die im hintergrund sein sollen
    for bild in list:
        if bild.kard_reference: highpriority.append(bild)
        else:lowpriority.append(bild)
    for bild in lowpriority:
        self.screen.blit(bild.bild, (bild.x, bild.y))

    for bild in highpriority:
        if  bild.kard_reference and bild.kard_reference.karteOffen == False:
            self.screen.blit(self.placeholder_rueckseite, (bild.x, bild.y))
        else: self.screen.blit(bild.bild, (bild.x, bild.y))
        if bild.highlighted:
            highlight_rect = pygame.Rect(bild.x, bild.y, bild.bild.get_width(), bild.bild.get_height())
            pygame.draw.rect(self.screen, (255, 255, 0), highlight_rect, 2)  # Gelber Rand, Dicke 4

def waehle_karteaus(self)->MKarte:
    #Es müssen mindest 1 karte bewegbar sein
    maus = pygame.mouse.get_pos()
    templiste:list[int] =[]
    jointlist = self.gamelist+self.centerlist
    # Hier werden die Gegenerischen packchenkarten entfernt.
    if self.game.current.spielernummer == 1:
        for kard in jointlist:
            if self.game.spieler2Paechen and kard.kard_reference == self.game.spieler2Paechen[-1]:
                jointlist.remove(kard)
    if self.game.current.spielernummer == 2:
        for kard in jointlist:
            if self.game.spieler1Paechen and kard.kard_reference == self.game.spieler1Paechen[-1]:
                jointlist.remove(kard)


    for i in jointlist: #Pythagoras länge der hypotenuse als werkzeug

        pytagoras_a_quadrat = (i.x+i.bild.get_width()/2 - maus[0])**2
        pytagoras_b_quadrat = (i.y+i.bild.get_height()/2- maus[1])**2
        pytagoras_c = (pytagoras_a_quadrat + pytagoras_b_quadrat)**0.5
        templiste.append(pytagoras_c) #sqrt (a^2 +b^2) = c
    if not templiste:
        return None
    indize = indize_waehle_karteaus(self,templiste)
    #if jointlist[indize].kard_reference != None:
        #print(find_origin_list(self,jointlist[indize]))
    return jointlist[indize]

def indize_waehle_karteaus(self,templiste) -> int:
    kl_it = 0
    kr: int = templiste[0]
    #speichert die erste hypotenuse zum vergleichen
    for i in range(len(templiste)):
        #geht durch alle alle Elemente durch und hat für ein Element den indize "i"
        if templiste[i] < kr:
            #wenn die aktuelle hypotenuse kleiner ist als die vorherige
            kr = templiste[i]
            #wird die Speichervariable überschrieben.
            kl_it = i# ist die Position der kleineren hypotenuse in der Liste
    return kl_it

def set_card_at_center(self,feld:MKarte):
    #Die funktion wird immer ausgeführt.
    if  feld.state== True:
        eingabe = pygame.mouse.get_pos()
        feld.x = eingabe[0]-feld.bild.get_width()/2 # setzt die Position der Karte zu der Mitter der Maus
        feld.y = eingabe[1]-feld.bild.get_height()/2


def hebe_karte_auf(self, feld):

    if feld == None:
        return None

    if feld.bewegbar == False:
        return None

    if pygame.mouse.get_pressed()[0]:
        if feld.kard_reference.karteOffen == False:
            feld.kard_reference.karteOffen=True
            return None
        # delay damit der klick nicht mehrmals gezählt wird
        pygame.time.delay(250)
        feld.state = True
        feld.highlighted= True
        #print(feld.kard_reference.kartenwert, feld.kard_reference.kartentyp)


    # eingabe ist ein Tupel (x,y)

def lege_karte_ab(self,feld)-> str:
    if pygame.mouse.get_pressed()[0]:
        #print("test")
        self.action_done=True
        pygame.time.delay(250) # delay dami2t der klick nicht mehrmals gezählt wird
        if feld.state == True:
            feld.state = False
            feld.highlighted= False

        #remove ist wichtig damit waehle karte die nächste karte nimmt und nicht die gleiche
        self.gamelist.remove(feld)
        temp = waehle_karteaus(self)
        str1 = find_origin_list(self,feld)
        str2 = find_origin_list(self,temp)
        ergebnis = (str1 or "")+(str2 or "")
        print(ergebnis)
        return ergebnis

    #def an_karte_legen(self,feld_active:MKarte,feld_passive:MKarte):
def define_movable(self):
    #Es wird überprüft und gesetzt ob man eine karte bewegen kann
    jointlist = self.gamelist+self.centerlist
    for karte in jointlist:
        if karte.state == True:
            karte.bewegbar= True
            #soll schauen ob eine Karte hochgehoben ist und wenn ja wird der define movable a
            #erst wenn die karte wieder runtergelegt wird kann eine nächste karte hochgehoben werden bzw.
            #ist noch nicht kontroliert ob es wirklich funktioniert
        #alle karten in der liste von den dargestellten karten
        joint_list_fuer_paeckchen= self.game.platzliste+self.game.spieler1listen+self.game.spieler2listen
        for liste in joint_list_fuer_paeckchen:
            #alle karten in den platzlisten werden überprüft
            if not liste:
                continue
            if karte.kard_reference is liste[-1]:
                karte.bewegbar = True
                #karte.highlighted = True

def find_origin_list(self,feld:MKarte)->str:
    # findet die urpsrungsliste der karte

    map = {0: 2, 1: 1, 2: 0}
    for sublist in self.game.platzliste:
        for kard in sublist:
            if kard == feld.kard_reference:
                return f"S{self.game.platzliste.index(sublist)+1}"

    for sublist in self.game.spieler1listen:
        for kard in sublist:
            if kard == feld.kard_reference:
                if sublist in self.game.spieler1listen and self.game.current.spielernummer== 1:
                    return f"A{self.game.spieler1listen.index(sublist)}"

    for sublist in self.game.spieler2listen:
        for kard in sublist:
            if kard == feld.kard_reference:
                if sublist in self.game.spieler2listen and self.game.current.spielernummer== 2:
                    return f"A{self.game.spieler2listen.index(sublist)}"

    for sublist in self.game.mittlereliste:
        for kard in sublist:
            if kard == feld.kard_reference:
                return f"M{self.game.mittlereliste.index(sublist)+1}"
    return given_card_find_appropriate_list(self,feld)
def given_card_find_appropriate_list(self,feld:MKarte)->str:
    #funktion die die liste von der karte findet wenn es keine karte in der list gibt
    #600 und #900 linke und rechte seite der platzlisten
    #700 und #800 Kripslisten
    match(feld.x):#wird nach x position gefiltert

        case 600:
            i = (feld.y-140)/133
            return f"S{int(i+1)}"
        case 700:
            i = (feld.y-140)/66.5
            return f"M{int(i)+1}"
            #+1 weil die funktion play nur i von 1 -> 8 nutzt
        case 755:

            # 3 optionen möglich
            # 1. Karte karte nehmen bom haufen
            # 2. Karte auf den gegenerischen Haufen legen
            # 3. Eigene Runde beenden.
            # "R0" = Runde beenden
            # "G0" = Karte auf den gegnerischen Haufen legen
            # "A1" = Karte vom eigenen Haufen nehmen oder auf eigenen Haufen legen

            if feld.y ==25:
                if self.game.current.spielernummer == 1:
                    #wenn alle karten aus den packchen weg sind und noch karten im Haufen wird es umgedreht
                    if self.game.spieler1Haufen and not self.game.spieler1Paechen:
                        return "R0"
                    return "A1"
                if self.game.current.spielernummer == 2:
                    return "G0"
            if feld.y == 655:
                if self.game.current.spielernummer == 2:
                    #wenn alle karten aus den packchen weg sind und noch karten im Haufen wird es umgedreht
                    if self.game.spieler2Haufen and not self.game.spieler2Paechen:
                        return "R0"
                    return "A1"
                if self.game.current.spielernummer == 1:
                    return "G0"

        case 800:
            #Herleitung durch die funtkion Create_centerlist
            i = (feld.y-140)/66.5
            i+=1
            return f"M{int(i)+1}"
            #+1 weil die funktion play nur i von 1 -> 8 nutzt

        case 900:
            i = (feld.y+392)/133
            return f"S{int(i)+1}"




