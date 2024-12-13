import pygame

from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init,initialize_paechen
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert

class MKarte:

    def __init__(self,screen:any,x:int,y:int,bild:any,kard_reference:Karten):
        self.x = x
        self.y = y
        self.bild = bild
        self.screen = screen
        self.state = False # 0 = nicht ausgewaehlt, 1 = ausgewaehlt
        self.bewegbar= False
        self.highlighted = False
        self.kard_reference:Karten = kard_reference#

#Todo
# schreibe eine Funktion welche die Spieler päckchen positioniert
# schreibe eine Funktion die die karten dynamik des aufdeckens erlaubt / konflikt mit karte aufheben
# schreibe eine funktion die die karten korrekt darstellt offen zu
# kreire immaginäre felder 1/2 der x achse nach links oder nach rechts von der Letzen karte der liste
# schreibe eine weitere funktion die die Karten nur auf diese immaginären felder legen lässt
# Implementier die Spiel regeln



class GUI:
    def __init__(self,game:Spiel):
        pygame.init()
        self.run = True
        self.screen =pygame.display.set_mode((1540,  790))
        self.movable_cards:list[MKarte]= []
        self.centerlist = []
        self.sidelist = []
        self.playerlist = []
        self.game = game
        self.Kartentypen = []

    def create_player_packages(self,bild):
        for i in range(0,3):#geht von 0 bis 2
            index = i   #index geht von 1 bis 3
            x_wert = 575 #index * 180
            y_wert1 = 25
            y_wert2 = 655
            match(index):
                case 0:
                        if self.game.spieler1Paechen[-1].karteOffen == False:
                           self.playerlist.append(MKarte(self.screen,x_wert, y_wert1, bild, self.game.spieler1Paechen[-1]))# Bild ist der Placeholder
                        if self.game.spieler2Paechen[-1].karteOffen == False:
                            self.playerlist.append(MKarte(self.screen, 575, y_wert2, bild, self.game.spieler2Paechen[-1]))# Bild ist der Placeholder

                case 1:
                        if not self.game.spieler1Haufen:
                            pass
                        if not self.game.spieler2Haufen:
                            pass


                case 2:
                        print("test")
                        if self.game.spieler1Dreizehner[-1].karteOffen == True:
                            geholtes_bild_liste = self.match_funktion(self.game.spieler1Dreizehner[-1])
                            dargestelltes_bild = geholtes_bild_liste[self.game.spieler1Dreizehner[-1].kartenwert.value-1]
                            self.playerlist.append(MKarte(self.screen, x_wert+index*180, y_wert1, dargestelltes_bild, self.game.spieler1Dreizehner[-1]))# Bild muss ersetzt werden durch erste karte
                        if self.game.spieler2Dreizehner[-1].karteOffen == True:
                            geholtes_bild_liste = self.match_funktion(self.game.spieler2Dreizehner[-1])
                            dargestelltes_bild = geholtes_bild_liste[self.game.spieler2Dreizehner[-1].kartenwert.value-1]
                            self.playerlist.append(MKarte(self.screen, x_wert+index*180, y_wert2, dargestelltes_bild, self.game.spieler2Dreizehner[-1]))# Bild muss ersetzt werden durch erste karte

    def create_centerlist(self,bild): # ist dazu da die ersten 8 pluse in die mitte zu legen
        # Muss noch überprüft werden ob die karten richtig gelegt werden

        for i in range(1,5):
            kartendarstellung:any  = bild
            k = Karten(KartenTyp.Pik,KartenWert.Ass)
            if len(self.game.mittlereliste) == 0 or len(self.game.mittlereliste[i-1]) == 0:

                x_wert = 720
                y_wert = i * bild.get_height()*2 +i*25
                self.centerlist.append(MKarte(self.screen, x_wert, y_wert +25, bild,k))
                continue

            for k in self.game.mittlereliste[i-1]:# für jedekarte in derMittlereliste

                kartendarstellung= self.match_funktion(k)
                geholtes_bild =  kartendarstellung[k.kartenwert.value-1]

                x_wert = 720
                y_wert = i * bild.get_height()*2 +i*25 # keine ahnung warum mal 2. i*25 ist der abstand zwischen den karten

            self.centerlist.append(MKarte(self.screen, x_wert, y_wert +25 , geholtes_bild,k))

        for i in range(1,5):

            #wenn keine karte liegt wird der Placeholder plaziert
            if len(self.game.mittlereliste) == 0 or len(self.game.mittlereliste[i+4-1]) == 0:

                x_wert = 820
                y_wert = i * bild.get_height()*2 +i*25 # keine ahnung warum mal 2. i*25 ist der abstand zwischen den karten

                self.centerlist.append(MKarte(self.screen, x_wert, y_wert +25 , bild,k))
                continue

            for k in self.game.mittlereliste[i+4-1]:
                kartendarstellung= self.match_funktion(k)
                geholtes_bild =  kartendarstellung[k.kartenwert.value-1]

            x_wert = 820
            y_wert= i * bild.get_height()*2 +i*25

            self.centerlist.append(MKarte(self.screen, 820, y_wert +25,geholtes_bild,k))

    def create_sidelist(self,bild):
        kartendarstellung:any  = bild
        for i in range(0, 4):
            it = 0
            for k in self.game.platzliste[i]:  # für jede Karte in der Kartenliste
                # Wird überprüft, welcher Liste die Karte gehört
                kartendarstellung = self.match_funktion(k)
                geholtes_bild = kartendarstellung[k.kartenwert.value - 1]

                temp = self.centerlist[i]
                y_wert = temp.y
                x_wert = temp.x - 100 - it * bild.get_width() / 2  # Bild ist der Placeholder und wird als Formatierungsvorlage genutzt

                self.sidelist.append(MKarte(self.screen, x_wert, y_wert, geholtes_bild, k))
                it += 1
        for i in range(4, 8):
            it =0
            for k in self.game.platzliste[i]:# für jedekarte in der kartenliste

                #wird überprüft welcher zu liste die karte gehört
                kartendarstellung= self.match_funktion(k)
                geholtes_bild =  kartendarstellung[k.kartenwert.value-1]

                temp = self.centerlist[i]
                y_wert = temp.y
                x_wert = temp.x + 100 +it * bild.get_width()/2   # Bild ist der Placeholder und wird als formatierungsvorlage genutzt


                #hier wird die aus der match funktion genommene liste genutzt
                self.sidelist.append(MKarte(self.screen, x_wert, y_wert, geholtes_bild,k))
                it +=1

    def match_funktion(self, karte:Karten):
        match(karte.kartentyp.value): #  wird geschaut aus welcher liste die bilder genommenwerden sollen
            case ("Pik"):
                kartendarstellung= self.Kartentypen[0]
            case ("Coeur"):
                kartendarstellung= self.Kartentypen[1]
            case ("Treff"):
                kartendarstellung= self.Kartentypen[2]
            case ("Karro"):
                kartendarstellung= self.Kartentypen[3]

        return kartendarstellung



    def instance(self):

        placeholder_rueckseite = pygame.image.load('Bilder/Placeholder.png')
        placeholder_rueckseite = self.sizeofkards(placeholder_rueckseite)# ändert die größe zu einer vorherbestimmten größe
        plus=pygame.image.load('Bilder/Plus.png')
        plus=self.sizeofkards(plus,50)
        self.initate_cards()




        destination = (100, 100)
        destination2 = (200, 200)
        #feld1:MKarte =MKarte(self.screen, 0, 0, placeholder_rueckseite)
        #feld2:MKarte =MKarte(self.screen, 200, 500, plus,
        #self.movable_cards.append(feld1)
        #self.movable_cards.append(feld2)
        self.create_centerlist(plus)
        self.create_sidelist(placeholder_rueckseite)
        self.create_player_packages(placeholder_rueckseite)
        self.initate_cards()
        while self.run:
            self.screen.fill((30, 31, 34)) #Alles muss nach dem fill kommen sonst wird es nicht angezeigt


            self.define_movable()
            self.draw(self.centerlist)
            self.draw(self.sidelist)
            self.draw(self.playerlist)
            temp = self.waehle_karteaus()

            if temp.state == False:
                self.hebe_karte_auf(temp)
            elif temp.state == True:
                print(temp.kard_reference.kartenwert, temp.kard_reference.kartentyp)
                self.lege_karte_ab(temp)
            self.set_card_at_center(temp)



            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            pygame.display.update()




    def untilize_play(self):
        action: str = input(f"\nSpieler{self.game.current.spielernummer} ist drann."
                                 "\nWas soll gemacht werden?\n"
                                 "Karte aufdecken = A0 oder A2\n"  # Aufgedeckt werden können nur Päckchen und Dreizehner 
                                 "Karte hilegen = (A0-2,S1-8,)M1-8*S1-8*G0\n"
                                 "Runde Aufhören= P,Kartenhaufen umdrehen = R\n")
        self.game.play(action)
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

        joint_list = self.sidelist+self.playerlist
        for i in joint_list: #Pythagoras länge der hypotenuse als werkzeug
              if i.bewegbar == True:
                pytagoras_a_quadrat = (i.x+i.bild.get_width()/2 - maus[0])**2
                pytagoras_b_quadrat = (i.y+i.bild.get_height()/2- maus[1])**2
                pytagoras_c = (pytagoras_a_quadrat + pytagoras_b_quadrat)**0.5
                templiste.append(pytagoras_c) #sqrt (a^2 +b^2) = c
        if not templiste:
            return None
        indize = self.indize_waehle_karteaus(templiste)
        return joint_list[indize]
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
        if  feld.state== True:
            eingabe = pygame.mouse.get_pos()
            feld.x = eingabe[0]-feld.bild.get_width()/2 # setzt die Position der Karte zu der Mitter der Maus
            feld.y = eingabe[1]-feld.bild.get_height()/2


    def hebe_karte_auf(self, feld):
        #print(feld.kard_reference.kartenwert, feld.kard_reference.kartentyp)
        if feld == None:
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
            pygame.time.delay(250) # delay damit der klick nicht mehrmals gezählt wird
            if feld.state == True :
                feld.state = False
                feld.highlighted= False
            #elif feld.bewegbar:
            #   feld.state = True

    def define_movable(self):
        #Es wird überprüft und gesetzt ob man eine karte bewegen kann
            joint_list = self.sidelist+self.playerlist
            for karte in joint_list:
                if karte.state == True:
                    return None
                    #soll schauen ob eine Karte hochgehoben ist und wenn ja wird der define movable a
                    #erst wenn die karte wieder runtergelegt wird kann eine nächste karte hochgehoben werden bzw.
                    #ist noch nicht kontroliert ob es wirklich funktioniert
                #alle karten in der liste von den dargestellten karten
                joint_list_fuer_paeckchen = self.game.platzliste+self.game.spieler1listen+self.game.spieler2listen
                for liste in joint_list_fuer_paeckchen:
                    #alle karten in den platzlisten werden überprüft
                    if not liste:
                        continue
                    if karte.kard_reference is liste[-1]:
                        karte.bewegbar = True

                    #else:
                     #   karte.bewegbar = False
    def initate_cards(self):
        placeholder_rueckseite = pygame.image.load('Bilder/Placeholder.png')
        placeholder_rueckseite = self.sizeofkards(placeholder_rueckseite)# ändert die größe zu einer vorherbestimmten größe

        pik2 = pygame.image.load('Bilder/2_of_spades.png')
        pik2 = self.sizeofkards(pik2)
        couer2 = pygame.image.load('Bilder/2_of_hearts.png')
        couer2 = self.sizeofkards(couer2)
        treff2 = pygame.image.load('Bilder/2_of_clubs.png')
        treff2 = self.sizeofkards(treff2)
        karro2 = pygame.image.load('Bilder/2_of_diamonds.png')
        karro2 = self.sizeofkards(karro2)

        pik3 = pygame.image.load('Bilder/3_of_spades.png')
        pik3 = self.sizeofkards(pik3)
        couer3 = pygame.image.load('Bilder/3_of_hearts.png')
        couer3 = self.sizeofkards(couer3)
        treff3 = pygame.image.load('Bilder/3_of_clubs.png')
        treff3 = self.sizeofkards(treff3)
        karro3 = pygame.image.load('Bilder/3_of_diamonds.png')
        karro3 = self.sizeofkards(karro3)

        pik4 = pygame.image.load('Bilder/4_of_spades.png')
        pik4 = self.sizeofkards(pik4)
        couer4 = pygame.image.load('Bilder/4_of_hearts.png')
        couer4 = self.sizeofkards(couer4)
        treff4 = pygame.image.load('Bilder/4_of_clubs.png')
        treff4 = self.sizeofkards(treff4)
        karro4 = pygame.image.load('Bilder/4_of_diamonds.png')
        karro4 = self.sizeofkards(karro4)

        pik5 = pygame.image.load('Bilder/5_of_spades.png')
        pik5 = self.sizeofkards(pik5)
        couer5 = pygame.image.load('Bilder/5_of_hearts.png')
        couer5 = self.sizeofkards(couer5)
        treff5 = pygame.image.load('Bilder/5_of_clubs.png')
        treff5 = self.sizeofkards(treff5)
        karro5 = pygame.image.load('Bilder/5_of_diamonds.png')
        karro5 = self.sizeofkards(karro5)

        pik6 = pygame.image.load('Bilder/6_of_spades.png')
        pik6 = self.sizeofkards(pik6)
        couer6 = pygame.image.load('Bilder/6_of_hearts.png')
        couer6 = self.sizeofkards(couer6)
        treff6 = pygame.image.load('Bilder/6_of_clubs.png')
        treff6 = self.sizeofkards(treff6)
        karro6 = pygame.image.load('Bilder/6_of_diamonds.png')
        karro6 = self.sizeofkards(karro6)

        pik7 = pygame.image.load('Bilder/7_of_spades.png')
        pik7 = self.sizeofkards(pik7)
        couer7 = pygame.image.load('Bilder/7_of_hearts.png')
        couer7 = self.sizeofkards(couer7)
        treff7 = pygame.image.load('Bilder/7_of_clubs.png')
        treff7 = self.sizeofkards(treff7)
        karro7 = pygame.image.load('Bilder/7_of_diamonds.png')
        karro7 = self.sizeofkards(karro7)

        pik8 = pygame.image.load('Bilder/8_of_spades.png')
        pik8 = self.sizeofkards(pik8)
        couer8 = pygame.image.load('Bilder/8_of_hearts.png')
        couer8 = self.sizeofkards(couer8)
        treff8 = pygame.image.load('Bilder/8_of_clubs.png')
        treff8 = self.sizeofkards(treff8)
        karro8 = pygame.image.load('Bilder/8_of_diamonds.png')
        karro8 = self.sizeofkards(karro8)

        pik9 = pygame.image.load('Bilder/9_of_spades.png')
        pik9 = self.sizeofkards(pik9)
        couer9 = pygame.image.load('Bilder/9_of_hearts.png')
        couer9 = self.sizeofkards(couer9)
        treff9 = pygame.image.load('Bilder/9_of_clubs.png')
        treff9 = self.sizeofkards(treff9)
        karro9 = pygame.image.load('Bilder/9_of_diamonds.png')
        karro9 = self.sizeofkards(karro9)

        pik10 = pygame.image.load('Bilder/10_of_spades.png')
        pik10 = self.sizeofkards(pik10)
        couer10 = pygame.image.load('Bilder/10_of_hearts.png')
        couer10 = self.sizeofkards(couer10)
        treff10 = pygame.image.load('Bilder/10_of_clubs.png')
        treff10 = self.sizeofkards(treff10)
        karro10 = pygame.image.load('Bilder/10_of_diamonds.png')
        karro10 = self.sizeofkards(karro10)

        pik11 = pygame.image.load('Bilder/Jack_of_spades2.png')
        pik11 = self.sizeofkards(pik11)
        couer11 = pygame.image.load('Bilder/Jack_of_hearts2.png')
        couer11 = self.sizeofkards(couer11)
        treff11 = pygame.image.load('Bilder/Jack_of_clubs2.png')
        treff11 = self.sizeofkards(treff11)
        karro11 = pygame.image.load('Bilder/Jack_of_diamonds2.png')
        karro11 = self.sizeofkards(karro11)

        pik12 = pygame.image.load('Bilder/Queen_of_spades2.png')
        pik12 = self.sizeofkards(pik12)
        couer12 = pygame.image.load('Bilder/Queen_of_hearts2.png')
        couer12 = self.sizeofkards(couer12)
        treff12 = pygame.image.load('Bilder/Queen_of_clubs2.png')
        treff12 = self.sizeofkards(treff12)
        karro12 = pygame.image.load('Bilder/Queen_of_diamonds2.png')
        karro12 = self.sizeofkards(karro12)

        pik13 = pygame.image.load('Bilder/King_of_spades2.png')
        pik13 = self.sizeofkards(pik13)
        couer13 = pygame.image.load('Bilder/King_of_hearts2.png')
        couer13 = self.sizeofkards(couer13)
        treff13 = pygame.image.load('Bilder/King_of_clubs2.png')
        treff13 = self.sizeofkards(treff13)
        karro13 = pygame.image.load('Bilder/King_of_diamonds2.png')
        karro13 = self.sizeofkards(karro13)

        pik1 = pygame.image.load('Bilder/Ace_of_spades2.png')
        pik1 = self.sizeofkards(pik1)
        couer1 = pygame.image.load('Bilder/Ace_of_hearts.png')
        couer1 = self.sizeofkards(couer1)
        treff1 = pygame.image.load('Bilder/Ace_of_clubs.png')
        treff1 = self.sizeofkards(treff1)
        karro1 = pygame.image.load('Bilder/Ace_of_diamonds.png')
        karro1 = self.sizeofkards(karro1)

        self.Kartentypen.append([pik1, pik2, pik3, pik4, pik5, pik6, pik7, pik8, pik9, pik10, pik11, pik12, pik13])
        self.Kartentypen.append([couer1, couer2, couer3, couer4, couer5, couer6, couer7, couer8, couer9, couer10, couer11, couer12, couer13])
        self.Kartentypen.append([treff1, treff2, treff3, treff4, treff5, treff6, treff7, treff8, treff9, treff10, treff11, treff12, treff13])
        self.Kartentypen.append([karro1, karro2, karro3, karro4, karro5, karro6, karro7, karro8, karro9, karro10, karro11, karro12, karro13])




