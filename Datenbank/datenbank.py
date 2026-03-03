from json import dumps, loads
from numbers import Number
from operator import index
import json

import setuptools
from numpy import integer
from sympy.codegen.ast import Raise

from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert
import duckdb
class Datenbank:
    def __init__(self,dbfilepath):
        self.connection = duckdb.connect(dbfilepath)




    '''
    game:Spiel = None
    hostname = "StudiDB.GM.TH-Koeln.de"
    port = 1521
    sid = "vlesung"
    username:str = input("Bitte geben Sie Ihren Benutzernamen ein: ")
    password:str = input("Bitte geben Sie Ihr Passwort ein: ")
    # Verbindungsstring
    connection_str = f"{username}/{password}@{hostname}:{port}/{sid}"
    connection = None
    cursor = None
    menge_an_spielen = 0 # mit einer Funktion die anzahl der einzelnen Spiele in einer Datenbank zählt, berrechnen
    '''
    # Interface Funktionen
    def load_game_moves(self, id:int)->list[str]:
        if not self._check_if_table_exists("Moves"):
            return []
        return self._extrakt_game_moves(id)
    def load_starting_cards(self, id:int):
        if not self._check_if_table_exists("StartingCards"):
            raise Exception("Es gibt keine StartingCards Tabelle, es wurden noch keine Spiele gespeichert")
        return self._extract_game_starting_cards(id)
    def save_starting_cards(self,game:Spiel,id:int):
        if not self._check_if_table_exists("StartingCards"):
            self._create_starting_cards_table()
        if not self._check_if_table_exists("Moves"):
            self._create_moves_table()
        self._store_starting_cards(id, game)
        '''
        if self._get_max_id("StartingCards")== self._get_max_id("Moves"):
            self._store_starting_cards(self._get_max_id("Moves")+1,game)
            print(self._get_max_id("StartingCards"))
        else:
            raise Exception("Die Moves und StartingCards Tabellen haben einen Fehler, sie es gibt irgedwo extra einträge")
        '''
    def save_game_moves(self,zuege:list[str],id:int):
        self._store_moves(id, zuege)

    def reset_table(self, table_name: str):
        sql = f"TRUNCATE TABLE {table_name}"
        self.connection.execute(sql)

    def delete_table(self, table_name: str):
        sql = f"DROP TABLE {table_name}"
        self.connection.execute(sql)
    #Wenn es keine Tabellen gibt, dann wird die ID 1 sein
    def get_next_game_id(self) -> int:
        if not self._check_if_table_exists("StartingCards"):
            return 1
        id = self._get_max_id("StartingCards") + 1
        return id
    #Funktionen für die Datenbank


    def _check_if_table_exists(self,table_name:str)->bool:
        sql = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?"
        result = self.connection.execute(sql,[table_name]).fetchone()
        # Ergebnis ist so aus (0,) oder (1,)
        if result[0] > 0:
            return True
        else:
            return False
    def _create_starting_cards_table(self):
        sql = ("""CREATE TABLE IF NOT EXISTS StartingCards (
            GAME_ID INTEGER PRIMARY KEY,
            SPIELER1OWNDECK VARCHAR,
            SPIELER2OWNDECK VARCHAR
                )""")
        self.connection.execute(sql)

    def _create_moves_table(self):
        sql = ("""CREATE TABLE IF NOT EXISTS Moves (
            GAME_ID INTEGER PRIMARY KEY,
            MOVES VARCHAR[]
                )""")
        self.connection.execute(sql)

    def _store_moves(self, id:int, zuege:list[str]):
        sql = "INSERT INTO Moves VALUES (?, ?)"
        self.connection.execute(sql, (id, zuege))


    def _store_starting_cards(self, id:int, game:Spiel):
        spieler1owndeck = dumps(self._convert_listofcard_in_json(game.spieler1.owndeck))
        spieler2owndeck = dumps(self._convert_listofcard_in_json(game.spieler2.owndeck))


        sql = "INSERT INTO StartingCards VALUES (?, ?, ?)"
        self.connection.execute(sql, (id,spieler1owndeck,spieler2owndeck))

    def _convert_listofcard_in_json(self, cards:list[Karten]):
        list_jsonobjects = []
        for card in cards:
            card_json = {
                "wert": card.kartenwert.value,
                "typ": card.kartentyp.value,
                "offen": card.karteOffen
            }
            list_jsonobjects.append(card_json)
        return list_jsonobjects

    def _get_max_id(self, table_name:str):
        sql = f"SELECT MAX(GAME_ID) FROM {table_name}"
        result = self.connection.execute(sql).fetchone()
        if result[0] is not None:
            return result[0]
        else:
            return 0

    def _extrakt_game_moves(self, id:int)->list[str]:
        sql = "SELECT MOVES FROM MOVES WHERE GAME_ID = ?"
        moves = self.connection.execute(sql, (id,)).fetchone()
        print(moves)
        if moves is None:
            return []
        else:
            return moves[0]
    def _extract_game_starting_cards(self, id:int):
        sql = "SELECT SPIELER1OWNDECK, SPIELER2OWNDECK FROM StartingCards WHERE GAME_ID = ?"
        result = self.connection.execute(sql, (id,)).fetchone()
        if result is None:
            raise Exception("Es gibt keine Startkarten für diese ID")
        print(result)
        spieler1_own_deck = self._read_starting_cards_from_json_list(result[0])
        spieler2_own_deck =self._read_starting_cards_from_json_list(result[1])
        return spieler1_own_deck, spieler2_own_deck

    def _read_starting_cards_from_json_list(self, json_list):
        card_list = []
        print(json_list)
        json_list = loads(json_list)
        for card_json in json_list:
            wert = card_json["wert"]
            typ = card_json["typ"]
            offen = card_json["offen"]
            karte = Karten(KartenTyp(typ),KartenWert(wert))
            karte.karteOffen = offen
            card_list.append(karte)
        return card_list
