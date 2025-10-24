"""
Policy-Engine für diskrete Optimierungsprobleme.

ZWECK
-----
Wiederverwendbare Bellman-Policy-Engine für beliebige Domains.
Unterstützt verschiedene Such-Algorithmen und lazy State-Expansion.

HAUPTKOMPONENTEN
----------------
- GraphSkeleton: Abstrakte Problem-Repräsentation
- BellmanPolicy: Universelle Policy-Engine
- Domain-Protocol: Schnittstelle für Problem-Domains

VERWENDUNG
----------
>>> from thi.i.ki.util.policy import BellmanPolicy
>>> from thi.i.ki.informatik1.exercise.tm.policy import TMDomain
>>>
>>> domain = TMDomain(start=(3, 2), target=32)
>>> policy = BellmanPolicy(domain.build_skeleton())
>>> action, next_state = policy.step(current_state)

ERWEITERBARKEIT
---------------
Neue Domains fügen einfach build_skeleton() hinzu.
Keine Vererbung, kein Boilerplate nötig.
"""

from .skeleton import GraphSkeleton
from .policy import BellmanPolicy
from .domain import Domain

__all__ = [
    "GraphSkeleton",
    "BellmanPolicy",
    "Domain",
]