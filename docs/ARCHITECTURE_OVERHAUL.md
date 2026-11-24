# AlphaAlgebra Architecture Overhaul

**Status:** Architecture decision record / implementation plan  
**Target:** Olympiad algebra  
**Architecture:** Hybrid neuro-symbolic search with an independently trusted symbolic verifier  
**Branch:** `architecture/olympiad-hybrid`

## 1. Decision

AlphaAlgebra will be developed as an Olympiad-algebra reasoning system by transforming the existing AlphaGeometry-derived repository. It will retain the useful research lineage and reusable infrastructure, but it will not treat the geometry solver as an algebra engine.

The system will use four separated responsibilities:

1. **Symbolic candidate generation** enumerates transformations that are applicable to the current algebraic state.
2. **Neural guidance** ranks legal candidate actions or estimates their usefulness. It does not invent mathematical validity.
3. **Independent verification** checks each proposed transition, including preconditions, side conditions, and its logical relationship to the prior state.
4. **Bounded search** explores candidate derivations under explicit depth, node, and time budgets.

A neural policy may be absent in early milestones. The architecture will expose a policy interface from the beginning so that symbolic-only and neural-guided search can be compared under the same verifier and resource limits.

## 2. Research question

> Can learned guidance improve the efficiency of Olympiad algebra proof search while preserving independently verifiable mathematical correctness?

This is a hypothesis to test. It is not a claim about current AlphaAlgebra performance.

## 3. Initial mathematical scope

### Core problem families

- Polynomial identities and simplification
- Polynomial equations, including linear and quadratic equations
- Factorization and expansion
- Systems of polynomial equations; substitution and elimination
- Rational expressions and equations, with explicit denominator restrictions
- Inequalities, with sign-sensitive transformations

### Later extensions

- Functional equations
- Sequences and recurrences
- Algebraic number-theory problems

Advanced abstract algebra, unrestricted theorem proving, and geometry-specific construction problems are outside the initial target.

## 4. Proposed architecture

```text
Problem statement
      |
      v
Parser + problem/goal representation
      |
      v
Typed algebraic state (AST, domains, assumptions, relations)
      |
      v
Legal candidate transformation generator
      |                         \
      |                          v
      |                    Neural action ranker
      |                          |
      +-----------<--------------+
      |
      v
Independent rule verifier
      |
      v
Verified transition / proof certificate
      |
      v
Bounded symbolic or neural-guided search
      |
      v
Verified derivation + explanation renderer
```

The neural ranker receives structured state and candidate-action features and returns scores or an ordering. It cannot add an action to the legal candidate set, edit a proof certificate, or override a verifier rejection.

The verifier is a separate module with rule-specific checking logic. Candidate generation and neural scoring are untrusted proposal mechanisms.

## 5. Target package boundaries

The following is the intended destination structure. It is a target architecture, not a claim that all modules already exist.

```text
alphaalgebra/
  core/
    ast.py
    domains.py
    assumptions.py
    relations.py
    polynomial.py
    proof_state.py
  problem/
    statement.py
    goals.py
    parser.py
    renderer.py
  rules/
    base.py
    registry.py
    polynomial/
    equations/
    inequalities/
    rational/
  verification/
    certificate.py
    verifier.py
    rule_checkers/
  search/
    candidates.py
    state_graph.py
    policies.py
    symbolic.py
    beam.py
  guidance/
    features.py
    action_codec.py
    scorer.py
  data/
    schemas.py
    synthetic/
    provenance.py
  evaluation/
    benchmarks.py
    metrics.py
    splits.py
  tests/
    ...
docs/
  ALPHAALGEBRA_SPEC.md
  ARCHITECTURE_OVERHAUL.md
```

Package boundaries should be introduced incrementally. Avoid a large directory reshuffle before the underlying interfaces are tested.

## 6. Transformation contract

Every transformation rule must declare:

- A stable rule identifier and version
- An applicability matcher
- A deterministic state transformer
- Explicit preconditions
- Explicit side conditions
- Its logical semantics: equivalence, forward implication, or reverse implication
- A separate verifier that recomputes or checks the claimed result
- Unit tests for valid, invalid, and boundary cases

The system must distinguish syntactic equality from mathematical equivalence and solution-set preservation.

Examples of conditions that must never be silently discarded:

- Denominators must be nonzero before division or cancellation.
- Multiplying or dividing an inequality requires the sign of the factor to be known.
- Squaring both sides may introduce extraneous solutions and is not generally an equivalence.
- A one-way implication must not be labelled as equivalence.

The current `polynomial_equation_to_zero` rule remains a narrow normalization rule, not a solver.

## 7. Search and learned guidance

The first search baseline should be deterministic and symbolic-only. Candidate actions are generated from the current state and checked before entering the search frontier.

The search interface should support:

- Maximum depth, expanded-node count, and wall-clock budget
- Canonical state keys and duplicate-state detection
- A documented cost function
- Deterministic tie-breaking and reproducible seeds where applicable
- Complete traces for successful searches
- Explicit timeout, budget-exhaustion, and saturation statuses

A policy interface should support at least:

- `SymbolicPolicy`: deterministic hand-designed ranking
- `NeuralPolicy`: learned ranking over the same legal candidate actions

The key comparison is symbolic-only versus neural-guided search with the same candidate generator, verifier, and resource budget. Neural-only proof acceptance is not part of the design.

## 8. Synthetic data and evaluation

Synthetic examples may be generated by applying known rules to sampled expressions and states. Every generated transition must pass the verifier before it can enter a training corpus.

Each record should retain:

- Stable example ID
- Generator and rule versions
- Initial state and goal
- Full structured action trace
- Verification outcome and verifier version
- Random seed and generation configuration
- Source/license metadata where external material is involved

Train/validation/test splits must be made at problem-template or generator-family level to reduce near-duplicate leakage. Official Olympiad problems should be held out for evaluation where feasible; source and redistribution rights must be checked before storing statement or solution text.

Report solve rate by topic, proof validity, verifier rejection rate, nodes expanded, runtime, memory, budget sensitivity, and failure categories. Report denominators and evaluation conditions. Do not describe an unrun benchmark as a result.

## 9. Inherited AlphaGeometry code audit

This table records an initial source-level review. “Adapt” means investigate and extract a reusable interface; it does not mean the current file is algebra-ready.

| Inherited component | Initial disposition | Reason |
|---|---|---|
| `geometry.py` | Replace in active solver | Defines geometric objects and operations |
| `graph.py` | Replace in active solver | Proof graph is built around geometric node types and geometry tables |
| `problem.py` | Replace in active solver | Problem clauses and construction parsing import the geometry model |
| `dd.py` | Replace in active solver | Deduction matchers operate on geometry objects and predicates |
| `ddar.py` | Replace in active solver | Orchestrates geometry DD and AR |
| `ar.py` | Do not reuse as the algebra engine | Despite its name (“Algebraic Reasoning”), it performs geometry-specific angle, distance, and ratio reasoning; it also uses floating-point representations |
| `alphageometry.py` | Replace entry point | CLI and problem flow are geometry-specific |
| `beam_search.py` | Adapt selectively | Generic-looking JAX/Flax token-decoding beam utilities, but coupled to autoregressive language-model decoding rather than structured algebra actions |
| `models.py`, `lm_inference.py`, `decoder_stack.py`, `transformer_layer.py` | Adapt selectively, later | Potential neural-model infrastructure; current configuration and data path are geometry-oriented and carry substantial dependencies |
| `graph_utils.py`, `numericals.py`, `pretty.py`, `trace_back.py` | Audit individually | Their utility cannot be assumed independent of geometry-specific data structures |
| `defs.txt`, `rules.txt`, geometry datasets and geometry model configuration/checkpoints | Exclude from algebra pipeline | They encode geometry constructions, predicates, or training targets |
| Upstream tests | Preserve as provenance/reference | They validate the inherited geometry implementation, not AlphaAlgebra capability |

No inherited geometry file should be deleted as part of the initial architecture step. Keep upstream attribution and notices intact. Any later retirement or extraction should be a reviewed, traceable change.

## 10. Existing AlphaAlgebra foundation

The current `alphaalgebra/core` package already provides:

- Immutable expression nodes for rationals, symbols, sums, products, and powers
- Explicit number-domain enum
- Symbol assumptions
- Typed equation and order relations
- Exact sparse multivariate polynomial normalization
- A narrow polynomial equation-to-zero transformation
- A checker that recomputes that named normalization and its corresponding state transition

Important limitations remain:

- No parser or problem interface
- Only an initial rule registry with one independently checked polynomial normalization rule; no broad rule library
- No general-purpose proof verifier
- Exact factorization is limited to univariate quadratics with rational roots; no general factorization, substitution, elimination, or inequality rule engine
- No general algebra solver; an initial bounded symbolic search kernel now exists
- No synthetic-data pipeline or learned model

The transition records for unimplemented rules are metadata only. The existing checker must not be generalized by simply trusting rule names or descriptive side-condition strings.

## 11. Milestones

### M0 — Architecture and provenance
- Record this architecture and preserve inherited geometry files.
- Keep algebra package imports independent of geometry modules.
- Identify source commit and retain upstream licensing.

### M1 — Formal algebra state
- Extend typed expressions and problem/goal records only as required by the first supported problem families.
- Define canonical state identity and explicit domains/assumptions.
- Add parser and renderer tests.

### M2 — Rule kernel and independent verifier
- Introduce a rule protocol and registry.
- [x] Implement and independently verify polynomial equation-to-zero normalization and exact rational-root quadratic factorization.\n- [ ] Expand the rule library to polynomial identities, substitution, elimination, rational equations, and inequalities with explicit side conditions.
- Add rational-domain and inequality precondition handling before enabling those rule families.

### M3 — Deterministic symbolic baseline
- [x] Implement deterministic candidate enumeration with independent verification before frontier insertion.
- [x] Implement bounded breadth-first search with structural duplicate-state detection, depth/node budgets, explicit terminal statuses, and complete traces for solved paths.
- [ ] Add broader rule families and a goal/problem interface suitable for multi-step Olympiad tasks.
- [ ] Measure baseline solve coverage and failure modes on generated problems.

The current implementation is an initial search kernel, not a capable Olympiad solver. Its default state key is structural (AST/proof-state representation), not mathematical equivalence modulo algebraic identities. It does not yet include a wall-clock budget, neural policy, or broad algebra rule library.

### M4 — Dataset and evaluation
- Build provenance-aware synthetic trace generation.
- Define topic-level and template-family splits.
- Establish held-out Olympiad evaluation protocol.

### M5 — Neural guidance
- Adapt or replace the inherited model stack behind the policy interface.
- Train a candidate-action ranker on verified traces.
- Compare against symbolic-only search under identical limits.

### M6 — Research evaluation
- Run ablations and report success, failure, correctness, efficiency, and generalization.
- Publish reproducible configurations and limitations.

## 12. Acceptance principles

- A neural suggestion is never proof.
- No transition is accepted without verifier approval.
- No equivalence claim is made where only implication is established.
- No geometry benchmark, dataset, or checkpoint is counted as algebra evidence.
- No performance claim is published without an actual reproducible run.
- Preserve upstream copyright and licensing notices on inherited code.
