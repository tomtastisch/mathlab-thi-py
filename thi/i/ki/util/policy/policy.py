"""
Policy-Engine mit Strategy Pattern.

ZWECK
-----
Koordiniert Algorithmus-Wahl und Action-Selektion.
Bietet einheitliche API unabhängig vom verwendeten Algorithmus.

DESIGN
------
- Composition over Inheritance: Kein Vererbungsbaum
- Strategy Pattern: Algorithmus zur Laufzeit wählbar
- Stateless: Policy speichert keine Laufzeit-States
- Single Responsibility: Nur Action-Selektion
"""

from typing import Protocol
from .skeleton import GraphSkeleton
from .types import State, Action, Cost
from .algorithms import zero_one_bfs_backward, zero_one_bfs_forward


class PolicyStrategy(Protocol):
    """
    Protocol für Algorithmus-Strategien.

    ZWECK
    -----
    Ermöglicht pluggbare Algorithmen ohne Vererbung.
    Jede Strategie implementiert compute() und liefert Distanzen + Parents.
    """

    def compute(
            self,
            skeleton: GraphSkeleton
    ) -> tuple[dict[State, Cost], dict[State, tuple[State, Action]]]:
        """
        Berechnet Distanzen und Parent-Pointer.

        RÜCKGABE
        --------
        (distances, parents) : tuple
            - distances[state] → minimale Distanz zum Ziel
            - parents[state] → (next_state, action) für Pfad-Rekonstruktion
        """
        ...


class BellmanPolicy:
    """
    Universelle Policy-Engine mit pluggbaren Algorithmen.

    ZWECK
    -----
    - Wählt automatisch optimalen Algorithmus basierend auf Skeleton-Metadata
    - Oder akzeptiert manuell gewählten Algorithmus
    - Bietet einheitliche API für Action-Selektion

    DESIGN
    ------
    - Keine Vererbungs-Hierarchie
    - Strategy Pattern: Algorithmus ist austauschbar
    - Single Responsibility: Nur Action-Selektion, keine Suche

    VERWENDUNG
    ----------
    >>> # Automatische Strategie-Wahl:
    >>> policy = BellmanPolicy(skeleton)

    >>> # Manuelle Strategie:
    >>> policy = BellmanPolicy(skeleton, strategy=MyStrategy())

    >>> # Action-Selektion:
    >>> action, next_state = policy.step(current_state)
    >>> dist = policy.distance(current_state)
    >>> path = policy.get_full_path(current_state)

    ATTRIBUTE
    ---------
    skeleton : GraphSkeleton
        Problem-Definition.

    _dist : dict[State, Cost]
        Berechnete Distanzen zu Zielen.

    _next_action : dict[State, Action]
        Vorberechnete optimale Aktionen.

    VORAUSSETZUNGEN
    ---------------
    - skeleton.validate() muss erfolgreich sein
    - Skeleton muss endlichen Graph beschreiben (oder Bounds setzen)
    """

    def __init__(
            self,
            skeleton: GraphSkeleton,
            strategy: PolicyStrategy | None = None,
            verbose: bool = False
    ):
        """
        Initialisiert Policy und berechnet optimale Aktionen.
        
        PARAMETER
        ---------
        skeleton : GraphSkeleton
            Problem-Repräsentation.

        strategy : PolicyStrategy | None
            Optional: Manuell gewählter Algorithmus.
            Falls None: automatische Wahl basierend auf skeleton.cost_type.

        verbose : bool
            Aktiviert Logging für Debugging (aktuell ungenutzt).

        FEHLERVERHALTEN
        ---------------
        ValueError wenn skeleton.validate() fehlschlägt.
        """
        # Validierung
        skeleton.validate()

        self.skeleton = skeleton
        self.verbose = verbose

        # Strategie wählen (automatisch oder manuell)
        if strategy is None:
            strategy = self._auto_select_strategy()

        self._strategy = strategy

        # Policy berechnen
        self._dist, self._parent = self._strategy.compute(skeleton)

        # Forward-Aktionen vorberechnen
        self._next_action: dict[State, Action] = {}
        self._compute_forward_actions()

    def _auto_select_strategy(self) -> PolicyStrategy:
        """
        Wählt optimalen Algorithmus basierend auf Skeleton-Metadata.

        ENTSCHEIDUNGSLOGIK
        ------------------
        - cost_type="zero_one" + direction="backward" → 0/1-BFS backward
        - cost_type="zero_one" + direction="forward" → 0/1-BFS forward
        - cost_type="uniform" → Spezialfall von 0/1-BFS
        - cost_type="arbitrary" → TODO: Dijkstra (aktuell Fallback auf 0/1)

        RÜCKGABE
        --------
        PolicyStrategy
            Konkrete Strategie-Instanz.
        """
        if self.skeleton.cost_type in ("zero_one", "uniform"):
            if self.skeleton.direction == "backward":
                return ZeroOneBFSBackwardStrategy()
            else:
                return ZeroOneBFSForwardStrategy()
        else:
            # TODO: Dijkstra für arbitrary costs
            # Fallback auf 0/1-BFS (wird validiert)
            if self.skeleton.direction == "backward":
                return ZeroOneBFSBackwardStrategy()
            else:
                return ZeroOneBFSForwardStrategy()

    def _compute_forward_actions(self):
        """
        Berechnet für jeden State die nächste optimale Aktion.

        ALGORITHMUS
        -----------
        Für jeden State s mit dist[s] < inf:
            Durchsuche alle Nachfolger ns
            Finde ns wo dist[ns] + cost(s→ns) == dist[s]
            Speichere action(s→ns) als nächste Aktion

        KONSISTENZ
        ----------
        Verwendet die ERSTE passende Aktion (deterministisch durch Successor-Reihenfolge).

        NEBENWIRKUNGEN
        --------------
        Füllt self._next_action Dictionary.
        """
        for state in self._dist:
            # Zielzustände haben keine nächste Aktion
            if self.skeleton.is_goal(state):
                continue

            # Finde passenden Nachfolger
            for next_state, action, cost in self.skeleton.successors(state):
                if next_state in self._dist:
                    # Prüfe ob dieser Nachfolger auf optimalem Pfad liegt
                    expected_dist = self._dist[next_state] + cost
                    if expected_dist == self._dist[state]:
                        self._next_action[state] = action
                        break  # Erste passende Aktion (deterministisch)

    def step(self, state: State, update: bool = False) -> tuple[Action | None, State]:
        """
        Gibt optimale Aktion und Nachfolgezustand zurück.

        ZWECK
        -----
        Kern-API für schrittweise Ausführung.
        Liefert nächste optimale Aktion vom aktuellen State.

        PARAMETER
        ---------
        state : State
            Aktueller Zustand.

        update : bool
            Reserviert für zukünftige Stateful-Features.
            Aktuell ignoriert (Policy ist stateless).

        RÜCKGABE
        --------
        (action, next_state) : tuple
            - action: Optimale Aktion (None falls Ziel erreicht/unerreichbar)
            - next_state: Nachfolgezustand nach Ausführung von action

        FEHLERVERHALTEN
        ---------------
        Keine Exception. Gibt (None, state) zurück wenn:
        - Ziel erreicht
        - State unerreichbar
        - State unbekannt

        BEISPIEL
        --------
        >>> state = initial_state
        >>> while not skeleton.is_goal(state):
        ...     action, state = policy.step(state)
        ...     if action is None:
        ...         break
        ...     print(f"Execute {action}")
        """
        # Ziel erreicht
        if self.skeleton.is_goal(state):
            return (None, state)

        # Unerreichbar oder unbekannt
        if state not in self._next_action:
            return (None, state)

        action = self._next_action[state]

        # Finde Nachfolgezustand durch Successor-Lookup
        next_state = state
        for ns, a, _ in self.skeleton.successors(state):
            if a == action:
                next_state = ns
                break

        return (action, next_state)

    def distance(self, state: State) -> Cost:
        """
        Gibt Distanz zum nächsten Ziel zurück.

        RÜCKGABE
        --------
        int
            Minimale Anzahl Schritte zum Ziel.
            float('inf') falls unerreichbar.

        BEISPIEL
        --------
        >>> policy.distance(start_state)
        5
        >>> policy.distance(unreachable_state)
        inf
        """
        return self._dist.get(state, float('inf'))

    def has_path(self, state: State) -> bool:
        """
        Prüft, ob es einen Pfad zum Ziel gibt.

        RÜCKGABE
        --------
        bool
            True wenn State erreichbar und Pfad existiert.

        BEISPIEL
        --------
        >>> policy.has_path(start_state)
        True
        >>> policy.has_path(isolated_state)
        False
        """
        return state in self._dist

    def get_full_path(self, state: State) -> list[tuple[Action, State]]:
        """
        Rekonstruiert vollständigen Pfad zum Ziel.

        ZWECK
        -----
        Liefert komplette Aktions-Sequenz vom gegebenen State zum Ziel.
        Nützlich für Planung und Visualisierung.

        PARAMETER
        ---------
        state : State
            Startzustand für Pfad-Rekonstruktion.

        RÜCKGABE
        --------
        list[tuple[Action, State]]
            Sequenz von (action, resulting_state) bis Ziel erreicht.
            Leere Liste falls kein Pfad existiert.

        BEISPIEL
        --------
        >>> path = policy.get_full_path(start_state)
        >>> for action, resulting_state in path:
        ...     print(f"{action} → {resulting_state}")
        add_1 → State(1)
        add_1 → State(2)
        double → State(4)
        """
        path = []
        current = state
        max_steps = 10000  # Schutz gegen Zyklen

        for _ in range(max_steps):
            if self.skeleton.is_goal(current):
                break

            action, next_state = self.step(current)
            if action is None:
                break

            path.append((action, next_state))
            current = next_state

        return path


# ==================== Konkrete Strategien ====================

class ZeroOneBFSBackwardStrategy:
    """0/1-BFS Backward-Strategie."""

    def compute(self, skeleton: GraphSkeleton):
        if skeleton.predecessors is None:
            raise ValueError("Backward-Strategie braucht predecessors")

        return zero_one_bfs_backward(
            skeleton.initial_states,
            skeleton.predecessors,
            skeleton.max_states
        )


class ZeroOneBFSForwardStrategy:
    """0/1-BFS Forward-Strategie."""

    def compute(self, skeleton: GraphSkeleton):
        return zero_one_bfs_forward(
            skeleton.initial_states,
            skeleton.successors,
            skeleton.max_states
        )