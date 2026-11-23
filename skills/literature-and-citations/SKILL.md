---
name: literature-and-citations
description: >-
  Conduct grounded academic literature reviews, verify BibTeX citations against
  Semantic Scholar, audit `.tex` + `.bib` files for missing or hallucinated keys,
  and run citation/literature quality autoraters (`citation_f1.py`,
  `lit_review_quality.py`). Use this skill whenever searching prior work, checking
  references, building a Related Work section, or evaluating citation precision/recall.
---

# Grounded Literature Synthesis & Citation Auditing

PaperOrchestra prevents hallucinated citations via a two-phase pipeline (`methods/agents/literature_review_agent.py` + `utils/scholar_utils.py`):
1. **Discovery**: Gemini with Google Search grounding proposes candidate papers per outline section (`CandidatePaper`: title, year, reason).
2. **Verification**: `s2_title_search` queries Semantic Scholar (`https://api.semanticscholar.org/graph/v1/paper/search`), enforces `--research_cutoff`, and requires fuzzy title match ratio `> 70` (+10 bonus when publication year matches) before registering a BibTeX entry in `references.bib` and `citation_map.json`.

## 1. Audit Any `.tex` + `.bib` Manuscript Offline or Online

Run [audit_citations.py](./scripts/audit_citations.py) on any writeup folder (`latex_writeup/`, `content_refinement_workdir/`, or external LaTeX repo) to detect undefined `\cite*` keys, duplicate BibTeX entries, unused references, and optionally verify every BibTeX title live against Semantic Scholar:

```bash
# Offline structural check (fast, runs inside sandbox)
python3 skills/literature-and-citations/scripts/audit_citations.py \
  --tex paper_output_my_study/latex_writeup/raw_draft_paper.tex \
  --bib paper_output_my_study/latex_writeup/references.bib

# Live Semantic Scholar title verification (requires network access)
conda run -n paper_orchestra python skills/literature-and-citations/scripts/audit_citations.py \
  --tex paper_output_my_study/latex_writeup/raw_draft_paper.tex \
  --bib paper_output_my_study/latex_writeup/references.bib \
  --verify-s2
```

## 2. Standalone Literature Review for Research Scoping

You can run `HybridLiteratureAgent` standalone—even before running experiments—to map the competitive landscape and collect verified `.bib` references for a draft `outline.json`:

```python
from methods.agents.outline_agent import OutlineAgent
from methods.agents.literature_review_agent import HybridLiteratureAgent

OutlineAgent(model_name="gemini-3.1-pro-preview", cutoff_date="2026-11").run(
    idea_file="projects/my_study/raw_materials/idea_sparse.md",
    experimental_log_file="projects/my_study/raw_materials/experimental_log.md",
    latex_template_file="templates/iclr2025/template.tex",
    conference_guidelines_file="templates/iclr2025/guidelines.md",
    output_filepath="projects/my_study/outline.json",
)

HybridLiteratureAgent(
    idea_path="projects/my_study/raw_materials/idea_sparse.md",
    experimental_log_path="projects/my_study/raw_materials/experimental_log.md",
    latex_template_path="templates/iclr2025/template.tex",
    conference_guidelines_path="templates/iclr2025/guidelines.md",
    output_dir="projects/my_study/lit_review",
    model_name="gemini-3.1-pro-preview",
).run(outline_path="projects/my_study/outline.json", cutoff_date="2026-11")
```

## 3. Evaluating Literature Quality & Citation F1

- **Must-Have (P0) vs. Supplemental (P1) Citation Recall/Precision** against a reference paper: see `autoraters/citation_f1.py` (`ReferenceF1V1Evaluator`). P0 covers compared baselines, datasets used, core methods extended, and cited benchmark metrics.
- **Standalone & Side-by-Side Literature Review Quality**: see `autoraters/lit_review_quality.py` and `autoraters/sxs_lit_review_quality.py`.

## Best Practices

- Set `SEMANTIC_SCHOLAR_API_KEY` in `.env` before running large literature sweeps or `ReferenceF1V1Evaluator` to avoid HTTP 429 throttling.
- Ensure every baseline in `experimental_log.md` Table 1 has a corresponding P0 citation in `references.bib`.
