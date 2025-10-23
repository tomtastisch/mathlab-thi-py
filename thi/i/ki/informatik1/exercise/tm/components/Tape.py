# org.thi.i.ki.informatik1.exercise01.a4.components
# Tape-Klasse (Band der Turingmaschine)

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Self

# Symboltyp und Leerstelle
Symbol = str
BLANK: Symbol = "_"


class Direction(Enum):
    """
    ZWECK
    -----
    Bewegungsrichtungen des Lese-/Schreibkopfs.

    BEGRIFFE
    --------
    LEFT
        Kopfposition um 1 nach links.
    RIGHT
        Kopfposition um 1 nach rechts.
    STAY
        Kopfposition unverändert.
    """
    LEFT = "L"
    RIGHT = "R"
    STAY = "N"


@dataclass(slots=True)
class Tape:
    """
    ZWECK
    -----
    Repräsentiert das (potenziell unendliche) Band einer Turingmaschine in
    sparsamer Darstellung (nur belegte Zellen werden gespeichert).

    SCHNITTSTELLEN (ATTRIBUTE)
    --------------------------
    cells : dict[int, Symbol]
        Sparse-Belegung: Index → Symbol (nur Nicht-BLANK).
    head : int
        Aktuelle Kopfposition (kann negativ werden).
    blank : Symbol
        Darstellungszeichen für leere Zellen.

    HINWEIS
    -------
    - BLANK-Zellen werden nicht gespeichert.
    - Indizes sind ganzzahlig; Snapshot und Collect arbeiten auf halb-offenen Bereichen.

    WICHTIG (KAPSELUNG)
    -------------------
    - Während der TM-Simulation sollen ausschließlich die Methoden read(), write(),
      move() und erase()/at_blank() verwendet werden. Direkter Zugriff auf `cells`
      ist außerhalb der Tape-Implementierung zu vermeiden.
    """
    cells: dict[int, Symbol]
    head: int = 0
    blank: Symbol = BLANK

    # ----------------------------- Fabrik -----------------------------

    @classmethod
    def from_string(cls, s: str, blank: Symbol = BLANK) -> Self:
        """
        ZWECK
        -----
        Erzeugt ein Band aus einer dichten Zeichenkette.

        PARAMETER
        ---------
        s : str
            Ausgangsstring (z. B. '111+111').
        blank : Symbol
            Zeichen, das Leerstelle repräsentiert (Standard: '_').

        RÜCKGABE
        --------
        Tape : Sparse-Band, BLANK-Zellen werden nicht gespeichert.
        """
        return cls(cells={i: ch for i, ch in enumerate(s) if ch != blank}, blank=blank)

    # End from_string()

    # ----------------------------- I/O --------------------------------

    def read(self) -> Symbol:
        """
        ZWECK
        -----
        Liest das Symbol an der aktuellen Kopfposition.

        RÜCKGABE
        --------
        Symbol : Zeichen oder `blank`, falls unbelegt.
        """
        return self.cells.get(self.head, self.blank)

    # End read()

    def write(self, ch: Symbol) -> None:
        """
        ZWECK
        -----
        Schreibt ein Symbol an der Kopfposition; BLANK entfernt die Zelle.

        PARAMETER
        ---------
        ch : Symbol
            Zu schreibendes Zeichen.

        NEBENWIRKUNGEN
        --------------
        Aktualisiert `cells` an `head`.
        """
        if ch == self.blank:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = ch

    # End write()

    def erase(self) -> None:
        """
        ZWECK
        -----
        Löscht (setzt BLANK) an der aktuellen Kopfposition.
        """
        self.write(self.blank)

    # End erase()

    def at_blank(self) -> bool:
        """
        ZWECK
        -----
        Prüft, ob die aktuelle Kopfposition BLANK ist.
        """
        return self.read() == self.blank

    # End at_blank()

    # --------------------------- Bewegung -----------------------------

    def move(self, direction: Direction) -> None:
        """
        ZWECK
        -----
        Bewegt den Lesekopf um eine Position.

        PARAMETER
        ---------
        direction : Direction
            LEFT, RIGHT oder STAY.
        """
        match direction:
            case Direction.RIGHT:
                self.head += 1
            case Direction.LEFT:
                self.head -= 1
            case Direction.STAY:
                pass

    # End move()

    # --------------------------- Utilities ----------------------------

    def snapshot(self) -> str:
        """
        ZWECK
        -----
        Gibt den sichtbaren Bandinhalt im Bereich [min(cells), max(cells)] zurück.

        RÜCKGABE
        --------
        str : Dichte Darstellung inkl. BLANKs zwischen belegten Zellen.
        """
        if not self.cells:
            return ""
        lo = min(self.cells)
        hi = max(self.cells)
        return "".join(self.cells.get(i, self.blank) for i in range(lo, hi + 1))

    # End snapshot()

    def collect_all(self, symbol: Symbol) -> str:
        """
        ZWECK
        -----
        Liefert alle Vorkommen eines Symbols in Bandreihenfolge als String.
        Hinweis: Für Ausgaberekonstruktion nach HALT gedacht, nicht für TM-Schritte.
        """
        return "".join(ch for ch in self.snapshot() if ch == symbol)

    # End collect_all()

    # Die folgenden Hilfen sind für Random-Access-Analysen gedacht; nicht für TM-Schritte benutzen.
    def find(self, symbol: Symbol, start: int = 0, end: int | None = None) -> int | None:
        """
        ZWECK
        -----
        Findet die kleinste belegte Position ≥ start (und < end, falls gesetzt),
        die `symbol` enthält. Optimiert mit Generator-Expression.
        """
        ub = end if end is not None else float("inf")
        matching = (i for i, ch in self.cells.items() if start <= i < ub and ch == symbol)
        return min(matching, default=None)

    # End find()

    def has_remaining(self, symbol: Symbol, start: int, end: int | None = None) -> bool:
        """
        ZWECK
        -----
        Prüft, ob `symbol` im Bereich [start, end) noch vorkommt.
        """
        return self.find(symbol, start, end) is not None

    # End has_remaining()

    def collect(self, symbol: Symbol, start: int, end: int | None = None) -> str:
        """
        ZWECK
        -----
        Sammelt alle Vorkommen von `symbol` im Bereich [start, end) als String.
        """
        if not self.cells:
            return ""
        hi = end if end is not None else (max(self.cells) + 1)
        if start >= hi:
            return ""
        return "".join(ch for i in range(start, hi) if (ch := self.cells.get(i)) == symbol)
    # End collect()

# End Tape.py
