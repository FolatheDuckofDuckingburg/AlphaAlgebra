"""AlphaAlgebra: inspectable symbolic foundations for algebra reasoning."""

from .core import (
    Add, Assumptions, Domain, Equation, GreaterEqual, GreaterThan,
    LessEqual, LessThan, Multiply, Polynomial, PolynomialEquationNormalForm,
    Power, Rational, RULE_POLYNOMIAL_EQUATION_TO_ZERO, Symbol,
    UnsupportedPolynomialExpression, normalize_polynomial_equation,
    polynomial_difference, polynomial_from_expr,
    verify_polynomial_equation_normal_form,
)

__all__ = [
    "Add", "Assumptions", "Domain", "Equation", "GreaterEqual",
    "GreaterThan", "LessEqual", "Multiply", "Polynomial",
    "PolynomialEquationNormalForm", "Power", "Rational",
    "RULE_POLYNOMIAL_EQUATION_TO_ZERO", "Symbol",
    "UnsupportedPolynomialExpression", "normalize_polynomial_equation",
    "polynomial_difference", "polynomial_from_expr",
    "verify_polynomial_equation_normal_form",
]
