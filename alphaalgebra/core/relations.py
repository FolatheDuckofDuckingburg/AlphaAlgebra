"""Typed relations between algebraic expressions."""

from dataclasses import dataclass

from .ast import Expr


@dataclass(frozen=True, slots=True)
class Relation:
    """Base class for a binary relation between two expressions."""

    left: Expr
    right: Expr

    def __post_init__(self) -> None:
        if not isinstance(self.left, Expr) or not isinstance(self.right, Expr):
            raise TypeError("relation sides must be Expr nodes")


class Equation(Relation):
    """The equality relation left = right."""


class LessThan(Relation):
    """The strict inequality left < right."""


class LessEqual(Relation):
    """The non-strict inequality left <= right."""


class GreaterThan(Relation):
    """The strict inequality left > right."""


class GreaterEqual(Relation):
    """The non-strict inequality left >= right."""
