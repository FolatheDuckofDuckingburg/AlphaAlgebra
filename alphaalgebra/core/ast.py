"""A small immutable AST for exact algebraic expressions."""

from dataclasses import dataclass
from fractions import Fraction
from typing import TypeAlias


class Expr:
    """Base class for all algebraic expression nodes."""


@dataclass(frozen=True, slots=True)
class Rational(Expr):
    """An exact rational number represented by fractions.Fraction."""

    value: Fraction

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, (int, Fraction)):
            raise TypeError("Rational.value must be an int or fractions.Fraction")
        object.__setattr__(self, "value", Fraction(self.value))

    @classmethod
    def from_parts(cls, numerator: int, denominator: int = 1) -> "Rational":
        if isinstance(numerator, bool) or isinstance(denominator, bool):
            raise TypeError("Rational parts must be integers")
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise TypeError("Rational parts must be integers")
        if denominator == 0:
            raise ZeroDivisionError("a rational denominator cannot be zero")
        return cls(Fraction(numerator, denominator))


@dataclass(frozen=True, slots=True)
class Symbol(Expr):
    """A named algebraic variable."""

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("symbol name must be a non-empty string")


@dataclass(frozen=True, slots=True)
class Add(Expr):
    """An unevaluated sum; normalization is a separate future operation."""

    terms: tuple[Expr, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.terms, tuple):
            object.__setattr__(self, "terms", tuple(self.terms))
        if len(self.terms) < 2:
            raise ValueError("Add requires at least two terms")
        if not all(isinstance(term, Expr) for term in self.terms):
            raise TypeError("every Add term must be an Expr")


@dataclass(frozen=True, slots=True)
class Multiply(Expr):
    """An unevaluated product; normalization is a separate future operation."""

    factors: tuple[Expr, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.factors, tuple):
            object.__setattr__(self, "factors", tuple(self.factors))
        if len(self.factors) < 2:
            raise ValueError("Multiply requires at least two factors")
        if not all(isinstance(factor, Expr) for factor in self.factors):
            raise TypeError("every Multiply factor must be an Expr")


@dataclass(frozen=True, slots=True)
class Power(Expr):
    """An unevaluated power with an expression base and exponent."""

    base: Expr
    exponent: Expr

    def __post_init__(self) -> None:
        if not isinstance(self.base, Expr) or not isinstance(self.exponent, Expr):
            raise TypeError("Power base and exponent must be Expr nodes")


Expression: TypeAlias = Rational | Symbol | Add | Multiply | Power
