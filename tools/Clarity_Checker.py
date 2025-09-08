#!/usr/bin/env python3
"""
Clarity_Checker.py
A simple command-line tool to measure how clear AI rollout communication is.

Metrics:
- Flesch Reading Ease (higher = easier to read)
- Flesch-Kincaid Grade Level (approx. school grade level)
- Basic diagnostics + practical suggestions

Usage:
  python Clarity_Checker.py --text "Paste your paragraph here."
  python Clarity_Checker.py --file path/to/textfile.txt
  python Clarity_Checker.py          # launches interactive prompt
"""

import argparse
import sys

try:
    import textstat
except ImportError:
    sys.stderr.write(
        "ERROR: Missing dependency 'textstat'.\n"
        "Install with:  pip install -r requirements.txt\n"
    )
    sys.exit(1)


SCORE_BANDS = [
    (70, "Very clear"),
    (50, "Fairly clear"),
    (-1, "Difficult to read"),
]


def label_from_score(score: float) -> str:
    for cutoff, label in SCORE_BANDS:
        if score >= cutoff:
            return label
    return "Difficult to read"


def suggestions(text: str, fre_score: float, fk_grade: float) -> list:
    """Return plain, actionable suggestions (no AI required)."""
    tips = []

    # Sentence & word length heuristics
    avg_sentence_len = textstat.avg_sentence_length(text)
    avg_syllables = textstat.avg_syllables_per_word(text)

    if fre_score < 70:
        tips.append("Use shorter sentences (aim for 12–18 words).")
    if fk_grade > 10:
        tips.append("Prefer simple words over jargon (choose common words).")
    if avg_sentence_len > 20:
        tips.append(f"Your average sentence length is {avg_sentence_len:.1f}. Split long sentences.")
    if avg_syllables > 1.7:
        tips.append("Swap complex words for simpler alternatives.")
    # Common corporate-jargon hints
    buzz = ["leverage", "optimize", "synergy", "utilize", "initiative",
            "transformative platform", "operationalize", "maximize"]
    if any(b in text.lower() for b in buzz):
        tips.append("Reduce corporate jargon—say exactly what the tool does in plain language.")
    # Concrete action hint
    tips.append("Add one concrete example (what changes first, who approves, when training starts).")

    # De-duplicate while preserving order
    seen = set()
    unique = []
    for t in tips:
        if t not in seen:
            unique.append(t)
            seen.add(t)
    return unique


def report(text: str) -> None:
    fre = textstat.flesch_reading_ease(text)            # higher is better
    fk  = textstat.flesch_kincaid_grade(text)           # lower is easier
    label = label_from_score(fre)

    print("\n--- Clarity Report ---")
    print(f"Flesch Reading Ease : {fre:.1f} → {label}")
    print(f"FK Grade Level      : {fk:.1f}")
    print(f"Sentence length (avg words): {textstat.avg_sentence_length(text):.1f}")
    print(f"Syllables per word (avg)   : {textstat.avg_syllables_per_word(text):.2f}")

    tips = suggestions(text, fre, fk)
    if tips:
        print("\nSuggestions:")
        for i, t in enumerate(tips, 1):
            print(f"  {i}. {t}")
    print("----------------------\n")


def main():
    parser = argparse.ArgumentParser(description="Measure clarity of AI rollout communication.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--text", type=str, help="Text to evaluate (wrap in quotes).")
    group.add_argument("--file", type=str, help="Path to a .txt or .md file to evaluate.")
    args = parser.parse_args()

    if args.text:
        text = args.text.strip()
        if not text:
            sys.exit("No text provided to --text.")
        report(text)
        return

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            sys.exit(f"Failed to read file: {e}")
        report(text)
        return

    # Interactive fallback
    print("Paste or type your text. Press ENTER twice to run the report.")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "":
            if lines:
                break
        lines.append(line)
    text = "\n".join(lines).strip()
    if not text:
        sys.exit("No text received.")
    report(text)


if __name__ == "__main__":
    main()
