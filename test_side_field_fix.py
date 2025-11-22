#!/usr/bin/env python3
"""
Test script to verify that cards cannot be placed on empty side fields
"""

import sys
from Klassen.spiel import Spiel
from Klassen.spieler import Spieler
from Klassen.karten import Karten, KartenTyp, KartenWert

def test_empty_side_field():
    """Test that cards cannot be placed on empty side fields after initial setup"""
    print("Testing empty side field card placement...")
    
    # Create a game
    game = Spiel()
    
    # Create two decks
    deck1 = game.kartenDeckErstellung()
    deck2 = game.kartenDeckErstellung()
    
    # Create players
    spieler1 = Spieler(1, deck1)
    spieler2 = Spieler(2, deck2)
    
    # Set up the game
    game.spieler1 = spieler1
    game.spieler2 = spieler2
    spieler1.set_spiel(game)
    spieler2.set_spiel(game)
    spieler1.set_gegenspieler(spieler2)
    spieler2.set_gegenspieler(spieler1)
    game.spieler1listen = [game.spieler1Paechen, game.spieler1Haufen, game.spieler1Dreizehner]
    game.spieler2listen = [game.spieler2Paechen, game.spieler2Haufen, game.spieler2Dreizehner]
    
    # Create a test card
    test_card = Karten(KartenTyp.Pik, KartenWert.Zwei)
    test_card.karteOffen = True
    
    # Create a test list with the card
    test_list = [test_card]
    
    # Test 1: Try to place card on empty side field (should NOT work)
    print("\n=== Test 1: Placing card on empty side field (default behavior) ===")
    initial_length = len(test_list)
    side_field_length = len(game.platzliste[0])
    print(f"Test list length before: {initial_length}")
    print(f"Side field 1 length before: {side_field_length}")
    
    spieler1.seiteHinlegen(1, test_list)
    
    final_length = len(test_list)
    side_field_final_length = len(game.platzliste[0])
    print(f"Test list length after: {final_length}")
    print(f"Side field 1 length after: {side_field_final_length}")
    
    if final_length == initial_length and side_field_final_length == 0:
        print("✓ PASS: Card was NOT placed on empty side field (correct behavior)")
    else:
        print("✗ FAIL: Card was placed on empty side field (incorrect behavior)")
        sys.exit(1)
    
    # Test 2: Try to place card on empty side field with allow_empty=True (should work)
    print("\n=== Test 2: Placing card on empty side field with allow_empty=True ===")
    test_list = [test_card]
    initial_length = len(test_list)
    print(f"Test list length before: {initial_length}")
    print(f"Side field 1 length before: {side_field_final_length}")
    
    spieler1.seiteHinlegen(1, test_list, allow_empty=True)
    
    final_length = len(test_list)
    side_field_final_length = len(game.platzliste[0])
    print(f"Test list length after: {final_length}")
    print(f"Side field 1 length after: {side_field_final_length}")
    
    if final_length == 0 and side_field_final_length == 1:
        print("✓ PASS: Card was placed on empty side field with allow_empty=True (correct behavior)")
    else:
        print("✗ FAIL: Card was NOT placed on empty side field with allow_empty=True (incorrect behavior)")
        sys.exit(1)
    
    # Test 3: Try to place card on non-empty side field (should work if valid)
    print("\n=== Test 3: Placing valid card on non-empty side field ===")
    # The side field now has a Pik 2 (value 2), so we can place a red 1 (Ace)
    red_ace = Karten(KartenTyp.Coeur, KartenWert.Ass)
    red_ace.karteOffen = True
    test_list2 = [red_ace]
    
    initial_length = len(test_list2)
    side_field_length = len(game.platzliste[0])
    print(f"Test list length before: {initial_length}")
    print(f"Side field 1 length before: {side_field_length}")
    print(f"Top card on side field 1: {game.platzliste[0][-1].kartentyp.value} {game.platzliste[0][-1].kartenwert.value}")
    print(f"Card to place: {red_ace.kartentyp.value} {red_ace.kartenwert.value}")
    
    spieler1.seiteHinlegen(1, test_list2)
    
    final_length = len(test_list2)
    side_field_final_length = len(game.platzliste[0])
    print(f"Test list length after: {final_length}")
    print(f"Side field 1 length after: {side_field_final_length}")
    
    if final_length == 0 and side_field_final_length == 2:
        print("✓ PASS: Valid card was placed on non-empty side field (correct behavior)")
    else:
        print("✗ FAIL: Valid card was NOT placed on non-empty side field (incorrect behavior)")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        test_empty_side_field()
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
