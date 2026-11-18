from random import shuffle

from sympy.core.random import rng

from Klassen import Card, CardType, CardValue, Board , Game, Player
from Klassen.rules import Rules
import random
class GameFactory:
        def __init__(self):
            pass

        def set_up_game(self, seed: int):
            game = Game()
            game.board = Board()
            game.rules = Rules(game)
            newdeck1 = self.create_deck()
            newdeck2 = self.create_deck()

            rng = random.Random(seed)
            shuffled_deck1: list[Card] = self.shuffle_deck(newdeck1,rng)
            shuffled_deck2: list[Card] = self.shuffle_deck(newdeck2,rng)


            player1 = Player(1, shuffled_deck1)
            player2 = Player(2, shuffled_deck2)

            self.add_playes(game,player1, player2)
            self.setup_players(game, player1, player2)
            game.play_fist_cards()
            game.decide_first_player()
            return game

        def add_playes(self, game: Game, player1: Player, player2: Player):
            game.player1 = player1
            game.player2 = player2


        def shuffle_deck(self, deck: list[Card], rng):
            rng.shuffle(deck)
            return deck

        def create_deck(self) -> list[Card]:
            templist = []  # Speichert die Karten
            card_type = list(CardType)
            card_value = list(CardValue)

            for i in range(len(card_type)):
                for j in range(len(card_value)):
                    templist.append(Card(card_type[i], card_value[j]))
            return templist
        def setup_players(self, game: Game, player1: Player, player2: Player):
            player1.set_opponent(player2)
            player2.set_opponent(player1)

            player1.distribute_cards_to_decks()
            player2.distribute_cards_to_decks()
