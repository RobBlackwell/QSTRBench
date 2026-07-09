#!/usr/bin/env python3

from functools import lru_cache
from itertools import chain, combinations
from pathlib import Path
import argparse
import numpy as np
import os
import pandas as pd
import re
import sys


def ensure_list(obj):
    return obj if isinstance(obj, list) else [obj]


def ensure_set(obj):
    if obj is None:
        return set()
    else:
        return set(ensure_list(obj))


def load_questions(filename):

    df = pd.read_json(filename, lines=True)

    if "ID" in df.columns:
        df = df.rename(columns={"ID": "id"})

    df["id"] = df["id"].astype(int)

    if "ANSWER" in df.columns:
        df = df.rename(columns={"ANSWER": "correctAnswer"})

    df["correctAnswer"] = df["correctAnswer"].apply(ensure_set)

    return df


def extract_relation(s: str) -> str:
    s = s.strip()

    s2 = s.rstrip(")];,")  # optional but helps with "E=F)"
    m = re.match(r"^\s*\S+\s*([<>]=?|!=|==|=)\s*\S+\s*$", s2)
    if m:
        op = m.group(1)
        return "=" if op == "==" else op

    # Case 2: infix form with spaces, e.g., "a < b", "x DC y", "a = b"
    tokens = s.split()
    if len(tokens) == 3:
        return tokens[1]

    # Case 3: single relation name like "AB"
    return s


def parse_answers(text):
    """
    An answer can be one or more comma or semicolon separated relations,
    so split these and return a list
    """

    # Remove anything inside parentheses (including the parentheses)
    text = re.sub(r"\([^)]*\)", "", text)

    raw_answers = [
        answer.strip() for answer in re.split(r"[;,]", text) if answer.strip()
    ]
    parsed = []
    for ans in raw_answers:
        # Annoyingly the LLMs sometimes put asterisks to mark a relation
        ans = re.sub(r"\*{2,}", "", ans)

        ans = extract_relation(ans)
        parsed.append(ans)

    return parsed


def clean_answer(text):
    """
    Extract the first non-blank line after the last 'answer:' marker.
    If not found, return the last non-empty line.
    Additionally, strip leading characters that are not
    letters, numbers, >, =, or <.
    """
    matches = list(re.finditer(r"answer:", text, re.IGNORECASE))

    if matches:
        last_match = matches[-1]
        after = text[last_match.end() :]

        # Split into lines and pick the first non-blank one
        lines = [line.strip() for line in after.splitlines()]
        result = next((line for line in lines if line), "")
    else:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        result = lines[-1] if lines else ""

    # Remove invald characters from the start or end
    result = re.sub(r"^[^a-zA-Z0-9<>=]+|[^a-zA-Z0-9<>=\)]+$", "", result)

    return result


def extract_tokens(response):
    usage = response.get("usage", {})

    if not usage:
        usage = response.get("usageMetadata", {})  # Google just have to be different!

    # OpenAI format with nested completion_token_details
    if "prompt_tokens" in usage and "completion_tokens" in usage:
        return {
            "input_tokens": usage["prompt_tokens"],
            "output_tokens": usage["completion_tokens"],
            "reasoning_tokens": usage.get("reasoning_tokens", None),
        }
    # Anthropic format
    elif "input_tokens" in usage and "output_tokens" in usage:
        return {
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "reasoning_tokens": usage.get(
                "reasoning_tokens", None
            ),  # Not sure about this?
        }
    # Gemini format
    elif "promptTokenCount" in usage and "candidatesTokenCount" in usage:
        return {
            "input_tokens": usage["promptTokenCount"],
            "output_tokens": usage["candidatesTokenCount"],
            "reasoning_tokens": usage.get("thoughtsTokenCount", None),
        }
    # Default
    else:
        return {"input_tokens": None, "output_tokens": None, "reasoning_tokens": None}


def load_answers(directory, model_name=None):
    """
    directory is a path to an experiment. If model_name is None,
    then load answers for all models tested.
    """
    if model_name:
        print(f"Loading answers for {model_name}..", file=sys.stderr)
        file_path = os.path.join(directory, model_name, "answers.jsonl")
        df = pd.read_json(file_path, lines=True)
        df["model"] = model_name
        df["id"] = df["id"].astype(int)

        return df
    else:
        model_names = [
            entry
            for entry in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, entry))
            and os.path.exists(os.path.join(directory, entry, "answers.jsonl"))
        ]
        df = pd.concat(
            [load_answers(directory, model_name) for model_name in model_names],
            ignore_index=True,
        )

    df["answer"] = df["answer"].fillna("")
    df["cleanAnswer"] = df["answer"].apply(clean_answer)

    df["delta_t"] = df["timestamp"].diff()

    # Apply the function to each row and convert results to a DataFrame
    tokens_df = df["response"].apply(extract_tokens).apply(pd.Series)

    # Concatenate only if there are useful columns
    if not tokens_df.empty:
        df = pd.concat([df, tokens_df], axis=1)

    return df


def jaccard_index(x, y):
    """
    Compute the Jaccard Index (intersection over union for two sets.
    """
    i = x.intersection(y)
    u = x.union(y)
    return len(i) / len(u)


def non_empty_subsets(B):
    return list(chain.from_iterable(combinations(B, r) for r in range(1, len(B) + 1)))


# Let $B$ be the set of all basis relations in a calculus.
# For a particular QSTR question, if it is a converse question then there is a correct answer $A$ such that $A \in B$. For CN and CT questions, $A \subseteq B$ and $A \neq \emptyset$.
# Let $G$ be the set of all possible guesses to the question. If the question is a converse question, then $G = B$. For CN and CT questions, $G = \{ X \subseteq B \mid X \neq \emptyset \}$
# The guess rate for that question is then $\frac{1}{|G|} \sum_{X \in G} J(A, X)$ where J is the Jaccard index.
# The guess rate for a specific QSTR calculus is the mean of the guess rates for all the questions we pose for that calculus.
# The guess rate for our QSTR benchmark is the mean of the guess rates for all the questions we pose for that benchmark.


@lru_cache(maxsize=None)
def guess_rate(b, a, converse=False):
    B = set(range(1, b + 1))
    if converse:  # Only one possible answer
        G = [{x} for x in B]
    else:  # multiple possible answers
        G = non_empty_subsets(B)

    A = set(range(1, a + 1))

    j = [jaccard_index(set(g), A) for g in list(G)]
    return sum(j) / len(G)


def compute_jaccard_guess_rate(row):
    b = int(row["basis"])
    answer = row["correctAnswer"]
    converse = row["TYPE"] == "converse"
    return guess_rate(b, len(answer), converse=converse)


def load_results(pathname):
    """
    Load questions and answers from all models, combining into a big
    table for easy analysis.
    """

    print("Loading questions ..", file=sys.stderr)
    df1 = load_questions(os.path.join(pathname, "questions.jsonl"))
    print("Loading answers ..", file=sys.stderr)
    df2 = load_answers(pathname)
    df2["cleanAnswer"] = df2["cleanAnswer"].apply(parse_answers)
    df3 = pd.merge(df1, df2, on="id", how="inner")

    # Strictly the correct answer
    df3["strict_score"] = df3.apply(
        lambda x: set(x["cleanAnswer"]) == set(x["correctAnswer"]), axis=1
    )

    # The Jaccard index is more lenient.
    df3["jaccard"] = df3.apply(
        lambda x: jaccard_index(set(x["cleanAnswer"]), x["correctAnswer"]), axis=1
    )

    # Number of basis relations
    df3.loc[df3["CALCULUS"] == "RCC-8", "basis"] = 8
    df3.loc[df3["CALCULUS"] == "RCC-5", "basis"] = 5
    df3.loc[df3["CALCULUS"] == "RCC-22", "basis"] = 22
    df3.loc[df3["CALCULUS"] == "INDU", "basis"] = 25
    df3.loc[df3["CALCULUS"] == "STAR", "basis"] = 9
    df3.loc[df3["CALCULUS"] == "CDC", "basis"] = 9
    df3.loc[df3["CALCULUS"] == "9IM", "basis"] = 8
    df3.loc[df3["CALCULUS"] == "IA", "basis"] = 13
    df3.loc[df3["CALCULUS"] == "PA", "basis"] = 3

    df3["basis"] = df3["basis"].astype(int)

    print("Computing strict guess rate ..", file=sys.stderr)

    df3["guess_rate"] = np.where(
        df3["TYPE"] == "converse", 1 / df3["basis"], 1 / (2 ** df3["basis"] - 1)
    )

    df3["normalized_strict_score"] = (df3["strict_score"] - df3["guess_rate"]) / (
        1 - df3["guess_rate"]
    )

    print("Computing Jaccard guess rate (this may take some time) ..", file=sys.stderr)

    df3["jaccard_guess_rate"] = df3.apply(compute_jaccard_guess_rate, axis=1)

    df3["normalized_jaccard"] = (df3["jaccard"] - df3["jaccard_guess_rate"]) / (
        1 - df3["jaccard_guess_rate"]
    )

    return df3


def main():
    parser = argparse.ArgumentParser(description="Process results.")
    parser.add_argument("path", type=Path, help="Path to results")

    args = parser.parse_args()

    path = args.path

    df = load_results(path)
    df.to_pickle("results.pkl")


def test(str, result):
    x = parse_answers(clean_answer(str))
    if x == result:
        print(f"PASS {str} : {x} : {result}")
    else:
        print(f"FAIL {str} : {x} : {result}")
        sys.exit(1)


if __name__ == "__main__":

    test("A < B", ["<"])
    test("TPPi(x, y), x NTPP y", ["TPPi", "NTPP"])
    test("A >B, C<D,E=F)", [">", "<", "="])
    test(("###>(x,z)"), [">"])
    test(">(x,z)", [">"])
    test(
        "PP(x,y) and PP(y,z) means that x and y are not coincident, and y is a part of x.\n\n### Answer: PP, PP, EQ",
        ["PP", "PP", "EQ"],
    )
    test(
        "\n\n### Answer: ID(y,x)\n\nDisclaimer: This information is provided as general guidance and should not be taken as professional advice",
        ["ID"],
    )
    test(
        '\n\n### Answer: ID(y,x),PPi(x,y)".',
        ["ID", "PPi"],
    )

    main()
