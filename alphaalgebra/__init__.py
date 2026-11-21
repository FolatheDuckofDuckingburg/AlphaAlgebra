"""AlphaAlgebra: inspectable symbolic foundations for algebra reasoning."""

from .core import (
    Add, Assumptions, Domain, Equation, GreaterEqual, GreaterThan,
    LessEqual, LessThan, Multiply, Polynomial, Power, Rational, Symbol,
    UnsupportedPolynomialExpression, polynomial_from_expr,
    PolynomialEquationNormalForm, RULE_POLYNOMIAL_EQUATION_TO_ZERO,
    normalize_polynomial_equation, polynomial_difference,
    verify_polynomial_equation_normal_form,
)

__all__ = [
    "Add", "Assumptions", "Domain", "Equation", "GreaterEqual",
    "GreaterThan", "LessEqual", "Multiply", "Polynomial", "Power",
    "Rational", "Symbol", "UnsupportedPolynomialExpression",
    "polynomial_from_expr",
]
