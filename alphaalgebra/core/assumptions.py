"""Explicit assumptions attached to a symbolic reasoning context."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Assumptions:
    """Facts about symbols that transformations may require.

    These facts are declarations supplied by a problem or derivation. This
    class does not infer additional facts or prove that declarations hold.
    """

    nonzero: frozenset[str] = field(default_factory=frozenset)
    positive: frozenset[str] = field(default_factory=frozenset)
    integer: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        for field_name in ("nonzero", "positive", "integer"):
            values = getattr(self, field_name)
            if not isinstance(values, frozenset):
                object.__setattr__(self, field_name, frozenset(values))
                values = getattr(self, field_name)
            if any(not isinstance(name, str) or not name.strip() for name in values):
                raise ValueError(f"{field_name} assumptions must contain non-empty symbol names")
        # Positivity entails nonzeroness in the real-number setting.
        if not self.positive.issubset(self.nonzero):
            object.__setattr__(self, "nonzero", self.nonzero | self.positive)

    def is_nonzero(self, symbol_name: str) -> bool:
        return symbol_name in self.nonzero

    def is_positive(self, symbol_name: str) -> bool:
        return symbol_name in self.positive

    def is_integer(self, symbol_name: str) -> bool:
        return symbol_name in self.integer
