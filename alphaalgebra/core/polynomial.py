"""Canonical exact polynomials and conversion from the expression AST.

This module provides a small normalization substrate, not a theorem prover.
Only expressions denoting polynomials with non-negative integer powers are
accepted. Coefficients are exact fractions; no floating-point arithmetic is
performed.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import TypeAlias

from .ast import Add, Expr, Multiply, Power, Rational, Symbol

Monomial: TypeAlias = tuple[tuple[str, int], ...]


class UnsupportedPolynomialExpression(ValueError):
    """Raised when an AST expression is outside the polynomial fragment."""


def _validate_monomial(monomial: Monomial) -> Monomial:
    if not isinstance(monomial, tuple):
        raise TypeError("a monomial must be a tuple of (symbol, exponent) pairs")
    combined: dict[str, int] = {}
    for item in monomial:
        if not isinstance(item, tuple) or len(item) != 2:
            raise TypeError("monomial entries must be (symbol, exponent) pairs")
        name, exponent = item
        if not isinstance(name, str) or not name.strip():
            raise ValueError("monomial symbol names must be non-empty strings")
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("monomial exponents must be integers")
        if exponent < 0:
            raise ValueError("monomial exponents must be non-negative")
        if exponent:
            combined[name] = combined.get(name, 0) + exponent
    return tuple(sorted(combined.items()))


@dataclass(frozen=True, slots=True)
class Polynomial:
    """An immutable multivariate polynomial in canonical sparse form.

    Each term is a pair of (monomial, coefficient). A monomial is a sorted
    tuple of (symbol_name, nonnegative_exponent) pairs. Zero coefficients
    and duplicate monomials are removed/combined during construction.
    """

    terms: tuple[tuple[Monomial, Fraction], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.terms, tuple):
            raise TypeError("Polynomial.terms must be a tuple")
        combined: dict[Monomial, Fraction] = {}
        for item in self.terms:
            if not isinstance(item, tuple) or len(item) != 2:
                raise TypeError("polynomial terms must be (monomial, coefficient) pairs")
            monomial, coefficient = item
            canonical = _validate_monomial(monomial)
            if isinstance(coefficient, bool) or not isinstance(coefficient, (int, Fraction)):
                raise TypeError("polynomial coefficients must be integers or Fractions")
            exact = Fraction(coefficient)
            combined[canonical] = combined.get(canonical, Fraction(0)) + exact
        canonical_terms = tuple(
            (monomial, coefficient)
            for monomial, coefficient in sorted(combined.items())
            if coefficient
        )
        object.__setattr__(self, "terms", canonical_terms)

    @classmethod
    def constant(cls, value: int | Fraction) -> "Polynomial":
        if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
            raise TypeError("polynomial constants must be integers or Fractions")
        coefficient = Fraction(value)
        return cls((((), coefficient),)) if coefficient else cls(())

    @classmethod
    def variable(cls, name: str) -> "Polynomial":
        if not isinstance(name, str) or not name.strip():
            raise ValueError("variable name must be a non-empty string")
        return cls(((((name, 1),), Fraction(1)),))

    def __add__(self, other: "Polynomial") -> "Polynomial":
        if not isinstance(other, Polynomial):
            return NotImplemented
        return Polynomial(self.terms + other.terms)

    def __mul__(self, other: "Polynomial") -> "Polynomial":
        if not isinstance(other, Polynomial):
            return NotImplemented
        products: list[tuple[Monomial, Fraction]] = []
        for left_monomial, left_coefficient in self.terms:
            for right_monomial, right_coefficient in other.terms:
                products.append((
                    left_monomial + right_monomial,
                    left_coefficient * right_coefficient,
                ))
        return Polynomial(tuple(products))

    def __pow__(self, exponent: int) -> "Polynomial":
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("polynomial exponent must be an integer")
        if exponent < 0:
            raise ValueError("polynomial exponent must be non-negative")
        result = Polynomial.constant(1)
        factor = self
        power = exponent
        while power:
            if power & 1:
                result = result * factor
            power >>= 1
            if power:
                factor = factor * factor
        return result


def polynomial_from_expr(expression: Expr) -> Polynomial:
    """Expand and collect a supported AST expression exactly.

    Supported nodes: Rational, Symbol, Add, Multiply, and Power with a
    non-negative integer Rational exponent. Division, negative powers,
    symbolic powers, and other non-polynomial forms are rejected explicitly.
    """
    if isinstance(expression, Rational):
        return Polynomial.constant(expression.value)
    if isinstance(expression, Symbol):
        return Polynomial.variable(expression.name)
    if isinstance(expression, Add):
        result = Polynomial.constant(0)
        for term in expression.terms:
            result = result + polynomial_from_expr(term)
        return result
    if isinstance(expression, Multiply):
        result = Polynomial.constant(1)
        for factor in expression.factors:
            result = result * polynomial_from_expr(factor)
        return result
    if isinstance(expression, Power):
        if not isinstance(expression.exponent, Rational):
            raise UnsupportedPolynomialExpression(
                "polynomial powers require a rational integer exponent"
            )
        exponent = expression.exponent.value
        if exponent.denominator != 1 or exponent < 0:
            raise UnsupportedPolynomialExpression(
                "polynomial powers require a non-negative integer exponent"
            )
        return polynomial_from_expr(expression.base) ** exponent.numerator
    raise UnsupportedPolynomialExpression(
        f"unsupported expression node: {type(expression).__name__}"
    )
