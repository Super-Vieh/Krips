#!/usr/bin/env python
"""
Test script for Krips game with responsive Pygame GUI
"""
import random
import pygame

from Pygame import GUI
from Klassen import Spiel, Karten, Spieler, initialize, initialize_paechen

def main():
    print("Initializing Krips game...")
    
    # Create game and decks
    game1 = Spiel()
    newdeck1 = game1.kartenDeckErstellung()
    newdeck2 = game1.kartenDeckErstellung()

    random.shuffle(newdeck1)
    random.shuffle(newdeck2)

    # Create players
    spieler1 = Spieler(1, newdeck1)
    spieler2 = Spieler(2, newdeck2)
    game1.spieler1 = spieler1
    game1.spieler2 = spieler2

    # Initialize game (important for circular imports)
    initialize(game1, spieler1, spieler2)

    # Initial actions
    spieler1.ersteAktion()
    spieler2.ersteAktion()
    game1.game_first_move()
    initialize_paechen(game1)
    
    print("Starting responsive GUI...")
    print("Controls:")
    print("- Click on cards to pick them up and place them")
    print("- Red buttons are for calling 'Krips'")
    print("- Window is resizable!")
    
    # Create and run GUI
    gui = GUI(game1, width=1540, height=790)
    gui.instance()
    
    pygame.quit()
    print("Game closed. Thank you for playing!")

if __name__ == "__main__":
    main()
