# AlphaAlgebra: Technical Specification

**Status:** Initial implementation — typed core foundation  
**Project:** AlphaAlgebra  
**Repository origin:** `google-deepmind/alphageometry`  
**Implementation status:** A minimal immutable expression AST, explicit domain enum, symbol assumptions, relation types, an exact sparse polynomial normalizer, and one explicit polynomial-equation normalization rule are implemented. A narrow checker recomputes that rule's output; it is not a general proof verifier. No parser, proof search, algebra solver, trained model, or training pipeline is claimed to exist.

## 1. Purpose

AlphaAlgebra is an experimental system for solving and explaining algebra problems through explicit, inspectable mathematical reasoning.

The initial research target is Olympiad-style algebra, approached incrementally. The first implementation should establish a reliable symbolic foundation and an independent proof-step verifier. Learned guidance is a later, optional component whose value must be demonstrated experimentally.

The project is inspired by the search-and-learning structure of AlphaGeometry, but it is **not** a claim that AlphaGeometry's geometry-specific reasoning system transfers directly to general algebra.

## 2. Research question

The central question is:

> Can learned step-ranking improve the efficiency of symbolic algebra proof search while preserving independently verified mathematical correctness?

This is a hypothesis to test, not an assumed outcome.

Subquestions:

1. Which algebra problem families can a bounded symbolic engine solve reliably?
2. Does neural ranking reduce search effort compared with symbolic-only search?
3. Can an independent verifier reject invalid transformations, missing preconditions, and solution-set changes?
4. Does guidance trained on generated traces generalise to held-out problem families?

## 3. Initial scope

### Included in the first domain

- Polynomial expressions and identities
- Linear and quadratic equations
- Factorisation and expansion
- Substitution and elimination in small systems
- Rational expressions, with explicit denominator constraints
- Basic inequalities, with sign-sensitive transformations
- Elementary sequences and functional equations only after the core equation engine is stable

### Explicitly out of scope for the first milestone

- A general-purpose computer algebra system
- Unrestricted theorem proving
- Full coverage of IMO algebra
- Advanced abstract algebra (groups, rings, fields, ideals, modules)
- Geometry-specific constructions and deduction rules
- Neural generation of unchecked proof steps as an authority

The scope may expand only when the existing domain has tests, documented semantics, and measurable performance.

## 4. Design principles

1. **Correctness before cleverness.** A small verified engine is preferable to a broad unreliable solver.
2. **Symbolic-first baseline.** Implement and measure symbolic search before introducing a neural policy.
3. **Independent verification.** The component proposing a transformation must not be the sole authority deciding whether it is valid.
4. **Explicit conditions.** Track domains, assumptions, nonzero conditions, and inequality sign conditions.
5. **Structured representations.** Parse expressions into an abstract syntax tree (AST); do not use raw string rewriting as the reasoning substrate.
6. **Provenance.** Every rule, dataset item, and reported result should have a traceable source and verification status.
7. **Reproducibility.** Pin dependencies, record configurations and seeds, preserve test fixtures, and distinguish measured results from intended work.

## 5. Proposed architecture

### 5.1 Problem interface

A normalized problem record should contain:

- Stable problem identifier
- Original statement and source
- Parsed goals and assumptions
- Variable declarations and domains
- Normalization version
- Parsing status and any unresolved ambiguity

The original statement must be preserved separately from its normalized representation.

### 5.2 Algebra representation

Use a typed AST for expressions and relations. The initial node vocabulary should cover:

- Integer and rational constants
- Symbols with declared domains
- Addition, multiplication, powers
- Equality and inequality relations
- Fractions or division nodes with denominator conditions
- Finite conjunctions and disjunctions where needed

Each proof state should carry its assumptions and side conditions. The representation must distinguish syntactic equality from mathematical equivalence.

### 5.3 Symbolic transformation engine

Rules are explicit, named transformations with:

- Input pattern and output construction
- Preconditions
- Side conditions
- Semantic justification
- Rule version and tests

Initial rule families include normalization, expansion, factorization, substitution, equation balancing, and safe inequality transformations.

Rules must not silently divide by an expression that may be zero, cancel a potentially zero factor, or multiply an inequality by an expression of unknown sign.

### 5.4 Search

The first search implementation should be deterministic and symbolic-only. It should expose:

- Candidate rule applications
- Search depth and node budget
- Visited-state handling
- Termination conditions
- A complete or explicitly truncated search trace

Search heuristics may initially be hand-designed and must be documented. The baseline should be reproducible.

### 5.5 Independent verifier

The verifier checks each proposed transition against the rule's formal semantics and recorded preconditions.

It should detect, at minimum:

- Invalid algebraic identities
- Missing domain restrictions
- Division by zero or cancellation of an unconstrained zero factor
- Invalid inequality direction changes
- Extraneous solutions introduced by non-equivalent transformations
- Incorrect claims that two equations or systems have the same solution set

Where a transformation preserves only implication in one direction, the proof state and goal logic must record that distinction. The system must not label it as equivalence.

A computer algebra library such as SymPy may support parsing, simplification, and baseline checks. It must not be treated as an independent proof certificate merely because it returns a simplified expression. The verifier's guarantees and limitations must be documented.

### 5.6 Optional learned policy (later phase)

A neural model may rank legal candidate transformations or estimate search priorities.

It must not:

- Define mathematical validity
- Override failed verifier checks
- Convert an unverified natural-language explanation into a proof
- Be required for the initial symbolic baseline

The policy should consume structured problem/search-state features and return rankings or scores over candidate actions. The symbolic engine remains responsible for generating legal candidates; the verifier remains responsible for checking transitions.

### 5.7 Explanation renderer

Render verified traces into readable derivations. Every displayed step should map to a specific rule application and its conditions. If a step is heuristic, incomplete, or not independently verified, label it accordingly rather than presenting it as a proof.

## 6. Dataset and provenance

Create a dataset namespace named **IMO-Algebra** for problem indexing and evaluation, subject to source and redistribution review.

Each record should include:

- ID in the form `IMO-YYYY-Pn`
- Year and problem number
- Original statement and source URL/reference
- Algebra topic tags
- Normalized problem representation
- Solution source and attribution
- Proof trace, if available
- Verification status and verifier version
- License/redistribution status

Do not assume that an online solution is licensed for redistribution. Keep source text, normalized data, generated traces, and derived annotations distinguishable.

Official Olympiad problems should initially be treated primarily as evaluation material, not as a sufficient training corpus. Synthetic training traces may be generated by applying known valid rules to generated expressions, but every generated transition must pass the verifier.

Prevent leakage by splitting at the problem or template-family level. Near-duplicate generated examples must not cross train and test splits.

## 7. Evaluation plan

### Baselines

1. **Symbolic-only:** deterministic rule application and search.
2. **Neural-only (optional research comparison):** evaluated for proposal quality, never accepted as a correctness authority.
3. **Neural-guided symbolic search:** learned ranking over legal symbolic candidates, with the same verifier and resource budget.

### Metrics

- Problem solve rate by topic and difficulty
- Proof validity rate
- Per-step verifier acceptance/rejection
- Search nodes expanded
- Runtime and memory
- Search-budget sensitivity
- Constraint and solution-set preservation
- Generalisation to held-out problem families

Report denominators, timeout policy, hardware, software versions, random seeds, and confidence intervals where appropriate. Do not tune on the final held-out evaluation set.

## 8. Milestones and acceptance criteria

### M0 — Repository and provenance boundary

- Preserve upstream attribution and the existing Apache-2.0 license.
- Record the upstream commit from which the project begins.
- Keep geometry-specific files intact until their reuse or retirement is deliberately reviewed.
- Establish AlphaAlgebra documentation and a separate development branch.

**Acceptance:** origin and license are documented; no upstream files are silently removed or relabeled.

### M1 — Formal algebra core

- Define immutable AST nodes for exact rational constants, symbols, sums, products, and powers.
- Define explicit number-domain labels and symbol assumptions.
- Define typed equality and order relations.
- Add unit tests for construction invariants and invalid inputs.
- Parser/renderer round-trip tests remain a follow-up task; no parser is included in this foundation.

**Acceptance for this initial slice:** supported nodes enforce their basic type and construction invariants, and exact rational constants do not pass through floating-point representations.

### M2 — Symbolic rule kernel

- Implement a small set of explicit transformations.
- Give every rule preconditions and tests.
- Record proof-state transitions.

**Acceptance:** each supported rule has positive and negative tests, including boundary cases.

### M3 — Independent verification

- Verify rule applications and side conditions.
- Distinguish equivalence from one-way implication.
- Add adversarial invalid-step tests.

**Acceptance:** invalid transformations in the test suite are rejected for the intended reason.

### M4 — Symbolic search baseline

- Add deterministic search with budgets and trace output.
- Evaluate on generated, verified problems and a carefully curated development set.

**Acceptance:** baseline results are reproducible and include failures and timeouts.

### M5 — Dataset pipeline

- Define versioned records and provenance fields.
- Generate synthetic examples with verified traces.
- Add family-aware splits and leakage checks.

**Acceptance:** every generated proof transition is verified and every record has provenance metadata.

### M6 — Neural guidance experiment

- Train a policy to rank legal candidate steps.
- Compare against symbolic-only search under matched budgets.
- Preserve verifier authority.

**Acceptance:** report whether guidance improves measured search efficiency; a negative result is valid.

### M7 — Additional algebra domains

Expand only through separately specified and tested rule domains. Advanced abstract algebra is not part of the initial MVP.

## 9. Repository strategy

The existing repository is a geometry research codebase. Do not rename geometry modules in place or imply that their contents already implement algebra.

Initial strategy:

- Add AlphaAlgebra documentation in a dedicated `docs/` area.
- Build new algebra modules in a separate package namespace.
- Reuse generic neural/search infrastructure only after file-level review and tests.
- Treat geometry-specific graph, construction, rule, and dataset code as legacy/reference material until a reuse decision is documented.
- Keep the upstream LICENSE and notices intact; review attribution obligations before redistribution or substantial reuse.

A later repository separation may be considered after the provenance and dependency audit. Do not detach the fork network as part of this initial specification commit.

## 10. Risks and open decisions

- **Semantic soundness:** the exact formal semantics of each transformation must be specified.
- **Parser ambiguity:** natural-language Olympiad statements may require manual normalization and review.
- **Search explosion:** symbolic search may fail to scale; measure before adding a learned policy.
- **Dataset leakage:** generated templates can make evaluation deceptively easy.
- **Tool dependence:** CAS simplification is not equivalent to a proof certificate.
- **Scope creep:** advanced domains should not be mixed into the initial algebra kernel.
- **Licensing:** verify permissions for every external solution, dataset, and derived artifact.

Open decisions for implementation include the Python version and packaging layout, the initial AST serialization format, and whether a proof-assistant backend will be explored after the verifier prototype.

## 11. Current status

The initial M1 foundation now contains immutable nodes for rational constants, symbols, sums, products, and powers; explicit domain labels; symbol assumptions; and typed equations and inequalities. Unit tests cover basic construction invariants. These components are data structures only: they do not simplify expressions, apply algebraic transformations, establish equivalence, or prove the truth of assumptions.

The transformation kernel, parser/renderer, independent verifier, search engine, dataset, model, and training pipeline remain unimplemented and unevaluated. The next task is to specify and test the semantics of a small set of symbolic transformations. The geometry implementation remains untouched.
