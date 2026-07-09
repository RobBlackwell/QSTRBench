# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

QSTRBench is a research dataset and evaluation framework for benchmarking LLMs on Qualitative Spatial and Temporal Reasoning (QSTR). It contains 1806 benchmark questions across multiple calculi (Point Algebra, Allen's Interval Algebra, INDU, RCC-5/8/22, 9IM, CDC, STAR), plus experimental results for 32+ frontier models.

## Data Pipeline

The workflow has three stages:

1. **Generate prompts** — `data/raw/QSTRBench/Makefile` uses [JSONT](https://github.com/RobBlackwell/jsont) to template `questions.jsonl` with `template.jsont` into `prompts.jsonl`.
2. **Run LLM experiments** — each model directory (e.g. `data/raw/QSTRBench/deepseek-r1-0528/`) has a `Makefile` that invokes [Golem](https://github.com/RobBlackwell/golem) to query an LLM and write `answers.jsonl`.
3. **Score results** — `bin/process.py` merges questions and answers, computes strict scores and Jaccard similarity, normalizes against guess rates, and serializes to `results.pkl`.

## Key Commands

Process results for a benchmark directory (requires numpy, pandas):
```bash
python3 bin/process.py data/raw/QSTRBench
```

Decompress xz-compressed JSONL files before using them:
```bash
xz -dk filename.jsonl.xz
```

Regenerate prompts (requires jsont at `~/git/jsont/jsont.py`):
```bash
make -C data/raw/QSTRBench prompts.jsonl
```

Run built-in answer-parsing tests:
```bash
python3 bin/process.py  # runs test() calls at bottom of __main__ block
```

## File Formats

- **`questions.jsonl`** — one JSON object per line with fields: `ID`, `QUESTION`, `CALCULUS`, `TYPE` (`ct`/`converse`/`cn`), `ANSWER` (list of correct relations), `BASIS`, and metadata (`ANON`, `DESCRIPTION-TYPE`, `RELATION-TYPE`, `PREFIX`).
- **`prompts.jsonl`** — one JSON object per line with `id` and `messages` (OpenAI-style chat format).
- **`answers.jsonl`** — Golem output, one JSON object per line with `id`, `answer` (raw LLM text), `response` (full API response including usage), and `timestamp`.

## Scoring Logic (`bin/process.py`)

- `clean_answer()` extracts the LLM's final answer by finding the last `### Answer:` marker and taking the first non-blank line after it.
- `parse_answers()` splits on commas/semicolons and normalizes each token to a bare relation name.
- **Strict score**: exact set equality between parsed answer and correct answer.
- **Jaccard score**: intersection-over-union for partial credit.
- Both are normalized against a **guess rate** baseline: `(score - guess_rate) / (1 - guess_rate)`.
- Guess rate for `converse` questions is `1/basis`; for `ct`/`cn` it uses the mean Jaccard over all non-empty subsets of the basis set.

## External Data Sources

- `data/external/gqr/` — composition tables and converse files from [GQR](https://github.com/m-westphal/gqr) (GPL v2).
- `data/external/sparq/` — calculus definitions from [SparQ](https://github.com/dwolter/SparQ) (GPL v3).
- `data/external/hunspell/` — English word list generated via `unmunch`.
- `data/external/austen/` — Pride and Prejudice text from Project Gutenberg (used for nonce-term experiments).

## Prolog (RCC-22 Conceptual Neighbourhood)

`prolog/rcc22.pl` computes the RCC-22 conceptual neighbourhood graph using SWI-Prolog. The output is `prolog/rcc22cn.txt`. Run with:
```prolog
?- alledges(L), print_pairs_to_file(L, rcc22cn).
```
