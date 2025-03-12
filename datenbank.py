from numbers import Number
from operator import index

import cx_Oracle
from Klassen import Spiel, Karten, Spieler, KartenTyp, KartenWert

class Datenbank:
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


    def verbindung_aufbauen(self):
        try:
            # Verbindung herstellen
            self.connection = cx_Oracle.connect(f"{self.username}/{self.password}@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=StudiDB.GM.TH-Koeln.de)(PORT=1521))(CONNECT_DATA=(SID=vlesung)))")
            self.cursor = self.connection.cursor()
        except cx_Oracle.Error as error:
            print(f"Fehler beim Verbindungsaufbau {error}")

    def sql_statement_ausfuehren(self,sql:str):
        # bei SQL-Anweisungen wird das Semikolon am Ende hinzugefügt,
        # desswegen schreibt man das statement ohne Semikolon
        try:
            print("SQL-Anweisung wird ausgeführt")
            self.cursor.execute(sql)
            self.connection.commit()

        except cx_Oracle.Error as error:
            print(f"Fehler bei der Ausführung einer SQL-Anweisung{error}")

    def verbindung_schliessen(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Verbindung geschlossen")

    def erstelle_neuen_spieldatensatz(self):
        id = self.hoechster_spielname() + 1
        print(f"id ist{id}")
        sql = (f"CREATE TABLE Spiel_{id} ("
               f"Zugwechsel_ID NUMBER PRIMARY KEY,"
               f"Spielzuege VARCHAR2(3950),"
               f"Spielernummer NUMBER,"
               f"Metadaten VARCHAR2(50))")
        print(sql)
        self.sql_statement_ausfuehren(sql)

    def erstelle_kartendatensatz(self):
        id= self.hoechster_spielname()
        sql=(f"CREATE TABLE Spielkarten_{id}("
            "Spielernr Number,"
            "Paeckchen VARCHAR2(400),"
            "Dreizehner Varchar2(250),"
            "erste4karten Varchar2(90))")
        self.sql_statement_ausfuehren(sql)

    def loesche_alle_spiele(self):
        for i in range(0, self.hoechster_spielname() + 1):
            sql = f"DROP TABLE SPIEL_{i}"
            self.sql_statement_ausfuehren(sql)

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
