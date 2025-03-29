from enum import Enum
import random

import pygame
#from datenbank import Datenbank

from Pygame import GUI, MKarte
from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init,play_console,initialize_paechen, play_from_db
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
from Neuralnetwork_Stuff import Agent, DualingQNetwork, Storage
def main():

    nn = DualingQNetwork(0.001,'scratch.txt')
    nn.load_savestate()
    agent = Agent(nn)

    agent.training_loop(nn.optimizer,   2,0.9,1)







    #game1 = Spiel()
    #db = Datenbank()
    #newdeck1 = game1.kartenDeckErstellung()
    #newdeck2 = game1.kartenDeckErstellung()

    #random.shuffle(newdeck1)
    #random.shuffle(newdeck2)

    #spieler1 = Spieler(1, newdeck1)
    #spieler2 = Spieler(2, newdeck2)
    #game1.spieler1 = spieler1
    #game1.spieler2 = spieler2

    #db.game=game1

    #db.verbindung_aufbauen()

    # Mega wichtig initialisiert das Spiel in Spieler sind zwei funktionen. Problem wegen circular import
    # wird über eine quasi setter funktion in der _init_ gemacht
    #initialize(game1, spieler1, spieler2)


    #spieler1.ersteAktion()
    #spieler2.ersteAktion()
    #game1.game_first_move()
    #initialize_paechen(game1)



        #play_from_db(game1,db,6)
        #gui = GUI(game1)
        #gui.instance()
    #play_init(game1)
        #play_console(game1,db)
        #pygame.quit()



        #db.verbindung_schliessen()



if __name__ == "__main__":
    main()
