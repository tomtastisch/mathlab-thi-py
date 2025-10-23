# org.thi.i.ki.informatik1.exercise01.a4.components
# TuringMachine.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict

from org.thi.i.ki.informatik1.exercise01.a4.components.Tape import Tape, Direction
from org.thi.i.ki.informatik1.exercise01.a4.components.TransitionBuilder import TransitionBuilder, State


class TraceEntry(TypedDict):
    """ZWECK: Repräsentiert einen protokollierten Schritt (DIN-gerecht, knapp)."""
    position: int
    state: str

class RunResult(TypedDict):
    """ZWECK: Strukturierte Rückgabe von `run_operation`."""
    operator: Literal["+", "-"]
    input: str
    output: str
    steps: int
    state: str
    position: int
    trace: list[TraceEntry]


@dataclass(slots=True)
class TuringMachine:
    """
    ZWECK
    -----
    Simulation einer Turingmaschine für unäre Addition bzw. Subtraktion.

    GELTUNGSBEREICH
    ---------------
    Natürliche Zahlen (>= 0) in unärer Darstellung auf einem Band mit Operator
    '+' oder '-'.

    SCHNITTSTELLEN (ATTRIBUTE)
    --------------------------
    n1 : int
        Linker Operand (dezimal).
    op : Literal['+','-']
        Operator.
    n2 : int
        Rechter Operand (dezimal).
    tape : Tape
        Interne Bandrepräsentation (zur Laufzeit erzeugt).
    result : str
        Ergebnis im Unärformat bzw. '-' bei REJECT.
    steps : int
        Zähler der δ-Mikroschritte (read→write→move→next-state), beidrichtungsfähig.
    state : State
        Aktueller Maschinenzustand (laufend konsistent, feingranular).
    trace : list[TraceEntry]
        Protokoll der Kopfposition und Zustände pro δ-Schritt.

    VORAUSSETZUNGEN
    ---------------
    - op ∈ {'+','-'}
    - n1, n2 ≥ 0

    NEBENWIRKUNGEN
    --------------
    - Schreibt auf `tape`, ändert `state`, `steps`, `result`, `trace`.

    HINWEIS
    -------
    Docstrings sind normgerecht gegliedert (Zweck, Voraussetzungen, Schnittstellen).
    """
    n1: int
    op: Literal["+", "-"]
    n2: int

    tape: Tape = field(init=False)
    result: str = field(init=False, default="")
    steps: int = field(init=False, default=0)
    state: State = field(init=False, default=State.START)
    trace: list[TraceEntry] = field(init=False, default_factory=list)

    # δ-Übergangsfunktion: (state, symbol) -> (write, move, next_state)
    delta: dict[tuple[State, str], tuple[str, Direction, State]] = field(init=False, default_factory=dict)

    # ----------------------------- Public API -----------------------------

    def run_operation(self) -> RunResult:
        """
        ZWECK
        -----
        Führt die konfigurierte Operation auf dem Band aus und liefert
        ein strukturiertes Ergebnis.

        ABLAUF (KURZ)
        -------------
        1) Validieren,
        2) Eingabe konstruieren,
        3) Band erzeugen,
        4) Schrittweise ausführen,
        5) Ergebnis zurückgeben.

        RÜCKGABE
        --------
        RunResult : Struktur mit Operator, Ein-/Ausgabe, Schritte, Zustand,
        Kopfposition und Trace.

        FEHLERVERHALTEN
        ---------------
        ValueError bei ungültigen Eingaben.
        """
        self._validate_inputs()
        tape_input = self._make_input()
        self.tape = Tape.from_string(tape_input)
        self._run_operation_steps(tape_input)
        return {
            "operator": self.op,
            "input": tape_input,
            "output": self.result,
            "steps": self.steps,
            "state": self.state.name,
            "position": self.tape.head,
            "trace": self.trace,
        }

    # ---------------------------- Internals ------------------------------

    def _validate_inputs(self) -> None:
        """
        ZWECK
        -----
        Laufzeitvalidierung der Eingaben.

        VORAUSSETZUNGEN
        ---------------
        - op ∈ {'+','-'}
        - n1, n2 ≥ 0

        FEHLERVERHALTEN
        ---------------
        ValueError bei Verstößen.
        """
        if self.op not in {"+", "-"}:
            raise ValueError("op muss '+' oder '-' sein.")
        if self.n1 < 0 or self.n2 < 0:
            raise ValueError("n1 und n2 müssen natürliche Zahlen (>= 0) sein.")

    def _make_input(self) -> str:
        """
        ZWECK
        -----
        Erzeugt die unäre Eingabezeichenkette, z. B. '111 + 11'.

        RÜCKGABE
        --------
        str : Unärstring der Form '1'*n1 + op + '1'*n2.
        """
        return f"{'1' * self.n1}{self.op}{'1' * self.n2}"

    def _run_operation_steps(self, tape_input: str) -> None:
        """
        ZWECK
        -----
        δ-getriebene Ausführung mit lokalen Lese-/Schreiboperationen.

        RAHMEN
        ------
        - Initialisiert die δ-Funktion abhängig vom Operator ('+' oder '-').
        - Führt Mikro-Schritte aus: read → write → move → next-state.
        - Pro δ-Schritt wird der Trace fortgeschrieben und `steps` erhöht.
        - Bei fehlender Transition → REJECT (wohlgeformte Eingaben vorausgesetzt).
        """
        # Startzustand setzen und δ-Tabelle aufbauen
        self.state = State.START
        self._build_delta()

        # Initialen Snapshot des Zustands protokollieren (optional)
        self._trace_step()

        # Mikro-Schritt-Schleife
        while self.state not in (State.ACCEPT, State.REJECT):
            self.step()

        # Nach HALT: Ausgabe rekonstruieren (nur '1' zählen/ausgeben)
        if self.state == State.ACCEPT:
            # Für 0 → '' (leerer String). Kein '-' als Nullmarker.
            self.result = self.tape.collect_all('1')
        else:
            # Keine Überlagerung von REJECT mit Nullmarker
            self.result = ""

    # ------------------------- δ-Engine --------------------------

    def step(self) -> None:
        """
        Führt genau einen δ-Mikroschritt aus.
        read → write → move → next-state; zählt Schritt und traced.
        """
        a = self.tape.read()
        key = (self.state, a)
        if key not in self.delta:
            # Ungültige Konfiguration → REJECT (wohlgeformte Eingaben vorausgesetzt)
            self._reject()
            self._trace_step()
            return
        b, move, q2 = self.delta[key]
        self.tape.write(b)
        self.tape.move(move)
        self.state = q2
        self.steps += 1
        self._trace_step()

    def _build_delta(self) -> None:
        """
        ZWECK
        -----
        Koordiniert den Aufbau der δ-Übergangstabelle abhängig vom Operator.
        """
        if self.op == "+":
            self.delta = self._build_addition_delta()
        else:
            self.delta = self._build_subtraction_delta()

    def _build_addition_delta(self) -> dict[tuple[State, str], tuple[str, Direction, State]]:
        """
        ZWECK
        -----
        Baut die δ-Übergangstabelle für Addition ('+') auf.

        STRATEGIE
        ---------
        Löscht das '+' und läuft zum Ende des Bandes → ACCEPT.
        """
        bl = self.tape.blank
        tb = TransitionBuilder()

        # START: scanne rechts bis '+'
        tb.add(State.START, '1', '1', Direction.RIGHT, State.PLUS_SCAN)
        tb.add(State.START, '+', bl, Direction.RIGHT, State.PLUS_SEEK_END)  # leeres LHS
        tb.add_same(State.START, {bl, '-'}, Direction.STAY, State.REJECT)

        # PLUS_SCAN: über '1' nach rechts, am '+' löschen und in SEEK_END
        tb.add(State.PLUS_SCAN, '1', '1', Direction.RIGHT, State.PLUS_SCAN)
        tb.add(State.PLUS_SCAN, '+', bl, Direction.RIGHT, State.PLUS_SEEK_END)
        tb.add_same(State.PLUS_SCAN, {bl, '-'}, Direction.STAY, State.REJECT)

        # PLUS_SEEK_END: bis BLANK laufen, dann halten (ACCEPT)
        tb.add(State.PLUS_SEEK_END, '1', '1', Direction.RIGHT, State.PLUS_SEEK_END)
        tb.add(State.PLUS_SEEK_END, bl, bl, Direction.STAY, State.ACCEPT)

        return tb.build()

    def _build_subtraction_delta(self) -> dict[tuple[State, str], tuple[str, Direction, State]]:
        """
        ZWECK
        -----
        Baut die δ-Übergangstabelle für Subtraktion ('-') auf.

        STRATEGIE
        ---------
        Markiert rechte '1' als 'x', sucht links passende '1', löscht beide.
        Iteriert bis rechts leer, dann Cleanup und ACCEPT.
        """
        bl = self.tape.blank
        tb = TransitionBuilder()

        # START → linke Bandgrenze markieren ('L') und dann bis '-' scannen,
        # Falls n1 > 0: von der ersten '1' aus eine linke Grenze setzen
        # Falls n1 == 0: Grenze links vom '-' setzen
        tb.add(State.START, '1', '1', Direction.LEFT, State.SUB_PLACE_LBOUND)
        tb.add(State.START, '-', '-', Direction.LEFT, State.SUB_PLACE_LBOUND)
        tb.add_same(State.START, {bl, '+'}, Direction.STAY, State.REJECT)

        # SUB_PLACE_LBOUND: schreibe permanente linke Grenze 'L' links der Eingabe und entscheide Fortsetzung
        tb.add(State.SUB_PLACE_LBOUND, bl, 'L', Direction.RIGHT, State.SUB_AFTER_LBOUND)

        # SUB_AFTER_LBOUND: je nach aktuellem Zeichen fortfahren
        tb.add(State.SUB_AFTER_LBOUND, '1', '1', Direction.RIGHT, State.SUB_SCAN_TO_MINUS)
        tb.add(State.SUB_AFTER_LBOUND, '-', '-', Direction.RIGHT, State.SUB_SCAN_R)
        tb.add_same(State.SUB_AFTER_LBOUND, {bl, 'L', 'x', '+'}, Direction.STAY, State.REJECT)

        # SUB_SCAN_TO_MINUS: rechts über linke Einsen bis '-'
        tb.add(State.SUB_SCAN_TO_MINUS, '1', '1', Direction.RIGHT, State.SUB_SCAN_TO_MINUS)
        tb.add(State.SUB_SCAN_TO_MINUS, '-', '-', Direction.RIGHT, State.SUB_SCAN_R)
        tb.add(State.SUB_SCAN_TO_MINUS, bl, bl, Direction.STAY, State.REJECT)

        # SUB_SCAN_R: rechts nach nächster rechten '1' suchen oder rechts leer
        tb.add(State.SUB_SCAN_R, '1', 'x', Direction.LEFT, State.SUB_SEEK_LEFT_THROUGH_MINUS)
        tb.add(State.SUB_SCAN_R, bl, bl, Direction.LEFT, State.SUB_CLEANUP_MINUS)  # rechts leer → cleanup

        # SUB_CLEANUP_MINUS: nach links bis '-' und löschen, dann ACCEPT
        tb.add_same(State.SUB_CLEANUP_MINUS, {'1', bl}, Direction.LEFT, State.SUB_CLEANUP_MINUS)
        tb.add(State.SUB_CLEANUP_MINUS, '-', bl, Direction.STAY, State.ACCEPT)

        # SUB_SEEK_LEFT_THROUGH_MINUS: gehe nach links bis '-'
        tb.add_same(State.SUB_SEEK_LEFT_THROUGH_MINUS, {'1', bl}, Direction.LEFT, State.SUB_SEEK_LEFT_THROUGH_MINUS)
        tb.add(State.SUB_SEEK_LEFT_THROUGH_MINUS, '-', '-', Direction.LEFT, State.SUB_MATCH_L)

        # SUB_MATCH_L: suche links eine '1' zum Löschen; BLANKs überspringen; '-'/'L' → keine linke '1' → REJECT
        tb.add(State.SUB_MATCH_L, '1', bl, Direction.RIGHT,
               State.SUB_RETURN_TO_R)  # linke 1 löschen und zurück nach rechts
        tb.add(State.SUB_MATCH_L, bl, bl, Direction.LEFT, State.SUB_MATCH_L)  # weiter nach links suchen
        tb.add(State.SUB_MATCH_L, 'L', 'L', Direction.STAY, State.REJECT)
        tb.add(State.SUB_MATCH_L, '-', '-', Direction.STAY, State.REJECT)

        # SUB_RETURN_TO_R: gehe nach rechts bis zur Markierung 'x'
        tb.add_same(State.SUB_RETURN_TO_R, {'1', '-', bl}, Direction.RIGHT, State.SUB_RETURN_TO_R)
        tb.add(State.SUB_RETURN_TO_R, 'x', 'x', Direction.STAY, State.SUB_UNMARK_DELETE_R)

        # SUB_UNMARK_DELETE_R: lösche die Markierung und springe in rechten Scan zurück
        tb.add(State.SUB_UNMARK_DELETE_R, {'x', '1'}, bl, Direction.RIGHT, State.SUB_SCAN_R)

        return tb.build()

    def _reject(self) -> None:
        """
        ZWECK
        -----
        Übergang in den Haltezustand REJECT ohne Nullmarker-Überlagerung.

        NEBENWIRKUNGEN
        --------------
        Setzt `result = ''` und `state = REJECT`.
        """
        self.result = ""
        self.state = State.REJECT

    def _trace_step(self) -> None:
        """
        ZWECK
        -----
        Protokolliert aktuelle Kopfposition und Zustand.

        RAHMEN
        ------
        Wird zu Beginn jeder Iteration und unmittelbar nach Setzen eines
        Haltezustands aufgerufen, damit externe Beobachter stets den
        normgerecht aktuellen Zustand sehen.
        """
        self.trace.append({"position": self.tape.head, "state": self.state.name})
