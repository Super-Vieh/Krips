import pygame

from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
from Pygame_Funktionen import MKarte
from Pygame_Funktionen import erstelle_sidelist,erstelle_centerlist,erstelle_spieler_packchen,initialisierung_der_bilder,loesche_alle_elemente
from Pygame_Funktionen import finde_die_ursprungsliste,aendere_kartenformat,draw,waehle_karteaus,indize_waehle_karteaus,lege_karte_ab,hebe_karte_auf,definiere_bewegbare_karten,setze_karte_auf_den_zeiger


# Die Klasse GUI ist das Graphical User Interface des Spieles. Das Ziel dieses ist keine Funktionen zum Spiel hinzufügen
# sondern nur die Inputs des Nutzers an die Klasse Spiel und Spieler weiterzugeben.
# Es gibt den Zustand des Spieles wieder und ist im Grunde eine Glorifizierte eingabe konsole.
# Jede Aktion die hier getätig wird, wird in ein String kovertiert und in die Haupt logik eingespeist.


class ResponsiveLayout:
    """Handles responsive layout calculations based on window size"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.update_dimensions()
    
    def update_dimensions(self):
        """Calculate all responsive dimensions based on screen size"""
        # Card dimensions (relative to screen size)
        self.card_width = int(self.screen_width * 0.048)  # ~75px at 1540px width
        self.card_height = int(self.card_width * 1.4)  # Maintain aspect ratio
        
        # Margins and spacing
        self.margin_top = int(self.screen_height * 0.032)  # ~25px at 790px height
        self.margin_bottom = int(self.screen_height * 0.829)  # ~655px at 790px height
        self.spacing_horizontal = int(self.screen_width * 0.117)  # ~180px at 1540px
        
        # Player piles area (left side)
        self.player_piles_x = int(self.screen_width * 0.373)  # ~575px at 1540px
        self.player1_y = self.margin_top
        self.player2_y = self.margin_bottom
        
        # Side piles (left and right columns)
        self.left_column_x = int(self.screen_width * 0.390)  # ~600px at 1540px
        self.right_column_x = int(self.screen_width * 0.584)  # ~900px at 1540px
        self.side_pile_spacing = int(self.screen_height * 0.168)  # ~133px at 790px height
        self.side_pile_start_y = int(self.screen_height * 0.177)  # ~140px at 790px height
        
        # Center piles (middle area)
        self.center_left_x = int(self.screen_width * 0.455)  # ~700px at 1540px
        self.center_right_x = int(self.screen_width * 0.519)  # ~800px at 1540px
        self.center_start_y = int(self.screen_height * 0.177)  # ~140px at 790px height
        self.center_spacing = int(self.screen_height * 0.070)  # ~54px + 12.5px spacing
        
        # Krips button dimensions
        self.button_width = int(self.screen_width * 0.065)  # ~100px at 1540px
        self.button_height = int(self.card_height)
    
    def get_player_pile_pos(self, pile_index: int, player: int) -> tuple:
        """Get position for player piles (0=Paechen, 1=Haufen, 2=Dreizehner)"""
        x = self.player_piles_x + (pile_index * self.spacing_horizontal)
        y = self.player1_y if player == 1 else self.player2_y
        return (int(x), int(y))
    
    def get_side_pile_pos(self, pile_index: int) -> tuple:
        """Get position for side piles (0-7)"""
        if pile_index < 4:
            x = self.left_column_x
            y = self.side_pile_start_y + (pile_index * self.side_pile_spacing)
        else:
            x = self.right_column_x
            y = self.side_pile_start_y + ((pile_index - 4) * self.side_pile_spacing)
        return (int(x), int(y))
    
    def get_center_pile_pos(self, pile_index: int) -> tuple:
        """Get position for center/foundation piles (0-7)"""
        # Alternating left/right columns
        x = self.center_left_x if pile_index % 2 == 0 else self.center_right_x
        y = self.center_start_y + ((pile_index // 2) * self.center_spacing)
        return (int(x), int(y))
    
    def get_krips_button_pos(self, player: int) -> pygame.Rect:
        """Get Krips button rectangle for player"""
        x = int(self.screen_width * 0.260)  # ~400px at 1540px
        y = self.margin_top if player == 1 else self.margin_bottom
        return pygame.Rect(x, y, self.button_width, self.button_height)


class GUI:
    def __init__(self, game: Spiel, width: int = 1540, height: int = 790):
        pygame.init()
        self.run = True
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Krips - Zank-Patience")
        
        # Layout calculator
        self.layout = ResponsiveLayout(self.width, self.height)
        
        # Game state
        self.movable_cards: list[MKarte] = []
        self.centerlist: list[MKarte] = []
        self.gamelist: list[MKarte] = []
        self.movable_list: list[MKarte] = []
        self.game = game
        self.Kartentypen = []
        self.action_done = False
        
        # Load and scale images
        self.placeholder_rueckseite = pygame.image.load('Bilder/Placeholder.png')
        self.placeholder_rueckseite = self.scale_card_image(self.placeholder_rueckseite)
        self.plus = pygame.image.load('Bilder/Plus.png')
        self.plus = self.scale_card_image(self.plus, int(self.layout.card_width * 0.67))
        
        self.current_card = None

    def scale_card_image(self, image: pygame.Surface, width: int = None) -> pygame.Surface:
        """Scale card image to responsive size"""
        if width is None:
            width = self.layout.card_width
        height = int(image.get_height() * width / image.get_width())
        return pygame.transform.scale(image, (width, height))
    
    def handle_resize(self):
        """Handle window resize event"""
        self.width, self.height = self.screen.get_size()
        self.layout = ResponsiveLayout(self.width, self.height)
        
        # Rescale images
        self.placeholder_rueckseite = pygame.image.load('Bilder/Placeholder.png')
        self.placeholder_rueckseite = self.scale_card_image(self.placeholder_rueckseite)
        self.plus = pygame.image.load('Bilder/Plus.png')
        self.plus = self.scale_card_image(self.plus, int(self.layout.card_width * 0.67))
        
        # Reload all card images at new size
        self.Kartentypen = []
        self.initialisierung_der_bilder()
        
        # Recreate all card positions
        self.action_done = True

    def image(self):
        initialisierung_der_bilder(self)
        erstelle_centerlist(self, self.plus)
        erstelle_sidelist(self)
        erstelle_spieler_packchen(self)

        self.screen.fill((30, 31, 34))
        draw(self, self.gamelist)
        draw(self, self.centerlist)
        self.reset()
        pygame.display.update()
        
    def instance(self):
        initialisierung_der_bilder(self)

        self.game.game_first_move()

        erstelle_centerlist(self, self.plus)
        erstelle_sidelist(self)
        erstelle_spieler_packchen(self)
        
        clock = pygame.time.Clock()
        
        while self.run:
            self.screen.fill((30, 31, 34))  # Alles muss nach dem fill kommen sonst wird es nicht angezeigt

            definiere_bewegbare_karten(self)

            if self.game.spieler1.anderreihe == True: self.game.current = self.game.spieler1
            elif self.game.spieler2.anderreihe == True: self.game.current = self.game.spieler2

            # Utilize Play ist eine Funktion welche die Funktion Play der Klasse Spiel durchführt.
            self.nutze_play()

            draw(self, self.gamelist)
            draw(self, self.centerlist)

            krips_knoepfe = self.erstelle_knopf()
            for button in krips_knoepfe:
                pygame.draw.rect(self.screen, (255, 0, 0), button)

            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.circle(self.screen, (255, 0, 0), mouse_pos, 5)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize()

                self.rufe_krips(event, krips_knoepfe)
                
            pygame.display.update()
            clock.tick(60)  # 60 FPS

    def nutze_play(self):
        # Hier wird die Funktion Play() der Klasse Spiel durchgeführt

        temp = waehle_karteaus(self)
        if not temp: return None
        if temp.picked_up == False:
            hebe_karte_auf(self, temp)

        elif temp.picked_up == True:
            # print(temp.kard_reference.kartenwert, temp.kard_reference.kartentyp)
            ergebniss_string = lege_karte_ab(self)
            if ergebniss_string:
                self.game.play(ergebniss_string)
        setze_karte_auf_den_zeiger(self)
        self.reset()

    def reset(self):
        # Es löscht alle Elemente auf dem Bildschirm und erstellt neue nach dem gamestate.
        if self.action_done == True:  # action_done hat keinen bezug zu dem hier in der funktion
            loesche_alle_elemente(self)
            erstelle_spieler_packchen(self)
            erstelle_sidelist(self)
            erstelle_centerlist(self, self.plus)
            self.action_done = False

    def erstelle_knopf(self):
        # Der Krips Button wird erstellt
        button_rects = [
            self.layout.get_krips_button_pos(1),  # Player 1 (top)
            self.layout.get_krips_button_pos(2)   # Player 2 (bottom)
        ]
        return button_rects
        
    def rufe_krips(self, event, knoepfe_liste):
        # Die interaktion mit dem Krips Button wird hier gesteuert
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect in knoepfe_liste:
                if rect.collidepoint(event.pos):
                    self.game.play("K")
    
    def initialisierung_der_bilder(self):
        """Load and scale all card images"""
        # This method should be called from the module function
        # but we need to access it for rescaling
        pass
