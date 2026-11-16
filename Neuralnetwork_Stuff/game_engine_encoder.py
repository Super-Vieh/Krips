import numpy as np
from Klassen import Game, Card, CardType
#from Klassen import print_top,print_sidesplus,print_bot

class GameEngineEncoder:
    @staticmethod
    def encode_states(game: Game) -> np.ndarray:
        """
        SPIELER 1:
        [0:52]     -> Spieler 1 Päckchen (Handkarten)
        [52:104]   -> Spieler 1 Haufen (Ablagestapel)
        [104:156]  -> Spieler 1 Dreizehner

        SPIELER 2:
        [156:208]  -> Spieler 2 Päckchen (Handkarten)
        [208:260]  -> Spieler 2 Haufen (Ablagestapel)
        [260:312]  -> Spieler 2 Dreizehner

        SPIELFELD Seitenplätze:
        [312:728]  -> Platzliste 8 Listen * 52
        (z.B. Platz 1 ist 312:364, Platz 2 ist 364:416, ...)

        SPIELFELD Mitte:
        [728:1144] -> Mittelliste 8 Listen * 52
        """

        states: list = []
        spieler_listen: list[list[Card]] = []
        # spielerfeld listen is a list of all list that are on the playing field.
        # it is a list of lists and so are platzliste and mittlereliste. they can be added
        spielfeld_listen: list[list[Card]] = game.board.tableau + game.board.foundations

        # spieler listen is a list of all lists that belong to the players the list itself is also a list of list
        # but the game.player1 and game.player2 list are only simple lists
        spieler_listen.append(game.player1.player_stock)
        spieler_listen.append(game.player1.player_waste)
        spieler_listen.append(game.player1.player_reserve)

        spieler_listen.append(game.player2.player_stock)
        spieler_listen.append(game.player2.player_waste)
        spieler_listen.append(game.player2.player_reserve)

        i: int = 0
        for list in spieler_listen + spielfeld_listen:
            i += 1
            states += GameEngineEncoder.transform_to_52bitvektor(list)
        return np.array(states, dtype=np.int8)
    @staticmethod
    def transform_to_52bitvektor(list: list[Card]) -> list[int]:
        dict_suit: dict[CardType, int] = {
            CardType.Pik: 0,
            CardType.Coeur: 1,
            CardType.Treff: 2,
            CardType.Karro: 3
        }
        empty_list: list[int] = [0] * 52
        if not list:  # wenn die liste kein element hat wird ein voller 0 vektor zurückgegeben
            return empty_list
        for card in list:
            if card.is_face_up == False and list[-1].is_face_up == False:
                # wenn die Karte nicht offen ist, dann wird sie nicht in den Vektor aufgenommen
                # das list[-1] ist für doe spielerlisten da dort die letze karte die erste ist
                break
            if card.is_face_up == False:
                # wenn die Karte nicht offen ist, dann wird sie nicht in den Vektor aufgenommen
                # die zweite überprüfung is notwending da im ersten if auf eine kombination
                continue
            mult: int = dict_suit[card.card_type]
            empty_list[(mult * 13) + card.card_rank.value - 1] = 1
            # der intex wird berechnet durch die art von Karte 0-3 und den Wert1-13

        return empty_list