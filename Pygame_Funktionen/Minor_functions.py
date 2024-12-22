import pygame
from .MKarte import MKarte

def sizeofkards(self,placeholder_bild,neue_breite=75)->any: # verändert die karte adequat zur eingegebenen breite
    neue_hoehe = placeholder_bild.get_height() * neue_breite/placeholder_bild.get_width()
    kleines_bild = pygame.transform.scale(placeholder_bild, (int(neue_breite), int(neue_hoehe)))
    return kleines_bild
def draw(self, list):
    for bild in list:
        self.screen.blit(bild.bild, (bild.x, bild.y))

        #Chat GPT
        if bild.highlighted:
            highlight_rect = pygame.Rect(bild.x, bild.y, bild.bild.get_width(), bild.bild.get_height())
            pygame.draw.rect(self.screen, (255, 255, 0), highlight_rect, 2)  # Gelber Rand, Dicke 4

def waehle_karteaus(self)->MKarte:
    #Es müssen mindest 1 karte bewegbar sein
    maus = pygame.mouse.get_pos()
    templiste:list[int] =[]


    for i in self.gamelist: #Pythagoras länge der hypotenuse als werkzeug

        pytagoras_a_quadrat = (i.x+i.bild.get_width()/2 - maus[0])**2
        pytagoras_b_quadrat = (i.y+i.bild.get_height()/2- maus[1])**2
        pytagoras_c = (pytagoras_a_quadrat + pytagoras_b_quadrat)**0.5
        templiste.append(pytagoras_c) #sqrt (a^2 +b^2) = c
    if not templiste:
        return None
    indize = indize_waehle_karteaus(self,templiste)
    return self.gamelist[indize]

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
        # delay damit der klick nicht mehrmals gezählt wird
        pygame.time.delay(250)
        feld.state = True
        feld.highlighted= True
        #print(feld.kard_reference.kartenwert, feld.kard_reference.kartentyp)


    # eingabe ist ein Tupel (x,y)

def lege_karte_ab(self,feld):
    if pygame.mouse.get_pressed()[0]:
        self.action_done=True
        pygame.time.delay(250) # delay dami2t der klick nicht mehrmals gezählt wird
        if feld.state == True :
            feld.state = False
            feld.highlighted= False

        #self.waehle_karteaus()

    #def an_karte_legen(self,feld_active:MKarte,feld_passive:MKarte):
def define_movable(self):
    #Es wird überprüft und gesetzt ob man eine karte bewegen kann

    for karte in self.gamelist:
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
