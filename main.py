from enum import Enum
import random

import pygame

from Datenbank.datenbank import Datenbank
from Klassen.spielinititalisierer import SpielInitialisierer
from Datenbank import Datenbank

from Pygame import GUI, MKarte
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert, SpielInitialisierer
from Neuralnetwork_Stuff import Agent, DualingQNetwork, Storage, AgentTrainer
def main():

    for i in range(0,40):
        trainer = AgentTrainer()
        trainer.load_nn("Agent1.txt", "Agent2.txt")
        #trainer.train_agents_and_store(1, 2000, 0.9, 0.9, 0.9999)
        trainer.train_agents_and_replay(20, 2000, 0.9, 0.9, 0.9999)

        #play_from_db(game1,db,6)
        #gui = GUI(game1)
        #gui.instance()

        #play_console(game1,db)
        #pygame.quit()



        #db.verbindung_schliessen()



if __name__ == "__main__":
    main()
