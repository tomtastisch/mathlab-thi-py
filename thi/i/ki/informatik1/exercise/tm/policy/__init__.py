"""
Turing Machine Domain für Policy-basierte Operationsverkettung.

ZWECK
-----
Ermöglicht Planung von Operationssequenzen für mathematische Konstruktionen.
Nutzt die generische Bellman-Policy-Engine.

HAUPTKOMPONENTE
---------------
TMDomain: Domain-Adapter für TM-Verkettungen

VERWENDUNG
----------
>>> from thi.i.ki.informatik1.exercise.tm.policy import TMDomain
>>> from thi.i.ki.util.policy import BellmanPolicy
>>>
>>> # Von (3, 2) zu Zielwert 32
>>> domain = TMDomain(start_n1=3, start_n2=2, target=32, ops=("+", "-", "#"))
>>> policy = BellmanPolicy(domain.build_skeleton())
>>>
>>> # Beste Aktion vom Start
>>> action, next_state = policy.step(domain.initial_state())

HINWEIS
-------
Dies ist für VERKETTUNGEN von Operationen, nicht für einzelne TM-Ausführungen.
Die bestehende TuringMachine-Klasse bleibt unverändert.
"""

from .tm_domain import TMDomain, TMState

__all__ = [
    "TMDomain",
    "TMState",
]