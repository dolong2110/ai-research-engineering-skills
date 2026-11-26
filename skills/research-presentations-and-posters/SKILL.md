---
name: research-presentations-and-posters
description: >-
  Design and build conference oral/spotlight slide decks (Beamer, Marp, Google
  Slides), scannable conference posters (A0 / 48x36), Q&A backup slides, and
  interactive GitHub Pages academic project websites from completed papers. Use
  this skill when turning a manuscript into a talk, poster, or project webpage.
---

# Research Presentations, Posters & Academic Project Pages

A paper is read linearly; a **talk or poster is scanned in 5 seconds**. Never copy-paste paper paragraphs or dense 10-column tables onto slides or posters.

Read [talk_and_poster_blueprint.md](./resources/talk_and_poster_blueprint.md) before outlining slides or posters.

## 1. Conference Talks (5-Min Spotlight & 15-Min Oral)

- **Assertion-Evidence Slide Rule**: Every slide title is a **1-line takeaway claim** (*"Temporal memory cuts unseen mask drift by 5.0% J"*), NOT a generic topic label (*"Results"*).
- **Visual Density Cap**: $\le 35$ words per slide, minimum `18–20 pt` body font, highlight the **one key row/number** in tables (mute everything else in light gray), and show visual intuition *before* equations.
- **Timing Budget**: ~1 minute per content slide + dedicated **Backup Slides** after "Thank You" anticipating top reviewer Q&A (hyperparameter sensitivity, latency overhead, failure cases, extra ablations).
- **Tool Integration**: Use the installed **Google Slides** (`gslides`) plugin to push decks directly to Google Slides, or author clean **LaTeX Beamer** (`metropolis` theme, `aspectratio=169`) / **Marp Markdown** decks in the repo.

## 2. Conference Posters (A0 Portrait / 48×36" Landscape)

- **3-Second Hook**: Top banner holds concise Title + Authors + Institution + **QR code** (linking to arXiv PDF + GitHub code).
- **Visual-First Columns**: 3 balanced columns (*Problem & Key Insight* -> *Method Diagram* -> *Headline Results & Takeaway*), $\ge 40\%$ whitespace, figures occupying $>50\%$ of ink area, readable from 2 meters (`>= 24–28 pt` body text).

## 3. Academic Project Websites (GitHub Pages)

Build a single-page responsive static site (`index.html` + clean CSS, mobile-friendly) featuring:
1. Title, author links, venue badge, and pill buttons (`Paper`, `arXiv`, `Code`, `Demo`).
2. Above-the-fold teaser figure/animation + crisp 1-paragraph TL;DR.
3. Interactive qualitative/metric slider or clean highlight figures.
4. One-click copyable `@inproceedings` / `@article` BibTeX block.
