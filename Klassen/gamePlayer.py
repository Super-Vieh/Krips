from .spieler import Spieler,Karten
from .spiel import Spiel,KartenWert, KartenTyp
class GamePlayer():
    def __init__(self,sp1:Spieler,sp2:Spieler,game:Spiel):
        self.sp1 = sp1
        self.sp2 = sp2
        self.game = game

