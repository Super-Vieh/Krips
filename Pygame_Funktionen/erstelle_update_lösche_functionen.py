# Funktionen die zu der Klasse GUI gehören - Responsive Version
import pygame
from Pygame_Funktionen.mk_karte import MKarte
from Klassen import Karten, KartenWert, KartenTyp
from Pygame_Funktionen.unterstuezungs_und_navigations_funktionen_ import draw, waehle_karteaus, lege_karte_ab, hebe_karte_auf


def aendere_kartenformat(self, placeholder_bild, neue_breite=None) -> any:
    """Verändert die Karte adequat zur eingegebenen breite (responsive)"""
    if neue_breite is None:
        neue_breite = self.layout.card_width
    neue_hoehe = placeholder_bild.get_height() * neue_breite / placeholder_bild.get_width()
    kleines_bild = pygame.transform.scale(placeholder_bild, (int(neue_breite), int(neue_hoehe)))
    return kleines_bild


def erstelle_spieler_packchen(self):
    """Erstellt die Spieler-Päckchen mit responsiven Positionen"""
    bild = self.placeholder_rueckseite
    for i in range(3):
        index = i
        match (index):
            case 0:
                mache_die_packete(self, bild)
            case 1:
                mache_die_haufen(self, index)
            case 2:
                mache_die_dreizehner(self, index, bild)


def loesche_alle_elemente(self):
    self.gamelist = []


def mache_die_packete(self, bild):
    """Erstellt die normalen Päckchen mit responsiven Positionen"""
    x, y1 = self.layout.get_player_pile_pos(0, 1)
    _, y2 = self.layout.get_player_pile_pos(0, 2)
    
    if self.game.spieler1Paechen:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler1Paechen[-1], x, y1, bild)
        self.gamelist.append(MKarte(self.screen, x, y1, self.placeholder_rueckseite, None))
    else:
        self.gamelist.append(MKarte(self.screen, x, y1, self.plus, None))
        
    if self.game.spieler2Paechen:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler2Paechen[-1], x, y2, bild)
        self.gamelist.append(MKarte(self.screen, x, y2, self.placeholder_rueckseite, None))
    else:
        self.gamelist.append(MKarte(self.screen, x, y2, self.plus, None))


def mache_die_haufen(self, index):
    """Erstellt die Haufen mit responsiven Positionen"""
    x1, y1 = self.layout.get_player_pile_pos(1, 1)
    x2, y2 = self.layout.get_player_pile_pos(1, 2)
    
    if self.game.spieler1Haufen:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler1Haufen[-1], x1, y1)
    else:
        self.gamelist.append(MKarte(self.screen, x1, y1, self.plus, None))
        
    if self.game.spieler2Haufen:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler2Haufen[-1], x2, y2)
    else:
        self.gamelist.append(MKarte(self.screen, x2, y2, self.plus, None))


def mache_die_dreizehner(self, index, bild):
    """Erstellt die Dreizehner-Päckchen mit responsiven Positionen"""
    x1, y1 = self.layout.get_player_pile_pos(2, 1)
    x2, y2 = self.layout.get_player_pile_pos(2, 2)
    
    if self.game.spieler1Dreizehner:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler1Dreizehner[-1], x1, y1, bild)
        self.gamelist.append(MKarte(self.screen, x1, y1, self.placeholder_rueckseite, None))
        
    if self.game.spieler2Dreizehner:
        fuege_karte_der_gamelist_hinzu(self, self.game.spieler2Dreizehner[-1], x2, y2, bild)
        self.gamelist.append(MKarte(self.screen, x2, y2, self.placeholder_rueckseite, None))


def fuege_karte_der_gamelist_hinzu(self, card, x_wert, y_wert, bild=None):
    if not card.karteOffen:
        self.gamelist.append(MKarte(self.screen, x_wert, y_wert, self.placeholder_rueckseite, card))
    else:
        geholtes_bild_liste = kartendarstellungs_listen_funktion(self, card)
        dargestelltes_bild = geholtes_bild_liste[card.kartenwert.value - 1]
        self.gamelist.append(MKarte(self.screen, x_wert, y_wert, dargestelltes_bild, card))


def erstelle_centerlist(self, bild):
    """Erstellt die mittleren/Foundation-Stapel mit responsiven Positionen"""
    for i in range(8):
        x, y = self.layout.get_center_pile_pos(i)
        current_list = self.game.mittlereliste[i]

        if current_list:
            kartendarstellung = kartendarstellungs_listen_funktion(self, current_list[-1])
            geholtes_bild = kartendarstellung[current_list[-1].kartenwert.value - 1]
            self.centerlist.append(MKarte(self.screen, x, y, geholtes_bild, current_list[-1]))
        else:
            self.centerlist.append(MKarte(self.screen, x, y, bild, None))


def erstelle_sidelist(self):
    """Erstellt die seitlichen Stapel mit responsiven Positionen"""
    for i in range(8):
        x, y = self.layout.get_side_pile_pos(i)
        
        if not self.game.platzliste[i]:
            self.gamelist.append(MKarte(self.screen, x, y, self.plus, None))
        else:
            # Display cards in the pile with slight offset for visibility
            it = 0
            for k in self.game.platzliste[i]:
                kartendarstellung = kartendarstellungs_listen_funktion(self, k)
                geholtes_bild = kartendarstellung[k.kartenwert.value - 1]
                
                # Calculate offset based on card width and pile side
                offset = it * (self.layout.card_width // 2)
                card_x = x + (offset if i >= 4 else -offset)
                
                self.gamelist.append(MKarte(self.screen, card_x, y, geholtes_bild, k))
                it += 1


def kartendarstellungs_listen_funktion(self, karte: Karten):
    match (karte.kartentyp.value):
        case "Pik":
            kartendarstellung = self.Kartentypen[0]
        case "Coeur":
            kartendarstellung = self.Kartentypen[1]
        case "Treff":
            kartendarstellung = self.Kartentypen[2]
        case "Karro":
            kartendarstellung = self.Kartentypen[3]
    return kartendarstellung


def initialisierung_der_bilder(self):
    """Lädt und skaliert alle Kartenbilder"""
    # Helper function to load and scale a card image
    def load_card(path):
        img = pygame.image.load(path)
        return aendere_kartenformat(self, img)
    
    # Load all spades
    pik_cards = [
        load_card('Bilder/ace_of_spades2.png'),
        load_card('Bilder/2_of_spades.png'),
        load_card('Bilder/3_of_spades.png'),
        load_card('Bilder/4_of_spades.png'),
        load_card('Bilder/5_of_spades.png'),
        load_card('Bilder/6_of_spades.png'),
        load_card('Bilder/7_of_spades.png'),
        load_card('Bilder/8_of_spades.png'),
        load_card('Bilder/9_of_spades.png'),
        load_card('Bilder/10_of_spades.png'),
        load_card('Bilder/jack_of_spades2.png'),
        load_card('Bilder/queen_of_spades2.png'),
        load_card('Bilder/king_of_spades2.png'),
    ]
    
    # Load all hearts
    coeur_cards = [
        load_card('Bilder/ace_of_hearts.png'),
        load_card('Bilder/2_of_hearts.png'),
        load_card('Bilder/3_of_hearts.png'),
        load_card('Bilder/4_of_hearts.png'),
        load_card('Bilder/5_of_hearts.png'),
        load_card('Bilder/6_of_hearts.png'),
        load_card('Bilder/7_of_hearts.png'),
        load_card('Bilder/8_of_hearts.png'),
        load_card('Bilder/9_of_hearts.png'),
        load_card('Bilder/10_of_hearts.png'),
        load_card('Bilder/jack_of_hearts2.png'),
        load_card('Bilder/queen_of_hearts2.png'),
        load_card('Bilder/king_of_hearts2.png'),
    ]
    
    # Load all clubs
    treff_cards = [
        load_card('Bilder/ace_of_clubs.png'),
        load_card('Bilder/2_of_clubs.png'),
        load_card('Bilder/3_of_clubs.png'),
        load_card('Bilder/4_of_clubs.png'),
        load_card('Bilder/5_of_clubs.png'),
        load_card('Bilder/6_of_clubs.png'),
        load_card('Bilder/7_of_clubs.png'),
        load_card('Bilder/8_of_clubs.png'),
        load_card('Bilder/9_of_clubs.png'),
        load_card('Bilder/10_of_clubs.png'),
        load_card('Bilder/jack_of_clubs2.png'),
        load_card('Bilder/queen_of_clubs2.png'),
        load_card('Bilder/king_of_clubs2.png'),
    ]
    
    # Load all diamonds
    karro_cards = [
        load_card('Bilder/ace_of_diamonds.png'),
        load_card('Bilder/2_of_diamonds.png'),
        load_card('Bilder/3_of_diamonds.png'),
        load_card('Bilder/4_of_diamonds.png'),
        load_card('Bilder/5_of_diamonds.png'),
        load_card('Bilder/6_of_diamonds.png'),
        load_card('Bilder/7_of_diamonds.png'),
        load_card('Bilder/8_of_diamonds.png'),
        load_card('Bilder/9_of_diamonds.png'),
        load_card('Bilder/10_of_diamonds.png'),
        load_card('Bilder/jack_of_diamonds2.png'),
        load_card('Bilder/queen_of_diamonds2.png'),
        load_card('Bilder/king_of_diamonds2.png'),
    ]
    
    # Assign to Kartentypen
    self.Kartentypen.append(pik_cards)
    self.Kartentypen.append(coeur_cards)
    self.Kartentypen.append(treff_cards)
    self.Kartentypen.append(karro_cards)


def definiere_bewegbare_karten(self):
    """Definiert welche Karten bewegbar sind"""
    # Es wird überprüft und gesetzt ob man eine karte bewegen kann
    jointlist = self.gamelist + self.centerlist
    # Hier werden listen deklariert die die erste karte vom Haufen speichern
    haufen1_k = None
    haufen2_k = None
    if self.game.spieler1Haufen: haufen1_k = self.game.spieler1Haufen[0]
    if self.game.spieler2Haufen: haufen2_k = self.game.spieler2Haufen[0]

    for karte in jointlist:
        if karte.picked_up == True:
            karte.bewegbar = False
        # alle karten in der liste von den dargestellten karten
        joint_list_fuer_paeckchen = self.game.platzliste + self.game.spieler1listen + self.game.spieler2listen
        for liste in joint_list_fuer_paeckchen:
            # alle karten in den platzlisten werden überprüft
            if not liste:
                continue

            if karte.kard_reference is liste[-1]:
                karte.bewegbar = True
            if haufen1_k and karte.kard_reference is haufen1_k and self.game.current.spielernummer == 1:
                karte.bewegbar = True
            if haufen2_k and karte.kard_reference is haufen2_k and self.game.current.spielernummer == 2:
                karte.bewegbar = True
