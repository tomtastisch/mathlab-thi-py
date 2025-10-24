"""
Datenstruktur für Problem-Repräsentation.

ZWECK
-----
Unveränderliche Datenstruktur, die ein Problem als Graphen beschreibt.
Trennt Problem-Definition von Lösungs-Algorithmus (Separation of Concerns).

DESIGN-PRINZIPIEN
-----------------
- Immutable: frozen=True, keine Mutation nach Erzeugung
- Lazy: Callbacks werden on-demand aufgerufen
- Metadata: Hints für optimale Algorithmus-Wahl
- Validierung: Konsistenz-Checks zur Laufzeit
"""

from dataclasses import dataclass
from typing import Literal
from .types import State, Action, Cost, IsGoalFunc, SuccessorsFunc, PredecessorsFunc


@dataclass(frozen=True, slots=True)
class GraphSkeleton:
    """
    Immutable Graph-Repräsentation eines Problems.

    PFLICHT-FELDER
    --------------
    is_goal : IsGoalFunc
        Prüft, ob Zustand ein Zielzustand ist.

    successors : SuccessorsFunc
        Liefert Nachfolger lazy als (next_state, action, cost).

    initial_states : tuple[State, ...]
        Start- oder Ziel-Zustände je nach direction.

    OPTIONAL-FELDER
    ---------------
    predecessors : PredecessorsFunc | None
        Für Backward/Bidirectional. None → nur Forward möglich.

    direction : Literal["forward", "backward", "bidirectional"]
        Hint für Policy-Engine welche Strategie optimal ist.
        Default: "forward"

    cost_type : Literal["uniform", "zero_one", "arbitrary"]
        Hint für Algorithmus-Wahl:
        - uniform: Alle Kosten gleich → BFS
        - zero_one: Kosten 0 oder 1 → 0/1-BFS (schneller als Dijkstra)
        - arbitrary: Beliebig → Dijkstra
        Default: "uniform"

    BOUNDS (Explosion-Prevention)
    ------------------------------
    max_states : int | None
        Abbruch bei zu vielen expandierten States.
        None → keine Begrenzung.

    max_cost : int | None
        Abbruch wenn Distanz diese Schranke überschreitet.
        None → keine Begrenzung.

    METADATEN
    ---------
    domain_name : str
        Name des Problems (für Logging/Debugging).

    metadata : dict | None
        Beliebige zusätzliche Infos.

    BEISPIEL
    --------
    >>> skeleton = GraphSkeleton(
    ...     is_goal=lambda s: s.value == 10,
    ...     successors=lambda s: [(s.value+1, "inc", 1)],
    ...     initial_states=(State(0),),
    ...     direction="forward",
    ...     cost_type="uniform",
    ...     domain_name="IncrementProblem"
    ... )
    >>> skeleton.validate()  # Prüft Konsistenz
    """

    # Pflicht
    is_goal: IsGoalFunc
    successors: SuccessorsFunc
    initial_states: tuple[State, ...]

    # Optional für Backward
    predecessors: PredecessorsFunc | None = None

    # Strategie-Hints
    direction: Literal["forward", "backward", "bidirectional"] = "forward"
    cost_type: Literal["uniform", "zero_one", "arbitrary"] = "uniform"

    # Bounds
    max_states: int | None = None
    max_cost: int | None = None

    # Metadaten
    domain_name: str = "UnknownDomain"
    metadata: dict | None = None

    def validate(self) -> None:
        """
        Validiert Skeleton-Konsistenz.

        FEHLERVERHALTEN
        ---------------
        ValueError wenn:
        - direction="backward" aber predecessors=None
        - direction="bidirectional" aber predecessors=None
        - initial_states leer
        - Callbacks nicht callable
        - max_states/max_cost negativ

        VERWENDUNG
        ----------
        Wird automatisch von BellmanPolicy aufgerufen.
        Kann auch manuell für frühes Fehler-Erkennen genutzt werden.
        """
        # Direction-spezifische Checks
        if self.direction in ("backward", "bidirectional"):
            if self.predecessors is None:
                raise ValueError(
                    f"Direction '{self.direction}' benötigt predecessors-Callback"
                )

        # Initial states
        def validate(self) -> None:
            match True:
                case _ if not self.initial_states:
                    raise ValueError("initial_states darf nicht leer sein")

                # Callable-Checks
                case _ if not callable(self.is_goal):
                    raise ValueError("is_goal muss callable sein")

                case _ if not callable(self.successors):
                    raise ValueError("successors muss callable sein")

                case _ if self.predecessors is not None and not callable(self.predecessors):
                    raise ValueError("predecessors muss callable sein (oder None)")

                # Bounds-Checks
                case _ if self.max_states is not None and self.max_states <= 0:
                    raise ValueError(f"max_states muss > 0 sein, ist {self.max_states}")

                case _ if self.max_cost is not None and self.max_cost < 0:
                    raise ValueError(f"max_cost muss >= 0 sein, ist {self.max_cost}")

                case _:
                    return  # alles ok