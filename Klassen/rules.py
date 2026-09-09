from sympy import true

from Klassen import Game, Player, Card
from Klassen.move import Move, OriginType


class Rules:
    def init(self, game: Game):
        self.game = game
        self.current_player = game.current_player
        self.opposing_player = game.current_player.opponent

    def can_end_turn(self) -> bool:
        if self.current_player.player_stock[-1].is_face_up== True:
            return True
        else:
            return False
    def possible_moves_to_tableau(self)->list[Move]:
        for origin_list in OriginType:
            match(origin_list):
                case OriginType.PLAYER:
                    legal_player_origins = self.get_legal_player_origins_to_move_a_card()
                    for origin_value in legal_player_origins:
                        self.possible_tableau_moves_from_origin(OriginType.PLAYER,origin_value)



    def get_legal_player_origins_to_move_a_card(self):
        origin_value= []
        if self.current_player.player_stock[-1] and self.current_player.player_stock[-1].is_face_up== True:
            origin_value.append(0)
        if ((len(self.current_player.player_stock)==0 or self.current_player.player_stock[-1].is_face_up==False)
            and (len(self.current_player.player_waste)!=0)):
            origin_value.append(1)
        if self.current_player.player_reserve and self.current_player.player_reserve[-1].is_face_up== True:
            origin_value.append(2)
        if 0 in origin_value and 1 in origin_value:
            raise ValueError("Illegal Situaltion")
        return origin_value

    def possible_tableau_moves_from_origin(self,origin_type:OriginType, origin_value:int)->list[Move]:
        move_list:list[Move] = []
        if origin_type == OriginType.PLAYER:
            for slot,list in enumerate(self.game.board.tableau,0):
                if list and list[-1]:
                    self.can_play_on_tableau(list[-1],slot)
                else:
                    move_list.append(Move(origin_type,origin_value,slot))



    def can_play_on_tableau(self, card: Card, slot: int) -> bool:
        tableau: list[Card] = self.game.board.tableau[slot - 1]
        if (tableau[-1].rank.value == card.rank.value + 1 and tableau[-1].farbe != card.farbe):
            return True
        return False

