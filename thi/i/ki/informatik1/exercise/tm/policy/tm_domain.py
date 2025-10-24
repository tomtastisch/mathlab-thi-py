"""
Turing Machine Domain für Operationsverkettung.

ZWECK
-----
Domain-Adapter für Planung von TM-Operationssequenzen.
Ermöglicht Suche nach optimalen Wegen von Start zu Ziel durch Verkettung von +, -, #.

DESIGN
------
- State: (n_left, n_right, step_count)
- Operationen: +, -, # mit korrekter Semantik
- Bidirektionale Suche: Forward und Backward möglich
- Lazy Expansion: Nur besuchte States werden materialisiert

MATHEMATISCHE BASIS
-------------------
- Addition: (n1, n2) → n1 + n2
- Subtraktion: (n1, n2) → n1 - n2  (nur wenn n1 >= n2)
- Exponentielles Doubling: (n1, n2) → n1 * 2^n2
"""

from dataclasses import dataclass
from typing import Literal
from thi.i.ki.util.policy.domain import Domain
from thi.i.ki.util.policy.skeleton import GraphSkeleton
from thi.i.ki.util.policy.types import State, Action


@dataclass(frozen=True, slots=True)
class TMState:
    """
    Zustand für TM-Verkettungsplanung.

    ATTRIBUTE
    ---------
    n_left : int
        Linker Operand (in unär: Anzahl '1' links vom Operator).

    n_right : int
        Rechter Operand (in unär: Anzahl '1' rechts vom Operator).

    step_count : int
        Anzahl bisheriger Operationen (für Optimierung).
        Optional, kann auch 0 bleiben wenn nur Makro-Ops gezählt werden.

    INVARIANTEN
    -----------
    - n_left >= 0
    - n_right >= 0
    - step_count >= 0

    BEISPIEL
    --------
    >>> state = TMState(n_left=3, n_right=2, step_count=0)
    >>> # Nach Addition: TMState(5, 0, 1)
    """
    n_left: int
    n_right: int
    step_count: int = 0

    def __post_init__(self):
        """Validierung der Invarianten."""
        if self.n_left < 0:
            raise ValueError(f"n_left muss >= 0 sein, ist {self.n_left}")
        if self.n_right < 0:
            raise ValueError(f"n_right muss >= 0 sein, ist {self.n_right}")
        if self.step_count < 0:
            raise ValueError(f"step_count muss >= 0 sein, ist {self.step_count}")


class TMDomain:
    """
    Domain für Turing Machine Operationsverkettung.

    ZWECK
    -----
    Plant Sequenzen von TM-Operationen um von Start zu Ziel zu gelangen.

    VERWENDUNG
    ----------
    >>> # Von (3, 2) nach 32
    >>> domain = TMDomain(start_n1=3, start_n2=2, target=32)
    >>> skeleton = domain.build_skeleton()
    >>> policy = BellmanPolicy(skeleton)
    >>>
    >>> # Vollständiger Pfad
    >>> path = policy.get_full_path(TMState(3, 2, 0))
    >>> for action, state in path:
    ...     print(f"{action}: {state}")

    OPERATIONEN
    -----------
    "+": Addition - (n1, n2) → (n1 + n2, 0)
    "-": Subtraktion - (n1, n2) → (n1 - n2, 0) falls n1 >= n2
    "#": Exponentielles Doubling - (n1, n2) → (n1 * 2^n2, 0)

    Nach jeder Operation ist n_right = 0!

    PARAMETER
    ---------
    start_n1 : int
        Initialer linker Operand.

    start_n2 : int
        Initialer rechter Operand.

    target : int
        Zielwert (wenn n_left == target und n_right == 0).

    ops : tuple[str, ...]
        Erlaubte Operationen. Default: ("+", "-", "#")

    max_value : int
        Obere Schranke für Werte (Explosion-Prevention).
        Default: 10000

    cost_mode : Literal["uniform", "realistic"]
        Kostenmodell:
        - "uniform": Alle Ops kosten 1
        - "realistic": Kosten approximieren Mikroschritte

    VORAUSSETZUNGEN
    ---------------
    - start_n1, start_n2 >= 0
    - target > 0
    - ops nicht leer

    BEISPIELE
    ---------
    # Einfache Addition:
    >>> domain = TMDomain(3, 2, target=5)
    >>> # Lösung: ["+"] → (3, 2) → (5, 0)

    # Komplexe Verkettung:
    >>> domain = TMDomain(3, 2, target=32)
    >>> # Mögliche Lösung: ["-", "#", "#", "#", "#", "#"]
    >>> # (3, 2) → (1, 0) → (2, 0) → (4, 0) → (8, 0) → (16, 0) → (32, 0)
    """

    def __init__(
            self,
            start_n1: int,
            start_n2: int,
            target: int,
            ops: tuple[str, ...] = ("+", "-", "#"),
            max_value: int = 10000,
            cost_mode: Literal["uniform", "realistic"] = "uniform"
    ):
        """Initialisiert TM-Domain."""
        if start_n1 < 0 or start_n2 < 0:
            raise ValueError("start_n1 und start_n2 müssen >= 0 sein")
        if target <= 0:
            raise ValueError("target muss > 0 sein")
        if not ops:
            raise ValueError("ops darf nicht leer sein")

        self.start_n1 = start_n1
        self.start_n2 = start_n2
        self.target = target
        self.ops = ops
        self.max_value = max_value
        self.cost_mode = cost_mode

    def initial_state(self) -> TMState:
        """Gibt initialen Zustand zurück."""
        return TMState(self.start_n1, self.start_n2, 0)

    def build_skeleton(self) -> GraphSkeleton:
        """
        Erzeugt GraphSkeleton für Bellman-Policy.

        STRATEGIE
        ---------
        - Direction: "bidirectional" (für TM optimal)
        - Cost-Type: "uniform" oder "zero_one" je nach cost_mode
        - Max-States: Begrenzt durch max_value

        RÜCKGABE
        --------
        GraphSkeleton mit allen nötigen Callbacks.
        """
        return GraphSkeleton(
            is_goal=self._is_goal,
            successors=self._successors,
            predecessors=self._predecessors,
            initial_states=(self.initial_state(),),
            direction="bidirectional",
            cost_type="uniform" if self.cost_mode == "uniform" else "zero_one",
            max_states=self.max_value * 10,  # Großzügige Schranke
            domain_name=f"TM({self.start_n1},{self.start_n2}→{self.target})",
            metadata={
                "ops": self.ops,
                "cost_mode": self.cost_mode,
            }
        )

    def _is_goal(self, state: TMState) -> bool:
        """
        Prüft, ob Ziel erreicht.

        BEDINGUNG
        ---------
        n_left == target UND n_right == 0
        (n_right muss 0 sein, da nach jeder Op n_right=0)
        """
        return state.n_left == self.target and state.n_right == 0

    def _successors(self, state: TMState):
        """
        Generiert alle möglichen Nachfolger-Zustände.

        SEMANTIK
        --------
        - "+": (n1, n2) → (n1 + n2, 0)
        - "-": (n1, n2) → (n1 - n2, 0) nur wenn n1 >= n2
        - "#": (n1, n2) → (n1 * 2^n2, 0)

        Nach jeder Operation ist n_right = 0!
        """
        n1, n2, steps = state.n_left, state.n_right, state.step_count

        # Addition
        if "+" in self.ops:
            result = n1 + n2
            if result <= self.max_value:
                yield (
                    TMState(result, 0, steps + 1),
                    "+",
                    self._cost(state, "+")
                )

        # Subtraktion (nur wenn n1 >= n2)
        if "-" in self.ops and n1 >= n2:
            result = n1 - n2
            if result >= 0:
                yield (
                    TMState(result, 0, steps + 1),
                    "-",
                    self._cost(state, "-")
                )

        # Exponentielles Doubling: n1 * 2^n2
        if "#" in self.ops:
            # Schutz gegen Overflow
            if n2 <= 20:  # 2^20 = ~1M
                result = n1 * (2 ** n2)
                if result <= self.max_value:
                    yield (
                        TMState(result, 0, steps + 1),
                        "#",
                        self._cost(state, "#")
                    )

    def _predecessors(self, state: TMState):
        """
        Generiert alle möglichen Vorgänger-Zustände.

        STRATEGIE
        ---------
        Inverse Operationen mit Bounds für Explosion-Prevention.

        HINWEIS
        -------
        Predecessors sind nicht immer exakt eindeutig (z.B. bei Addition).
        Wir generieren plausible Vorgänger bis max_value.
        """
        n1, n2, steps = state.n_left, state.n_right, state.step_count

        # Nur States mit n_right=0 können Nachfolger einer Operation sein
        if n2 != 0:
            return

        if steps > 0:
            prev_steps = steps - 1
        else:
            prev_steps = 0

        # Inverse Addition: (n1, 0) kam von (a, b) mit a + b = n1
        if "+" in self.ops:
            for a in range(min(n1 + 1, self.max_value)):
                b = n1 - a
                if 0 <= b <= self.max_value:
                    yield (
                        TMState(a, b, prev_steps),
                        "+",
                        self._cost(TMState(a, b, prev_steps), "+")
                    )

        # Inverse Subtraktion: (n1, 0) kam von (a, b) mit a - b = n1
        if "-" in self.ops:
            # a = n1 + b, b kann beliebig sein
            for b in range(1, min(self.max_value - n1, 100)):  # Begrenzt auf 100 Vorgänger
                a = n1 + b
                if a <= self.max_value:
                    yield (
                        TMState(a, b, prev_steps),
                        "-",
                        self._cost(TMState(a, b, prev_steps), "-")
                    )

        # Inverse Doubling: (n1, 0) kam von (a, b) mit a * 2^b = n1
        if "#" in self.ops:
            # n1 = a * 2^b → a = n1 / 2^b
            for b in range(min(n1.bit_length() + 1, 20)):  # Max 20 Bit-Shifts
                if n1 % (2 ** b) == 0:
                    a = n1 // (2 ** b)
                    if 0 < a <= self.max_value:
                        yield (
                            TMState(a, b, prev_steps),
                            "#",
                            self._cost(TMState(a, b, prev_steps), "#")
                        )

    def _cost(self, state: TMState, op: str) -> int:
        """
        Kostenmodell für Operationen.

        MODI
        ----
        uniform: Alle Ops kosten 1 (Makro-Ops zählen)

        realistic: Approximation der Mikroschritte (TODO):
            - "+": O(1) (nur '+' löschen)
            - "-": O(n2) (Iterationen)
            - "#": O(n1 * n2) (exponentielles Kopieren)

        RÜCKGABE
        --------
        int: Kosten >= 0
        """
        if self.cost_mode == "uniform":
            return 1
        else:
            # Realistische Kosten (vereinfacht)
            if op == "+":
                return 1  # Rasant
            elif op == "-":
                return max(1, state.n_right // 10)  # Proportional zu Iterationen
            elif op == "#":
                return max(1, state.n_left // 100)  # Proportional zu Kopiervorgängen
            else:
                return 1