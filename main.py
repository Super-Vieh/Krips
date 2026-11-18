import time

from Gymnasium import KripsEnv, RandomBot,LeakyRuleBasedBot
import random

def main() -> None:

    #seed = random.randint(0, 2 ** 32 - 1)
    seed = 44
    start = time.perf_counter()
    env = KripsEnv()
    observation , (info) = env.reset(seed)
    legal_moves, player_number = (info["legal_moves"], info["player_number"])
    bot1 = LeakyRuleBasedBot(seed)
    bot2 = LeakyRuleBasedBot(seed)

    while True:
            if player_number == 1:
                move = bot1.act(env.game,legal_moves)
                (_, _, terminated, truncated, info) = env.step(move,False)
                legal_moves,player_number = (info["legal_moves"],info["player_number"])
                if terminated or truncated :
                    break
                move = bot2.act_off_turn(env.game,legal_moves)
                (_, _, terminated, truncated, info) = env.step(move,True)
                legal_moves, player_number = (info["legal_moves"],info["player_number"])
            if player_number == 2:
                move = bot2.act(env.game,legal_moves)
                (_, _, terminated, truncated, info) = env.step(move,False)
                legal_moves ,player_number= (info["legal_moves"],info["player_number"])
                if terminated or truncated:
                    break
                move = bot1.act_off_turn(env.game,legal_moves)
                (_, _, terminated, truncated, info) = env.step(move,True)
                legal_moves, player_number = (info["legal_moves"],info["player_number"])


    env.render()
    dauer = time.perf_counter() - start
    print(dauer)








# GUI- und Trainings-Variante. Die schweren Importe werden nur dort gebraucht:
# from Datenbank.datenbank import Database
# from Pygame import GUI, MKarte
# from Neuralnetwork_Stuff import Agent, DualingQNetwork, Recorder, AgentTrainer
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
