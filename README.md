                                                        Das Spiel des Krips

Das Spiel Krips ist eine Patience bei der zwei Spieler gegeneinander spielen. Die bekanntesten Bezeichnungen sind: Zank-Patience(deutsch), Russian Bank(amerikanisch) und Crapette(französisch).
Es ist ein eher unbekanntes Spiel, welches jedoch in meiner Familie seit mind. über einem Jahrhundert gespielt wird.

[Zur Wikipedia Seite zu Krips](https://de.wikipedia.org/wiki/Zank-Patience)

Dieses Repository dient als Darstellung meiner Fähigkeit, die ich in den Informatik-Modulen des ersten und zweiten Semesters des Wirtschaftsinformatik Studiums der TH-Koeln, erlangt habe.
Dieses Projekt ist ein Teil eines größeren Reinforcement-Learning Projektes zur Analyse einer optimalen Spielstrategie. 

Die momentane Zielsetzung ist: (X)= Beendet
- Erstelle ein Spiel, welches in der Konsole spielbar ist.                                        X
- Erstelle eine Graphical User Interface, welches die Konsole in der Ein- und Ausgabe ersetzt.    X
- Erstelle eine Datenhaltung, welche die Spielzüge in einer Schach änhlichen Notation speichert.
- Lernen des Umgangs mit Datenanalyse und Datendarstellungs Tools.
- Design einer ML-Architektur evtl. Deep Q Networks oder sogar Deep Dueling Q Networks.
- Umsetzung des Designs und Training des Modells mit Pytorch.
- Vielleicht weitere Spielereien.

Bis jetzt sind die Ersten zwei Punkte grob Beendet.


Allgemeine Spielregeln des Krips in Kurzform:  
Die Zielprämisse des Spiels ist es wie im Solitär Sets  zusammen zu legen. Von Ass -> Zwei -> ... -> König von Pik zu Karro.  
Dadurch ergeben sich 8 Felder in der Mitte in einer 4X2 Matrix.
Wenn man kann muss man die Karten zusammenlegen sonst, kann der Gegner diesen Fehler bemerken und der Spielzug wird an den Gegner übergeben.
Außenrum gibt es 8 Felder die frei belegt werden können, jedoch zu beginn mit jeweils einer Karte bedeckt sind. 4 von jedem Spieler.
Jeder Spieler hat 3 Haufen an Karten ein Haufen auf dem Karten abgelegt werden, wenn man keine Karte mehr hinlegen kann. Einen Haufen bei dem die Karten, bei Beenden des Zuges, genommen werden und auf den ersten, Ablagehaufe gelegt werden und zuletzt eine Stationären Haufen, das Dreizehner Päckchen. Die oberste Karte bleibt bestehen solange sie nicht irgentwo abgelegt werden kann, konträr zum Normalen Packchen welches seine oberste Karten auf den Haufen legt.  Das Dreizehner Päckchen wird mit 13 Karten befüllt. 
Wenn alle Karten von Normalen Päckchen abgespiel sind wird der Haufen umgedreht, also alle Karten auf dem Haufen werden auf das Normale Päckchen gelegt.





