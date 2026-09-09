from .card import Card


class Board:
    def __init__(self) -> None:
        self.pik1: list[Card] = []
        self.pik2: list[Card] = []
        self.coeur1: list[Card] = []
        self.coeur2: list[Card] = []
        self.treff1: list[Card] = []
        self.treff2: list[Card] = []
        self.karro1: list[Card] = []
        self.karro2: list[Card] = []
        self.foundations: list[list[Card]] = [self.pik1, self.pik2, self.coeur1, self.coeur2, self.treff1, self.treff2, self.karro1,
                            self.karro2]
        # Seitenlisten
        self.tableau1: list[Card] = []
        self.tableau2: list[Card] = []
        self.tableau3: list[Card] = []
        self.tableau4: list[Card] = []
        self.tableau5: list[Card] = []
        self.tableau6: list[Card] = []
        self.tableau7: list[Card] = []
        self.tableau8: list[Card] = []
        self.tableau: list[list[Card]] = [self.tableau1, self.tableau2, self.tableau3, self.tableau4, self.tableau5, self.tableau6,
                        self.tableau7,
                        self.tableau8]