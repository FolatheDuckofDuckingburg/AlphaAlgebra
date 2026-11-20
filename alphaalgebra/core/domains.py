"""Mathematical domains supported by the initial algebra model."""

from enum import Enum


class Domain(str, Enum):
    """A declared number domain; no implicit domain inference is performed."""

    NATURAL = "natural"
    INTEGER = "integer"
    RATIONAL = "rational"
    REAL = "real"
    COMPLEX = "complex"
