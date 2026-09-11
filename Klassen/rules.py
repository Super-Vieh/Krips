from Klassen import Game, Player, Card, CardValue, CardType, game
from Klassen.move import Move, OriginType, DestinationType


class Rules:
    def __init__(self, game: Game):
        self.game = game
        self.current_player = game.current_player
        self.opposing_player = game.current_player.opponent
    def get_all_valid_moves(self)->list[Move]:
        legal_moves :list[Move] = []
        legal_moves += self.possible_moves_to_tableau()
        legal_moves += self.possible_moves_to_player()
        legal_moves += self.possible_moves_to_foundation()
        legal_moves += self.possible_moves_to_opponent()
        return legal_moves
    def can_end_turn(self) -> bool:
        if self.current_player.player_stock and self.current_player.player_stock[-1].is_face_up== True:
            return True
        else:
            return False
    def possible_moves_to_tableau(self)->list[Move]:
        legal_moves :list[Move] = []
        for origin_list in OriginType:
            match(origin_list):
                case OriginType.PLAYER:
                    legal_player_origins = self.get_legal_player_origins_to_move_a_card()
                    for origin_value in legal_player_origins:
                        legal_moves+= self.possible_tableau_moves_from_origin(OriginType.PLAYER,origin_value)
                case OriginType.TABLEAU:
                    legal_tableau_origins = self.get_legal_tableau_origins_to_move_a_card()
                    for origin_value in legal_tableau_origins:
                        legal_moves+=self.possible_tableau_moves_from_origin(OriginType.TABLEAU, origin_value)
        return legal_moves
    def possible_moves_to_player(self)->list[Move]:
        legal_moves :list[Move] = []
        if self.current_player.player_stock and self.current_player.player_stock[-1].is_face_up== True:
            legal_moves.append(Move(OriginType.PLAYER,0,DestinationType.PLAYER,1))
        if self.current_player.player_stock and self.current_player.player_stock[-1].is_face_up== False:
            legal_moves.append(Move(OriginType.PLAYER,0,DestinationType.PLAYER,0))
        if self.current_player.player_reserve and self.current_player.player_reserve[-1].is_face_up== False:
            legal_moves.append(Move(OriginType.PLAYER,2,DestinationType.PLAYER,2))
        if not self.current_player.player_stock and self.current_player.player_waste:
            legal_moves.append(Move(OriginType.PLAYER,0,DestinationType.PLAYER,0))
        return legal_moves
    def possible_moves_to_foundation(self) -> list[Move]:
        legal_moves: list[Move] = []
        for origin_list in OriginType:
            match (origin_list):
                case OriginType.PLAYER:
                    legal_player_origins = self.get_legal_player_origins_to_move_a_card()
                    for origin_value in legal_player_origins:
                        legal_moves += self.possible_foundation_moves_from_origin(OriginType.PLAYER, origin_value)
                case OriginType.TABLEAU:
                    legal_tableau_origins = self.get_legal_tableau_origins_to_move_a_card()
                    for origin_value in legal_tableau_origins:
                        legal_moves += self.possible_foundation_moves_from_origin(OriginType.TABLEAU, origin_value)
        return legal_moves
    def possible_moves_to_opponent(self) -> list[Move]:
        legal_moves: list[Move] = []
        for origin_list in OriginType:
            match (origin_list):
                case OriginType.PLAYER:
                    legal_player_origins = self.get_legal_player_origins_to_move_a_card()
                    for origin_value in legal_player_origins:
                        legal_moves += self.possible_opponent_moves_from_origin(OriginType.PLAYER, origin_value)
                case OriginType.TABLEAU:
                    legal_tableau_origins = self.get_legal_tableau_origins_to_move_a_card()
                    for origin_value in legal_tableau_origins:
                        legal_moves += self.possible_opponent_moves_from_origin(OriginType.TABLEAU, origin_value)
        return legal_moves
    def possible_opponent_moves_from_origin(self,origin_type:OriginType, origin_value:int) -> list[Move]:
        move_list: list[Move] = []
        if origin_type == OriginType.PLAYER:
            source_pile: list[Card] = self.current_player.player_piles[origin_value]
        else:
            source_pile: list[Card] = self.game.board.tableau[origin_value]

        if not source_pile or not source_pile[-1].is_face_up:
            return move_list
        origin_card: Card = source_pile[-1]

        if self.opposing_player.player_waste:
            top: Card = self.opposing_player.player_waste[-1]
            if (top.value.value in (origin_card.value.value+1, origin_card.value.value-1)
                    and top.card_type == origin_card.card_type):
                move_list.append(Move(origin_type, origin_value, DestinationType.OPPONENT, 0))
        return move_list
    def possible_foundation_moves_from_origin(self,origin_type:OriginType, origin_value:int)->list[Move]:
        move_list: list[Move] = []
        if origin_type == OriginType.PLAYER:
            source_pile: list[Card] = self.current_player.player_piles[origin_value]
        else:
            source_pile: list[Card] = self.game.board.tableau[origin_value]

        if not source_pile or not source_pile[-1].is_face_up:
            return move_list
        origin_card: Card = source_pile[-1]

        #
        for slot in range(0, 8):
            if self.can_play_on_foundation(origin_card, slot):
                move_list.append(Move(origin_type, origin_value, DestinationType.FOUNDATION, slot))
        return move_list

    def possible_tableau_moves_from_origin(self,origin_type:OriginType, origin_value:int)->list[Move]:
        move_list:list[Move] = []
        if origin_type == OriginType.PLAYER:
            source_pile: list[Card] = self.current_player.player_piles[origin_value]
        else:
            source_pile: list[Card] = self.game.board.tableau[origin_value]

        if not source_pile or not source_pile[-1].is_face_up:
            return move_list
        origin_card: Card = source_pile[-1]

        #
        for slot in range(0, 8):
            if self.can_play_on_tableau(origin_card, slot):
                move_list.append(Move(origin_type,origin_value,DestinationType.TABLEAU,slot))
        return move_list




    def can_play_on_tableau(self, card: Card, slot: int) -> bool:
        tableau: list[Card] = self.game.board.tableau[slot]
        if not tableau:
            return True  # leeres Tableau darf belegt werden
        top: Card = tableau[-1]
        return top.value.value == card.value.value + 1 and top.farbe != card.farbe
    def can_play_on_foundation(self, card: Card, slot: int) -> bool:
        foundation: list[Card] = self.game.board.foundations[slot]
        card_type: CardType = None
        match slot:
            case 0 | 1:
                card_type = CardType.Pik
            case 2 | 3:
                card_type = CardType.Coeur
            case 4 | 5:
                card_type = CardType.Treff
            case 6 | 7:
                card_type = CardType.Karro
        if not foundation :
            return card.value == CardValue.ACE and card_type == card.card_type
        top: Card = foundation[-1]
        return top.value.value +1 == card.value.value  and top.card_type == card.card_type

    def get_legal_tableau_origins_to_move_a_card(self):
        origin_value = []
        for index, pile in enumerate(self.game.board.tableau):
            if pile and pile[-1].is_face_up:
                origin_value.append(index)
        return origin_value

    def get_legal_player_origins_to_move_a_card(self)->list[int]:
        origin_value= []
        if self.current_player.player_stock and self.current_player.player_stock[-1].is_face_up== True:
            origin_value.append(0)
        if ((len(self.current_player.player_stock)==0 or self.current_player.player_stock[-1].is_face_up==False)
            and (len(self.current_player.player_waste)!=0)):
            origin_value.append(1)
        if self.current_player.player_reserve and self.current_player.player_reserve[-1].is_face_up== True:
            origin_value.append(2)
        if 0 in origin_value and 1 in origin_value:
            raise ValueError("Illegal Situaltion")
        return origin_value

    def could_be_krips(self):
        if self.possible_moves_to_foundation():
            return True
        else:
            return False

    def move_is_krips(self,move:Move)->bool:
        possible_moves = self.possible_moves_to_foundation()
        if self.game.would_be_krips and possible_moves:
            tableau_exists = False
            for possible_move in possible_moves:
                if possible_move.origin_type == OriginType.TABLEAU: tableau_exists = True
            if move.origin_type == OriginType.PLAYER and tableau_exists:
                return True
            else:
                return False
        return False

