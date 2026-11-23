# AlphaAlgebra

**An experimental symbolic reasoning system for algebraic problems.**

AlphaAlgebra explores how explicit mathematical representations, symbolic transformations, and independently checkable proof steps can support algebra problem solving. The initial target is olympiad-style algebra, developed incrementally from a small, testable formal core.

> **Project status:** early foundations. The repository currently contains the inherited AlphaGeometry codebase and an initial AlphaAlgebra specification. The AlphaAlgebra package includes typed expression and relation models, assumptions, exact sparse polynomial normalization, one narrowly scoped polynomial-equation normalization rule, and immutable proof-state/transition records. The existing recomputation checker covers that normalization rule only; the new transition records are descriptive data structures, not a general proof verifier. The project does not yet contain an algebra solver, proof search, trained model, or reported solving results.

## Relationship to AlphaGeometry

This repository preserves code and project history derived from [Google DeepMind's AlphaGeometry](https://github.com/google-deepmind/alphageometry), released with [“Solving Olympiad Geometry without Human Demonstrations”](https://www.nature.com/articles/s41586-023-06747-5).

AlphaAlgebra is an independent experimental extension developed in the AlphaGeometry research lineage. It investigates whether a similarly inspectable symbolic-search approach can be developed for algebra. The inherited geometry implementation is not an algebra engine, and its geometry-specific rules, datasets, checkpoints, and reported results must not be interpreted as evidence of algebra capability.

This repository is not an official Google or Google DeepMind product, and no affiliation, review, endorsement, or acceptance by Google DeepMind is implied. The long-term aspiration is to produce a technically sound contribution that could be proposed for upstream consideration.

## Research direction

The initial research question is:

> Can learned guidance improve the efficiency of symbolic algebra proof search while preserving independently verified correctness?

The first priority is a reliable symbolic foundation. Neural guidance is optional and will only be considered after a symbolic baseline exists and an efficiency bottleneck has been measured.

### Design principles

- **Correctness before cleverness:** a proposed transformation is not accepted merely because a model suggested it.
- **Explicit conditions:** transformations must record preconditions and side conditions, including denominator and sign constraints.
- **Inspectable derivations:** proof steps should be represented as structured data, not opaque natural-language claims.
- **Independent verification:** proof checking must be separated from candidate generation and search.
- **Reproducibility:** datasets, evaluation splits, software versions, seeds, and failure cases must be documented.
- **Scope discipline:** geometry-specific code is preserved unless a concrete, reviewed reuse case is established.

## Current scope

The formal core supports exact rational constants, symbolic variables, arithmetic expression trees, explicit mathematical domains and assumptions, equations and order relations, and immutable proof-state/transition records. An initial exact sparse polynomial representation can expand and collect expressions built from these nodes using non-negative integer powers.

The proof-state records distinguish equivalence from forward and reverse implication at the metadata level. They do not yet establish those relationships, interpret side-condition strings, or verify arbitrary transitions.

Out of scope for the initial foundation are a general-purpose computer algebra system, unrestricted theorem proving, and unchecked neural generation of proofs.

## Repository layout

```text
alphaalgebra/
  __init__.py
  core/
    __init__.py
    assumptions.py
    ast.py
    domains.py
    polynomial.py
    proof_state.py
    relations.py
    transformations.py
  tests/
    test_assumptions.py
    test_ast.py
    test_relations.py
    test_polynomial.py
    test_proof_state.py
    test_transformations.py
docs/
  ALPHAALGEBRA_SPEC.md
  UPSTREAM_ALPHA_GEOMETRY_README.md
.github/
  workflows/
    alphaalgebra-tests.yml
```

The original geometry implementation remains in the repository root for provenance and reference. The AlphaAlgebra package is kept separate from those geometry modules.

## Development

The initial core uses only the Python standard library. Requirements: Python 3.10 or newer.

Run the foundation tests from the repository root:

```bash
python -m unittest discover -s alphaalgebra/tests -v
```

The tests exercise data-model invariants, exact polynomial normalization, and the initial polynomial-equation rule plus its narrowly scoped proof-state transition checker. Passing them does not establish general theorem-proving capability.

## Roadmap

1. **Formal core:** typed expressions, domains, assumptions, and relations.
2. **Transformation kernel:** explicit rewrite rules with preconditions and side conditions.
3. **Proof representation and verifier:** independently check each transformation and preserve constraints.
4. **Symbolic baseline:** bounded, deterministic search with measurable resource limits.
5. **Dataset and evaluation:** trace provenance, prevent template leakage, and report failures as well as successes.
6. **Learned guidance experiment:** compare against the symbolic baseline without making the learned model the correctness authority.

See [the technical specification](docs/ALPHAALGEBRA_SPEC.md) for the research question, scope, architecture, and evaluation plan.

## Provenance and licensing

The inherited AlphaGeometry files retain their original notices and licensing terms. AlphaGeometry software is distributed under Apache-2.0; other upstream materials may have separate terms, including CC BY 4.0. See the repository's LICENSE and the archived upstream README in the repository history.

New AlphaAlgebra code in this contribution is provided under Apache-2.0, consistent with the repository's software licensing. Preserve upstream copyright and attribution notices when modifying or redistributing inherited files.

## Acknowledgement

AlphaGeometry was developed by Google DeepMind and collaborators. This project acknowledges that work as its technical and research starting point; it does not represent the original authors or organization.
