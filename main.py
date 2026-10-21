import time

from Klassen.gameorchestor import GameOrchestor
from Gymnasium import KripsEnv, RandomBot
import random

def main() -> None:
    """
    orchestrator: GameOrchestor = GameOrchestor(seed=42)
    game = orchestrator.set_up_game()
    orchestrator.play_console(game)
    """
    start = time.perf_counter()
    env = KripsEnv()
    env.reset()
    seed = random.randint(0, 2 ** 32 - 1)
    bot1 = RandomBot(seed)
    bot2 = RandomBot(seed + 1)
    for i in range(0,1000000):
            if env.game.current_player.player_number == 1:
                move = bot1.act(env.game)
                env.step(move,False)
                move = bot2.act_off_turn(env.game)
                env.step(move,True)
                continue
            if env.game.current_player.player_number == 2:
                move = bot2.act(env.game)
                env.step(move,False)
                move = bot1.act_off_turn(env.game)
                env.step(move,True)
    dauer = time.perf_counter() - start
    print(dauer)








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
    main()
