from Klassen.game_orchestor import Game_Orchestor


def main() -> None:
    # Konsolen-Version des Spieles.
    # pygame, torch und duckdb werden dafür nicht gebraucht und deshalb auch nicht geladen.
    orchestrator: Game_Orchestor = Game_Orchestor(seed=42)
    game = orchestrator.set_up_game()
    orchestrator.play_console(game)


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
