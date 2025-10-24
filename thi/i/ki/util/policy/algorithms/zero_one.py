"""
0/1-BFS Algorithmus für Graphen mit Kosten 0 oder 1.

ZWECK
-----
Effiziente Kürzeste-Pfad-Berechnung für Graphen, bei denen alle Kanten
Kosten 0 oder 1 haben. Schneller als Dijkstra für diesen Spezialfall.

ALGORITHMUS
-----------
Nutzt Deque mit zwei Prioritäten:
- Kosten 0: appendleft (höhere Priorität)
- Kosten 1: append (normale Priorität)

KOMPLEXITÄT
-----------
O(V + E) - Linear in Anzahl Knoten und Kanten.

REFERENZEN
----------
- 0-1 BFS: https://codeforces.com/blog/entry/22276
"""

from collections import deque
from typing import Iterable
from ..types import State, Action, Cost, SuccessorsFunc, PredecessorsFunc


def zero_one_bfs_backward(
        goal_states: Iterable[State],
        predecessors: PredecessorsFunc,
        max_states: int | None = None
) -> tuple[dict[State, Cost], dict[State, tuple[State, Action]]]:
    """
    0/1-BFS rückwärts von Zielzuständen.

    ZWECK
    -----
    Berechnet kürzeste Distanzen von allen erreichbaren States zu den Zielzuständen.
    Optimal für Bellman-Policy, da alle erreichbaren States abgedeckt werden.

    ALGORITHMUS
    -----------
    1. Seeds: goal_states mit dist=0
    2. Deque: 0-Kosten links (appendleft), 1-Kosten rechts (append)
    3. Relaxation: dist[prev] = min(dist[prev], dist[cur] + cost)
    4. Parent-Tracking für Pfad-Rekonstruktion

    PARAMETER
    ---------
    goal_states : Iterable[State]
        Start der Rückwärtssuche (typischerweise Zielzustände).

    predecessors : PredecessorsFunc
        Callback für Vorgänger: state → [(prev_state, action, cost), ...]

    max_states : int | None
        Optional: Abbruch bei zu vielen States (Explosion-Prevention).

    RÜCKGABE
    --------
    (distances, parents) : tuple
        - distances[state] → minimale Distanz zum nächsten Ziel
        - parents[state] → (next_state, action) für Forward-Rekonstruktion

    VORAUSSETZUNGEN
    ---------------
    - Alle Kosten müssen 0 oder 1 sein (ValueError sonst)
    - Graph muss endlich sein (oder max_states gesetzt)

    FEHLERVERHALTEN
    ---------------
    ValueError wenn cost nicht in {0, 1}.

    BEISPIEL
    --------
    >>> def preds(s):
    ...     if s == 5: yield (3, "add", 1)
    ...     if s == 5: yield (2, "add", 1)
    >>> dist, parents = zero_one_bfs_backward([5], preds)
    >>> dist[3]  # Distanz von 3 zum Ziel 5
    1
    """
    dist: dict[State, Cost] = {}
    parent: dict[State, tuple[State, Action]] = {}
    queue = deque()

    # Seeds: Zielzustände mit Distanz 0
    for state in goal_states:
        dist[state] = 0
        queue.append(state)

    expanded = 0

    while queue:
        # Abbruch bei zu vielen States
        if max_states and expanded >= max_states:
            break

        state = queue.popleft()
        expanded += 1

        # Alle Vorgänger expandieren
        for prev_state, action, cost in predecessors(state):
            # Kosten-Validierung
            if cost not in (0, 1):
                raise ValueError(
                    f"0/1-BFS erwartet Kosten 0 oder 1, bekam {cost} "
                    f"für Transition {prev_state} --[{action}]→ {state}"
                )

            new_dist = dist[state] + cost

            # Relaxation: Wenn neuer Pfad kürzer
            if prev_state not in dist or new_dist < dist[prev_state]:
                dist[prev_state] = new_dist
                parent[prev_state] = (state, action)

                # Priorität: 0-Kosten → vorne (höhere Priorität)
                if cost == 0:
                    queue.appendleft(prev_state)
                else:
                    queue.append(prev_state)

    return dist, parent


def zero_one_bfs_forward(
        initial_states: Iterable[State],
        successors: SuccessorsFunc,
        max_states: int | None = None
) -> tuple[dict[State, Cost], dict[State, tuple[State, Action]]]:
    """
    0/1-BFS vorwärts von Startzuständen.

    ZWECK
    -----
    Berechnet kürzeste Distanzen von Startzuständen zu allen erreichbaren States.
    Nützlich für Forward-Only-Suche (wenn Backward nicht möglich).

    ALGORITHMUS
    -----------
    Analog zu backward, aber mit successors statt predecessors.

    PARAMETER
    ---------
    initial_states : Iterable[State]
        Startzustände der Vorwärtssuche.

    successors : SuccessorsFunc
        Callback für Nachfolger: state → [(next_state, action, cost), ...]

    max_states : int | None
        Optional: Abbruch bei zu vielen States.

    RÜCKGABE
    --------
    (distances, parents) : tuple
        - distances[state] → minimale Distanz vom Start
        - parents[state] → (prev_state, action) für Pfad-Rekonstruktion

    VORAUSSETZUNGEN
    ---------------
    - Alle Kosten müssen 0 oder 1 sein
    - Graph muss endlich sein (oder max_states gesetzt)

    FEHLERVERHALTEN
    ---------------
    ValueError wenn cost nicht in {0, 1}.

    BEISPIEL
    --------
    >>> def succs(s):
    ...     yield (s + 1, "inc", 1)
    ...     yield (s * 2, "double", 1)
    >>> dist, parents = zero_one_bfs_forward([1], succs, max_states=100)
    >>> dist[10]  # Distanz von 1 nach 10
    4
    """
    dist: dict[State, Cost] = {}
    parent: dict[State, tuple[State, Action]] = {}
    queue = deque()

    # Seeds: Startzustände mit Distanz 0
    for state in initial_states:
        dist[state] = 0
        queue.append(state)

    expanded = 0

    while queue:
        if max_states and expanded >= max_states:
            break

        state = queue.popleft()
        expanded += 1

        # Alle Nachfolger expandieren
        for next_state, action, cost in successors(state):
            if cost not in (0, 1):
                raise ValueError(
                    f"0/1-BFS erwartet Kosten 0 oder 1, bekam {cost} "
                    f"für Transition {state} --[{action}]→ {next_state}"
                )

            new_dist = dist[state] + cost

            if next_state not in dist or new_dist < dist[next_state]:
                dist[next_state] = new_dist
                parent[next_state] = (state, action)

                if cost == 0:
                    queue.appendleft(next_state)
                else:
                    queue.append(next_state)

    return dist, parent