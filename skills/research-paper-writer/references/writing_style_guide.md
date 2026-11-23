# Academic Writing Style Guide (Survey & Experimental Papers)

## 1. Scholarly Voice, Tense & Precision

- **Voice**: Formal, objective, and concise. Prefer clear active constructions when stating contributions (*"We introduce..."*, *"Our experiments evaluate..."*) and objective third-person phrasing for established findings (*"Prior work [4] demonstrates..."*).
- **Verb Tense**:
  - *Present tense*: Established facts, mathematical definitions, and references to your own figures/tables (*"Table 2 summarizes..."*).
  - *Past tense*: Specific prior studies and completed experimental procedures (*"Smith et al. [3] trained..."*, *"We evaluated five baselines..."*).
- **Technical Precision**:
  - Define every acronym on first occurrence (*"Retrieval-Augmented Generation (RAG)"*) and use it consistently thereafter.
  - Replace vague qualifiers (*"very fast"*, *"many papers"*, *"significantly better"*) with exact figures (*"2.4× lower p99 latency"*, *"+4.1 F1 over Baseline A"*).

## 2. Argumentation & Section Flow

- **Claim -> Evidence -> Contrast**: Every technical paragraph should open with a topic sentence making one falsifiable claim, present data/proof/citations supporting it, and contrast it against alternatives.
- **Inverted Pyramid Introduction**: Move cleanly from domain stakes -> concrete bottleneck -> why existing approaches fall short -> core insight -> verifiable contribution bullets -> paper roadmap.
- **Thematic Related Work**: Organize literature into 2–4 conceptual axes (e.g., *architecture*, *training objective*, *evaluation regime*). Close each theme with an explicit positioning sentence: *"Unlike [3, 7], which assume stationary distributions, our formulation..."*

## 3. Paper Archetype Checklists

### Experimental / Method Paper
- Explicit problem formulation & notation table.
- Reproducible setup: datasets, splits, metrics (`↑`/`↓`), baselines, hyperparameters, compute cost.
- Main results table + component ablations + sensitivity/efficiency analysis + error analysis & limitations.

### Survey Paper
- Explicit **survey methodology** (databases searched, date window, inclusion/exclusion criteria).
- **Conceptual taxonomy** (visual tree or structured comparison matrix classifying every surveyed paper across unified dimensions).
- Synthesis of open challenges, benchmark flaws, and concrete future research directions—not an annotated bibliography.
