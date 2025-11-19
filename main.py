from enum import Enum
import random

import pygame

from Pygame import GUI, MKarte
from Klassen import print_sidesplus, seitenKarten, mittlereKarten, initialize,print_top, print_bot,play_init,initialize_paechen
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
from Neuralnetwork_Stuff import Agent, DualingQNetwork, Storage
def main():

    nn = DualingQNetwork(0.001,'scratch.txt')
    nn.load_savestate()
    agent = Agent(nn)

    agent.training_loop(nn.optimizer,   2,0.9,1)


if __name__ == "__main__":
    main()
