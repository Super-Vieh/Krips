from numbers import Number
from operator import index

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
    def get_game_moves(self, id:int)->list[str]:
        pass
    def get_starting_cards(self,id:int):
        pass
    def save_starting_cards(self,game:Spiel):
        if not self._check_if_table_exists("StartingCards"):
            self._create_starting_cards_table()
        if not self._check_if_table_exists("Moves"):
            self.create_moves_table()

        if self.get_max_id("StartingCards")== self.get_max_id("Moves"):
            self.store_starting_cards(self.get_max_id("Moves"),game)
        else:
            raise Exception("Die Moves und StartingCards Tabellen haben einen Fehler, sie es gibt irgedwo extra einträge")
    def save_game_moves(self,game:Spiel,zuege:list[str],id:int):
        pass
    def reset(self):
        pass

    #Hauptfunktionen


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
            SPIELER1HAUFEN VARCHAR[],
            SPIELER1PAECKCHEN VARCHAR[],
            SPIELER1DREIZEHNER VARCHAR[],
            SPIELER2HAUFEN VARCHAR[],
            SPIELER2PAECKCHEN VARCHAR[],
            SPIELER2DREIZEHNER VARCHAR[]
                )""")
        self.connection.execute(sql)

    def create_moves_table(self):
        sql = ("""CREATE TABLE IF NOT EXISTS Moves (
            GAME_ID INTEGER PRIMARY KEY,
            MOVES VARCHAR[]
                )""")
        self.connection.execute(sql)

    def store_moves(self,id:int,zuege:list[str]):
        sql = "INSERT INTO Moves VALUES (?, ?)"
        self.connection.execute(sql, (id, zuege))


    def store_starting_cards(self,id:int,game:Spiel):
        spieler1haufen = self.convert_listofcard_in_json(game.spieler1Haufen)
        spieler1paeckchen = self.convert_listofcard_in_json(game.spieler1Dreizehner)
        spieler1dreizehner = self.convert_listofcard_in_json(game.spieler1Dreizehner)
        spieler2haufen = self.convert_listofcard_in_json(game.spieler2Haufen)
        spieler2paeckchen = self.convert_listofcard_in_json(game.spieler1Haufen)
        spieler2dreizehner = self.convert_listofcard_in_json(game.spieler2Dreizehner)


        sql = "INSERT INTO StartingCards VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.connection.execute(sql, (id,spieler1haufen,spieler1paeckchen,spieler1dreizehner,spieler2haufen,spieler2paeckchen,spieler2dreizehner ))


    def convert_listofcard_in_json(self, cards:list[Karten]):
        list_jsonobjects = []
        for card in cards:
            card_json = {
                "wert": card.kartenwert.value,
                "typ": card.kartentyp.value,
                "offen": card.karteOffen
            }
            list_jsonobjects.append(card_json)
        return list_jsonobjects

    def get_max_id(self,table_name:str):
        sql = f"SELECT MAX(GAME_ID) FROM {table_name}"
        result = self.connection.execute(sql).fetchone()
        if result[0] is not None:
            return result[0]
        else:
            return 0

    def loesche_alle_spiele(self):
        for i in range(0, self.hoechster_spielname() + 1):
            sql = f"DROP TABLE SPIEL_{i}"
            self._commit_sql_querry(sql)

    def erstelle_ein_spieldatensatz(self, zugwechsel:int, alle_actionen:str, spielernummer:int):
        #wird bei dem Spiel Ablauf bei Klassen init ausgeführt
        cur = self.cursor.execute("SELECT table_name FROM user_tables WHERE table_name LIKE 'SPIEL\_%' ESCAPE '\\'")
        rows = cur.fetchall()

        #keine ahnung warum f"{}" für die variablen nicht funktioniert
        sql = f"INSERT INTO {rows[-1][-1]} (Zugwechsel_ID, Spielzuege, Spielernummer, Metadaten) VALUES (:1, :2, :3, :4)"
        print(sql)
        self.cursor.execute(sql, (zugwechsel, alle_actionen, spielernummer, None))
        self.connection.commit()

    def erstelle_ein_kartendatensatz(self, sp1_paeckchen, sp2_paeckchen, sp1_dreizehner, sp2_dreizehner, sp1_4karten, sp2_4karten):
            cur = self.cursor.execute("SELECT table_name FROM user_tables WHERE table_name LIKE 'SPIELKARTEN_%'")
            rows = cur.fetchall()

            sql = f"INSERT INTO {rows[-1][-1]} (Spielernr, Paeckchen, Dreizehner, erste4Karten) VALUES (:1, :2, :3, :4)"
            self.cursor.execute(sql, (1, sp1_paeckchen, sp1_dreizehner, sp1_4karten))
            self.cursor.execute(sql, (2, sp2_paeckchen, sp2_dreizehner, sp2_4karten))
            self.connection.commit()







    #Das ist eine relevante funktion für das Erstellen einer neuen Tabelle. Damit man keine Dublikate hat.
    def hoechster_spielname(self):
        cur = self.cursor.execute("SELECT table_name FROM user_tables WHERE table_name LIKE 'SPIEL\_%' ESCAPE '\\'")
        rows= cur.fetchall()
        #hier wird die höchste zahl rausgesucht
        highest = 0
        for row in rows:
            temp = self.extrahiere_spielnummer(row)
            if temp >highest: highest=temp
        return highest

    def extrahiere_spielnummer(self,spieltext:tuple[str])->int:
        #spieltext ist ein Tupel welcher auf der erstenstelle den namen der Tabelle hat
        start_indize =0
        indize =0
        ergebniss:int =0
        tabellenname:str = spieltext[0]
        for char in tabellenname:
            if char == '_': start_indize = indize
            indize+=1

        nummer_als_text=""
        for i in range(start_indize+1,indize):
            nummer_als_text+=tabellenname[i]# hier werden die buchstaben bzw. zahlen extrahiert.
        try :
            ergebniss=int(nummer_als_text)
        except ValueError:
            return 0
            print("In der Spielernummer kann kein String sein")
        return ergebniss




    def extrahiere_spiel(self,tabellennr:int):
        cur = self.cursor.execute("SELECT table_name FROM user_tables WHERE table_name LIKE 'SPIEL\_%' ESCAPE '\\'")
        rows = cur.fetchall()
        for row in rows :
            #Wenn das spiel gleich der Spielnummer ist
            if self.extrahiere_spielnummer(row)== tabellennr:
                sql = f"SELECT Spielzuege FROM Spiel_{tabellennr}"
                spielzuege = self.cursor.execute(sql)
                zuege =spielzuege.fetchall()
                return self.extrahiere_spielzuege(zuege)

    def extrahiere_spielkarten(self,tabellennr:int)->tuple[tuple[int,str,str,str]]:
        cur = self.cursor.execute("SELECT table_name FROM user_tables WHERE table_name LIKE 'SPIELKARTEN_%'")
        rows = cur.fetchall()

        for row in rows:
            if self.extrahiere_spielnummer(row)== tabellennr:
                sql = f"SELECT Spielernr,Paeckchen, Dreizehner, erste4karten FROM SPIELKARTEN_{tabellennr}"
                karten = self.cursor.execute(sql)
                return karten




    #kriegt ein tupel mit alle spielzuegen eines Spieles und convertiert das in einen einzelnen string
    def extrahiere_spielzuege(self,zuege):
        alle_spielzuege=""
        for zug in zuege:
            alle_spielzuege+=self.saubere_spielzug(zug[0])
        return alle_spielzuege

    #kriegt ein string und entfernt alle doppelten kommas
    def saubere_spielzug(self,zug:str):
        ergebniss=""
        last_buchtabe=""
        for buchstabe in zug:
            if( buchstabe== "," and last_buchtabe!=",")or(buchstabe!=","):
                ergebniss+=buchstabe
            last_buchtabe=buchstabe
        return ergebniss
