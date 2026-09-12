
from enum import Enum

class OriginType(Enum):
    PLAYER= "player"
    TABLEAU = "tableau"


class DestinationType(Enum):
    PLAYER = "player"
    TABLEAU = "tableau"
    FOUNDATION = "foundation"
    OPPONENT = "opponent"



class Move:
    def __init__(self, origin: OriginType,origin_value:int, destination: DestinationType,destination_value:int):
        self.origin_type: OriginType = origin
        self.origin_value: int = origin_value
        self.destination_type: DestinationType = destination
        self.destination_value: int=destination_value

    def __eq__(self, other_move: object) -> bool:
        if not isinstance(other_move, Move):
            return NotImplemented
        return (self.origin_type == other_move.origin_type
                and self.origin_value == other_move.origin_value
                and self.destination_type == other_move.destination_type
                and self.destination_value == other_move.destination_value)

    def __hash__(self) -> int:
        return hash((self.origin_type, self.origin_value,
                     self.destination_type, self.destination_value))
    def __post_init__(self) -> None:

        match self.origin_type:
            case OriginType.PLAYER:
                allowed_origin = [i for i in range(0,3)]
            case OriginType.TABLEAU:
                allowed_origin = [i for i in range(0,8)]
            case _:
                raise ValueError("Irgendwas ist Falsch")
        if self.origin_value not in allowed_origin:
            raise ValueError("Illegaler Move")

        match self.destination_type:
            case DestinationType.PLAYER:
                allowed_dest = [i for i in range(0,3)]
            case DestinationType.TABLEAU:
                allowed_dest = [i for i in range(0,8)]
            case DestinationType.FOUNDATION:
                allowed_dest = [i for i in range(0,8)]
            case DestinationType.OPPONENT:
                allowed_dest = {0}
            case _:
                raise ValueError("Irgendwas ist Falsch")
        if self.destination_value not in allowed_dest:
            raise ValueError("Illegaler Move")
