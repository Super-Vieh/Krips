import cProfile
import os
import pstats
import sys
import time

from Klassen.gameorchestor import GameOrchestor
from Gymnasium import KripsEnv, RandomBot
from Neuralnetwork_Batch import AgentTrainer
import random


def main(profile: bool = False, tensorboard: bool = True) -> None:
    if profile:
        tensorboard = False
    trainer = AgentTrainer(
        batch_size=256,
        buffer_capacity=100_000,
        n_envs=8,
        seed=0,
        updates_per_round=1,
        log_to_tensorboard=tensorboard,
    )
    trainer.load_nn("BatchAgent1.txt", "BatchAgent2.txt")
    profiler = cProfile.Profile()
    if profile:
        profiler.enable()
    try:
        trainer.train_agents(
            nr_epochs=1,
            episodes_per_epoch=10,
            steps=2000,
            start_epsilon=0.9,
            discount_factor=0.9,
            epsilon_decay=0.9999,
            n_envs=8,
            opponent=RandomBot(0),
        )
    finally:
        if profile:
            profiler.disable()
            os.makedirs("profiles", exist_ok=True)
            profiler.dump_stats("profiles/8env20000updates.prof")
            pstats.Stats(profiler).sort_stats("cumulative").print_stats(30)







# GUI- und Trainings-Variante. Die schweren Importe werden nur dort gebraucht:
# from Datenbank.datenbank import Database
# from Pygame import GUI, MKarte
# from Neuralnetwork_Stuff import Agent, DualingQNetwork, Storage, AgentTrainer
"""

    for i in range(0,40):
        trainer = AgentTrainer()
        trainer.load_nn("Agent1.txt", "Agent2.txt")
        trainer.train_agents_and_store(1, 2000, 0.9, 0.9, 0.9999)
        #trainer.train_agents_and_replay(20, 2000, 0.9, 0.9, 0.9999)

        #play_from_db(game1,db,6)
        #gui = GUI(game1)
        #gui.instance()

        #play_console(game1,db)
        #pygame.quit()


        #db.verbindung_schliessen()

"""

if __name__ == "__main__":
    main(
        profile="--profile" in sys.argv,
        tensorboard="--no-tensorboard" not in sys.argv,
    )
