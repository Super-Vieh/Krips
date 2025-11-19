"""
game_logic.py - Core Game Logic Rules for Krips/Zank-Patience

This module contains the extracted game logic rules and validation functions.
These rules are separated from the game state and visualization to allow
easier debugging and testing.

GAME RULES SUMMARY:
==================
Krips (Zank-Patience/Russian Bank/Crapette) is a competitive patience game for two players.

OBJECTIVE:
- Be the first to play all your cards
- Build 8 foundation piles in the middle (2 of each suit: Spades, Hearts, Clubs, Diamonds)
- Foundation piles build from Ace to King of the same suit

PRIORITY RULES:
- Cards MUST be played to the center/foundation piles (mittlere piles) when possible
- Failure to do so allows opponent to call "Krips" and take the turn

CARD AREAS:
1. Middle/Foundation Piles (mittlereliste): 8 piles, must start with Ace, build up same suit
2. Side Piles (platzliste): 8 piles, build down alternating colors (like Solitaire)
3. Player Piles: Each player has 3 piles:
   - Normal Package (Paechen): Draw pile
   - Waste Pile (Haufen): Discard pile
   - Thirteen Pile (Dreizehner): Special 13-card pile at game start

BUGS/ISSUES FOUND:
==================
1. Line 189 in spiel.py: typo - self.spieler1listen instead of self.spieler2listen for player 2
2. Krips detection may not catch all cases where a card could be played to center
3. Stalemate detection only checks package lengths, not actual playability
4. Assignment operators used instead of equality in wegen_krips_aufhoeren (lines 183, 184, 189, 190 in spieler.py)
5. No validation that drawn cards are within deck bounds
"""

from typing import Tuple, List, Optional
from Klassen.karten import Karten, KartenTyp, KartenWert


class GameRules:
    """Encapsulates all game rule validation logic"""
    
    @staticmethod
    def kann_mitte_hinlegen(karte: Karten, mittlere_liste: List[Karten], stelle: int) -> bool:
        """
        Check if a card can be played to a middle/foundation pile.
        
        Args:
            karte: The card to play
            mittlere_liste: The target foundation pile
            stelle: Position (1-8) indicating which foundation pile
            
        Returns:
            bool: True if the card can be legally played to this pile
            
        Rules:
            - First card must be an Ace of the correct suit for that position
            - Subsequent cards must be same suit and exactly one value higher
            - Positions 1-2: Spades, 3-4: Hearts, 5-6: Clubs, 7-8: Diamonds
        """
        # If pile is empty, only Aces can be placed
        if len(mittlere_liste) == 0:
            if karte.kartenwert.value != 1:  # Not an Ace
                return False
            # Check if Ace matches the position's suit
            if stelle in [1, 2] and karte.kartentyp != KartenTyp.Pik:
                return False
            if stelle in [3, 4] and karte.kartentyp != KartenTyp.Coeur:
                return False
            if stelle in [5, 6] and karte.kartentyp != KartenTyp.Treff:
                return False
            if stelle in [7, 8] and karte.kartentyp != KartenTyp.Karro:
                return False
            return True
        
        # If pile has cards, check if this card is next in sequence
        top_card = mittlere_liste[-1]
        return (karte.kartentyp == top_card.kartentyp and 
                karte.kartenwert.value == top_card.kartenwert.value + 1)
    
    @staticmethod
    def kann_seite_hinlegen(karte: Karten, seiten_liste: List[Karten]) -> bool:
        """
        Check if a card can be played to a side pile.
        
        Args:
            karte: The card to play
            seiten_liste: The target side pile
            
        Returns:
            bool: True if the card can be legally played
            
        Rules:
            - If pile is empty, any card can be placed
            - Otherwise, card must be one value lower and opposite color
              (like Solitaire)
        """
        if len(seiten_liste) == 0:
            return True
        
        top_card = seiten_liste[-1]
        return (karte.kartenwert.value == top_card.kartenwert.value - 1 and
                karte.farbe != top_card.farbe)
    
    @staticmethod
    def kann_gegner_geben(karte: Karten, gegner_haufen: List[Karten]) -> bool:
        """
        Check if a card can be played to opponent's waste pile.
        
        Args:
            karte: The card to play
            gegner_haufen: Opponent's waste pile
            
        Returns:
            bool: True if the card can be legally played
            
        Rules:
            - Card must be same suit as top card of opponent's waste pile
            - Card value must be exactly 1 higher or 1 lower
        """
        if not gegner_haufen:
            return False
        
        top_card = gegner_haufen[-1]
        return (karte.kartentyp == top_card.kartentyp and
                (karte.kartenwert.value == top_card.kartenwert.value + 1 or
                 karte.kartenwert.value == top_card.kartenwert.value - 1))
    
    @staticmethod
    def ist_krips_moeglich(spieler_listen: List[List[Karten]], 
                          platzliste: List[List[Karten]], 
                          mittlereliste: List[List[Karten]]) -> bool:
        """
        Check if there is a playable card to the foundation (Krips condition).
        
        Args:
            spieler_listen: Player's three piles (Paechen, Haufen, Dreizehner)
            platzliste: The 8 side piles
            mittlereliste: The 8 foundation piles
            
        Returns:
            bool: True if any card can be played to foundation
            
        BUG NOTES:
            - This function should check ALL visible cards from player's piles
              and side piles to see if any can go to the middle
            - Current implementation may not catch all cases
        """
        # Check all non-empty lists that have visible cards
        all_lists = platzliste + spieler_listen
        valid_lists = [liste for liste in all_lists if liste and liste[-1].karteOffen]
        
        for source_list in valid_lists:
            card = source_list[-1]
            
            # Check if card is an Ace (can always start a foundation)
            if card.kartenwert.value == 1:
                return True
            
            # Check if card can be played to any existing foundation pile
            for foundation in mittlereliste:
                if foundation:
                    top_card = foundation[-1]
                    if (card.kartentyp == top_card.kartentyp and
                        card.kartenwert.value == top_card.kartenwert.value + 1):
                        return True
        
        return False
    
    @staticmethod
    def check_win_condition(spieler1_piles: Tuple[List, List, List],
                           spieler2_piles: Tuple[List, List, List]) -> Optional[int]:
        """
        Check if the game has been won.
        
        Args:
            spieler1_piles: (Paechen, Haufen, Dreizehner) for player 1
            spieler2_piles: (Paechen, Haufen, Dreizehner) for player 2
            
        Returns:
            None if game continues
            1 if player 1 wins
            2 if player 2 wins
            
        Rules:
            - A player wins by emptying all their piles
        """
        if all(not pile for pile in spieler1_piles):
            return 1
        if all(not pile for pile in spieler2_piles):
            return 2
        return None
    
    @staticmethod
    def check_stalemate(spieler1_dreizehner: List[Karten],
                       spieler2_dreizehner: List[Karten],
                       stalemate_counter: int) -> Tuple[bool, Optional[int]]:
        """
        Check for stalemate condition.
        
        Args:
            spieler1_dreizehner: Player 1's thirteen pile
            spieler2_dreizehner: Player 2's thirteen pile
            stalemate_counter: Number of turns without progress
            
        Returns:
            (is_stalemate, winner): Tuple of whether game is stalemate and who wins
            
        Rules:
            - After 30 turns without progress, check:
              - If both have thirteen piles: draw (winner = 0)
              - If only player 2 has thirteen pile: player 1 wins
              - If only player 1 has thirteen pile: player 2 wins
              
        BUG NOTES:
            - The current implementation only checks pile lengths, not actual playability
            - A better implementation would check if any legal moves exist
        """
        if stalemate_counter < 30:
            return False, None
        
        # Stalemate reached
        if len(spieler1_dreizehner) == 0:
            return True, 1  # Player 1 cleared their thirteen pile
        elif len(spieler2_dreizehner) == 0:
            return True, 2  # Player 2 cleared their thirteen pile
        else:
            return True, 0  # Both still have thirteen piles, draw


class GameLogicErrors:
    """
    Documented bugs and issues found in the original game logic.
    """
    
    BUGS = [
        {
            "file": "Klassen/spiel.py",
            "line": 189,
            "severity": "HIGH",
            "description": "Typo in krips_karte_gespielt call for player 2",
            "issue": "Uses self.spieler1listen[second] instead of self.spieler2listen[second]",
            "fix": "Change line 189 from 'self.current.krips_karte_gespielt(self.spieler1listen[second])' "
                   "to 'self.current.krips_karte_gespielt(self.spieler2listen[second])'"
        },
        {
            "file": "Klassen/spieler.py",
            "line": [183, 184, 189, 190],
            "severity": "HIGH", 
            "description": "Assignment operators used instead of equality operators",
            "issue": "Uses '==' instead of '=' in wegen_krips_aufhoeren which doesn't assign values",
            "fix": "Change '==' to '=' on lines 183, 184, 189, 190 to actually assign values"
        },
        {
            "file": "Klassen/spieler.py",
            "function": "ist_krips",
            "severity": "MEDIUM",
            "description": "Incomplete Krips detection",
            "issue": "May not detect all cases where a card can be played to center",
            "fix": "Review logic to ensure all possible center plays are detected"
        },
        {
            "file": "Klassen/spiel.py",
            "function": "is_stalemate",
            "severity": "LOW",
            "description": "Stalemate detection only checks lengths",
            "issue": "Doesn't check if moves are actually possible, just if piles haven't changed",
            "fix": "Consider adding logic to check if any legal moves exist"
        },
        {
            "file": "Klassen/spiel.py",
            "function": "play",
            "severity": "MEDIUM",
            "description": "No bounds checking on action parsing",
            "issue": "Doesn't validate that parsed indices are within valid ranges",
            "fix": "Add validation that second/fourth values are within 0-8 range as appropriate"
        }
    ]
    
    @classmethod
    def print_bug_report(cls):
        """Print a formatted bug report"""
        print("=" * 80)
        print("KRIPS GAME LOGIC - BUG REPORT")
        print("=" * 80)
        print()
        
        for i, bug in enumerate(cls.BUGS, 1):
            print(f"BUG #{i} - {bug['severity']} PRIORITY")
            print(f"File: {bug['file']}")
            if 'line' in bug:
                if isinstance(bug['line'], list):
                    print(f"Lines: {', '.join(map(str, bug['line']))}")
                else:
                    print(f"Line: {bug['line']}")
            if 'function' in bug:
                print(f"Function: {bug['function']}")
            print(f"Description: {bug['description']}")
            print(f"Issue: {bug['issue']}")
            print(f"Suggested Fix: {bug['fix']}")
            print("-" * 80)
            print()


if __name__ == "__main__":
    # Print bug report when run directly
    GameLogicErrors.print_bug_report()
