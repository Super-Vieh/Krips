from game import Game
from player import Player
from numpy import random
class GameFactory:
        def __init__(self):
            pass

        def set_up_game(self):
            game = Game()
            newdeck1 = game.kartenDeckErstellung()
            newdeck2 = game.kartenDeckErstellung()

            random.shuffle(newdeck1)
            random.shuffle(newdeck2)

            spieler1 = Spieler(1, newdeck1)
            spieler2 = Spieler(2, newdeck2)
            game.spieler1 = spieler1
            game.spieler2 = spieler2

            SpielInitialisierer.initialize_oponents(game, game.spieler1, game.spieler2)
            return game
        def create_game(self):
            pass
        def add_player(self, player1: Player, player2: Player):
            pass
        def create_deck(self):
            pass
        def shuffle_deck(self):
            pass
        def setup_first_moves(self):
            pass
        



