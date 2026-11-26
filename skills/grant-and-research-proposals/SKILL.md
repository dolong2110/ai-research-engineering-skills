---
name: grant-and-research-proposals
description: >-
  Draft persuasive research proposals, PhD/postdoc/industry fellowship statements,
  grant narratives (NSF/NIH/compute grants), and multi-quarter research roadmaps
  with falsifiable specific aims, risk-mitigation plans, and compute/resource
  budgets. Use this skill when writing funding proposals, research pitches, or
  fellowship applications.
---

# Grant, Fellowship & Research Proposal Writing

Unlike a conference paper (which reports *completed* proofs and tables), a research proposal sells a **high-impact, feasible, de-risked plan** to reviewers scanning 20 proposals in an evening.

## 1. Core Persuasion Architecture (The Heilmeier + Specific Aims Frame)

Use [research_proposal_template.md](./resources/research_proposal_template.md) and anchor Page 1 (the make-or-break **Specific Aims / Executive Summary** page) around five crisp moves:
1. **Stakes & Urgency**: Concrete scientific or societal cost of the unsolved problem today.
2. **Knowledge / Capability Gap**: The exact technical bottleneck preventing progress (not "more compute").
3. **Central Hypothesis & Key Insight**: Why your approach is uniquely poised to break that bottleneck—backed by **preliminary pilot data** (even a small MVE curve doubles reviewer confidence!).
4. **2–3 Independent, Synergistic Specific Aims**:
   - **Critical Rule (No Domino Failure!)**: Never make Aim 2 completely impossible if Aim 1 underperforms! Design Aims that complement each other yet each yield standalone publishable value.
5. **Expected Impact & Deliverables**: Target open-source artifacts, benchmarks, datasets, and venues.

## 2. Feasibility, Risk Mitigation & Compute Budgets

Reviewers reject ambitious proposals mainly for *lack of feasibility*, not lack of vision. Always include:
- **Explicit Risk & Pivot Matrix**: Name the top 3 ways each Aim could fail (e.g., data scarcity, training instability, sim-to-real gap) alongside a concrete **Plan B mitigation** and measurable Go/No-Go milestone.
- **Transparent Compute & Timeline Table**: Itemize GPU-hours (`A100/H100` count × hours × seeds × ablations), storage, API/dataset costs, and quarterly milestones rather than hand-waving "we will use cluster GPUs."
- **Broader Impacts / Open Science**: Concrete commitments (open code under MIT/Apache-2.0, documented datasets, reproducibility benchmarks, mentorship/outreach).
