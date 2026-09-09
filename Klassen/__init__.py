from .game import Game
from .player import Player
from .card import Card
from .board import Board
from .card_property_enum import CardType, CardValue
# Die Init Datei ist dazu da um die Klassen zu importieren und die Funktionen zu definieren
# Ausßerdem hat es den Sin, Sachen für das Spiel selber(Game, Player) zu initialisieren.
# game_initializer(GameInitializer) wird nicht mehr importiert (Datei fehlt).
# gameFactory(GameFactory) ist der alte, kaputte Entwurf und bleibt raus.
# playerFactory(PlayerFactory) fehlt (Datei ist leer).
