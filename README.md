# QSTRBench

## Overview

This git repository contains benchmark questions, answers and
experimental results from our forthcoming paper:

A. G. Cohn and R. E. Blackwell, 2026.
QSTRBench : a New Benchmark to Evaluate the Ability of Language Models to Reason with Qualitative Spatial and Temporal Calculi

The dataset is an extensive qualitative spatial and temporal reasoning
(QSTR) benchmark for evaluating large language models (LLMs). We pose
questions concerning compositional reasoning (using composition
tables, CT), converse relations, and conceptual neighbourhoods (CN)
for QSTR calculi including Point Algebra (PA), Allen's Interval
Algebra, Interval and Duration (INDU), Region Connection Calculus
(RCC-5, RCC-8, and RCC-22), the nine intersection model, cardinal
direction calculus and STAR. An extended benchmark systematically
varies question presentation including prefix/infix,
words/symbols/nonce terms and schematic descriptions for selected
calculi.

[QSTRBench](data/raw/QSTRBench/) consists of 1806 questions, answers
and results for 32 contemporary frontier models.

[QSTRBenchExtended](data/raw/QSTRBenchExtended/) consists of 14372
questions, answers and results for o1 running on Microsoft Azure.

The RCC-22 conceptual neighbourhood, published in the paper for the first time,
is computed using a Prolog program, [rcc22.pl](prolog/rcc22.pl).

All LLM experiments were conducted using
[Golem](https://github.com/RobBlackwell/golem). [JSONT](https://github.com/RobBlackwell/jsont)
was used to template the prompts.

Some files in this repository are compressed with xz and must be
uncompressed with `xz -dk filename.xz`.

## Citation

If you use this dataset, please cite both the paper and the dataset:

TBD.

## Licensing

This dataset is copyright (c) 2026 The University of Leeds and licensed under the terms of the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

SparQ is copyright Diedrich Wolter and co-authors and licensed
under the terms of the GNU General Public License Version 3. See
[COPYING](data/external/sparq/COPYING) for more information.

GQR is copyright Matthias Westphal and co-authors and licensed
under the terms of the GNU General Public License v2.0. See
[LICENSE.txt](data/external/gqr/LICENSE.txt) for more information.

Hunspell is copyright Németh László and licensed under the terms
of the Mozilla Public License Version 1.1. See
[license.hunspell](data/external/hunspell/license.hunspell) for more
information.

The text of Jane Austen's Pride and Prejudice is licensed under the
terms of the [Project Gutenberg
License](https://www.gutenberg.org/policy/license.html) available
online at www.gutenberg.org. Credits: Chuck Greif and the Online
Distributed Proofreading Team at http://www.pgdp.net

## Contact

For more information, please contact: [r.e.blackwell@leeds.ac.uk](mailto:r.e.blackwell@leeds.ac.uk).

## Last Updated

May 2026
