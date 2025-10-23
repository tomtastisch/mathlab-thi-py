# org.thi.i.ki.informatik1.exercise01.a4.components
# TransitionBuilder-Klasse

from enum import Enum, auto

from thi.i.ki.informatik1.exercise.tm.components.Tape import Direction


class State(Enum):
    """
    ZWECK
    -----
    Feingranulare Zustände für δ-getriebene Mikro-Schritte einer TM.

    BEGRIFFE (AUSZUG)
    -----------------
    START
        Initialzustand vor dem ersten δ-Schritt.
    PLUS_SCAN
        Scannt nach rechts bis zum '+' (Addition).
    PLUS_ERASE
        Ersetzt '+' durch BLANK.
    PLUS_SEEK_END
        Läuft nach rechts bis BLANK und hält (Addition abgeschlossen).
    SUB_PICK_R
        Wählt rechts die nächste '1' und markiert sie als 'x'.
    SUB_SEEK_LEFT_THROUGH_MINUS
        Läuft nach links über '-' hinweg zur linken Zahl.
    SUB_MATCH_L
        Sucht und löscht links eine korrespondierende '1'.
    SUB_RETURN_TO_R
        Kehrt zur markierten 'x' zurück.
    SUB_UNMARK_DELETE_R
        Löscht/entfernt die Markierung (oder die rechte '1') und iteriert.
    ACCEPT / REJECT
        Haltezustände.
    """
    START = auto()
    PLUS_SCAN = auto()
    PLUS_ERASE = auto()
    PLUS_SEEK_END = auto()
    SUB_PLACE_LBOUND = auto()
    SUB_AFTER_LBOUND = auto()
    SUB_SCAN_TO_MINUS = auto()
    SUB_SCAN_R = auto()
    SUB_PICK_R = auto()
    SUB_SEEK_LEFT_THROUGH_MINUS = auto()
    SUB_MATCH_L = auto()
    SUB_RETURN_TO_R = auto()
    SUB_UNMARK_DELETE_R = auto()
    SUB_CLEANUP_MINUS = auto()
    ACCEPT = auto()
    REJECT = auto()


class TransitionBuilder:
    """
    ZWECK
    -----
    Interner, schlanker Builder zur Erstellung der δ-Übergangstabelle.

    VERWENDUNG
    ----------
    - add(state, symbols, write, move, next_state):
      Fügt für ein oder mehrere Eingabesymbole dieselbe Transition hinzu.
    - add_same(state, symbols, move, next_state):
      Fügt Transitionen hinzu, wobei das gelesene Symbol unverändert zurückgeschrieben wird.
    - build():
      Liefert das aufbereitete δ-Lexikon zurück.
    """
    __slots__ = ("d",)

    def __init__(self) -> None:
        """
        ZWECK
        -----
        Initialisiert den Builder mit leerem δ-Dictionary.
        """
        self.d: dict[tuple[State, str], tuple[str, Direction, State]] = {}

    def add(
            self,
            state: State,
            symbols: str | list[str] | tuple[str, ...] | set[str],
            write: str, move: Direction,
            next_state: State
    ) -> None:
        """
        ZWECK
        -----
        Fügt eine oder mehrere Transitionen zur δ-Tabelle hinzu.

        PARAMETER
        ---------
        state : State
            Ausgangszustand.
        symbols : str | list[str] | tuple[str, ...] | set[str]
            Eingabesymbol(e), für die dieselbe Transition gilt.
        write : str
            Zu schreibendes Symbol.
        move : Direction
            Bewegungsrichtung (LEFT, RIGHT, STAY).
        next_state : State
            Folgezustand.

        NEBENWIRKUNGEN
        --------------
        Aktualisiert `self.d` mit den neuen Übergängen.
        """
        if isinstance(symbols, (list, tuple, set)):
            it = symbols
        else:
            it = [symbols]
        for sym in it:
            self.d[(state, sym)] = (write, move, next_state)

    def add_same(
            self,
            state: State,
            symbols: str | list[str] | tuple[str, ...] | set[str],
            move: Direction,
            next_state: State
    ) -> None:
        """
        ZWECK
        -----
        Fügt Transitionen hinzu, bei denen das gelesene Symbol unverändert
        zurückgeschrieben wird (write := read). Reduziert Redundanz für
        identische Übergänge auf mehrere Symbole.

        PARAMETER
        ---------
        state : State
            Ausgangszustand.
        symbols : str | list[str] | tuple[str, ...] | set[str]
            Eingabesymbol(e), die unverändert zurückgeschrieben werden.
        move : Direction
            Bewegungsrichtung (LEFT, RIGHT, STAY).
        next_state : State
            Folgezustand.

        NEBENWIRKUNGEN
        --------------
        Aktualisiert `self.d` mit den neuen Übergängen.
        """
        if isinstance(symbols, (list, tuple, set)):
            it = symbols
        else:
            it = [symbols]
        for sym in it:
            self.d[(state, sym)] = (sym, move, next_state)

    def build(self) -> dict[tuple[State, str], tuple[str, Direction, State]]:
        """
        ZWECK
        -----
        Liefert die aufgebaute δ-Übergangstabelle zurück.

        RÜCKGABE
        --------
        dict[tuple[State, str], tuple[str, Direction, State]]
            Die vollständige δ-Tabelle: (Zustand, Symbol) → (Schreiben, Bewegen, Folgezustand).
        """
        return self.d
# End TransitionBuilder.py
