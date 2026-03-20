#!/usr/bin/env python3
"""Build compact WordNet 5WN noun index from Prolog files for browser runtime."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ATOMIC = ROOT / "atomic-kernel"
WN_ROOT = ROOT / "WNprolog-3.0" / "prolog"
NARR_ROOT = ROOT / "narrative-series" / "When Wisdom, Law, and the Tribe Sat Down Together"
OUT = ATOMIC / "nlp" / "wordnet_5wn_index.json"

RE_S = re.compile(r"^s\((\d+),(\d+),'((?:''|[^'])*)',([nvars]),(\d+),(\d+)\)\.$")
RE_HYP = re.compile(r"^hyp\((\d+),(\d+)\)\.$")


def unquote_word(raw: str) -> str:
    return raw.replace("''", "'").replace("_", " ").strip().lower()


def tokenize_text(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text)]


def load_candidate_lemmas() -> set[str]:
    terms: set[str] = set()
    for p in NARR_ROOT.rglob("*.md"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        terms.update(tokenize_text(txt))
    return terms


def parse_wordnet():
    synset_words: dict[str, set[str]] = defaultdict(set)
    lemma_senses: dict[str, list[tuple[str, int]]] = defaultdict(list)
    hypernyms: dict[str, list[str]] = defaultdict(list)

    wn_s = WN_ROOT / "wn_s.pl"
    wn_hyp = WN_ROOT / "wn_hyp.pl"

    with wn_s.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = RE_S.match(line.strip())
            if not m:
                continue
            synset_id, _w_num, word, ss_type, _sense_no, tag_count = m.groups()
            if ss_type != "n":
                continue
            lemma = unquote_word(word)
            if not lemma:
                continue
            synset_words[synset_id].add(lemma)
            lemma_senses[lemma].append((synset_id, int(tag_count)))

    with wn_hyp.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = RE_HYP.match(line.strip())
            if not m:
                continue
            child, parent = m.groups()
            if child.startswith("1") and parent.startswith("1"):
                hypernyms[child].append(parent)

    return synset_words, lemma_senses, hypernyms


def classify_builder(synset_words: dict[str, set[str]], hypernyms: dict[str, list[str]]):
    anchors = {
        "person": {
            "person", "human", "individual", "someone", "somebody", "mortal", "soul", "witness", "judge", "prophet"
        },
        "place": {
            "place", "location", "area", "region", "site", "city", "town", "country", "building", "room", "land", "world", "gate"
        },
        "thing": {
            "thing", "object", "artifact", "device", "instrument", "material", "entity", "whole", "item", "substance"
        },
    }

    anchor_synsets: dict[str, set[str]] = {k: set() for k in anchors}
    for sid, words in synset_words.items():
        for kind, terms in anchors.items():
            if words & terms:
                anchor_synsets[kind].add(sid)

    memo: dict[str, str] = {}

    def classify_synset(sid: str) -> str:
        if sid in memo:
            return memo[sid]

        votes = Counter()
        for kind in ("person", "place", "thing"):
            if sid in anchor_synsets[kind]:
                votes[kind] += 3

        for parent in hypernyms.get(sid, []):
            k = classify_synset(parent)
            if k != "unknown":
                votes[k] += 1

        if votes:
            kind = votes.most_common(1)[0][0]
        else:
            words = synset_words.get(sid, set())
            if any(w.endswith("er") or w.endswith("or") for w in words):
                kind = "person"
            elif any(w in {"city", "gate", "river", "garden", "desert", "mountain", "temple", "world"} for w in words):
                kind = "place"
            else:
                kind = "thing"

        memo[sid] = kind
        return kind

    return classify_synset


def build_index() -> dict:
    candidates = load_candidate_lemmas()
    synset_words, lemma_senses, hypernyms = parse_wordnet()
    classify_synset = classify_builder(synset_words, hypernyms)

    lemmas = {}
    for lemma, senses in lemma_senses.items():
        if lemma not in candidates and lemma.replace(" ", "") not in candidates:
            continue

        best_sid, _ = max(senses, key=lambda x: x[1])
        kind = classify_synset(best_sid)
        words = sorted(synset_words.get(best_sid, []))[:12]

        lemmas[lemma] = {
            "kind": kind,
            "synset": best_sid,
            "synset_words": words,
        }

    return {
        "version": 1,
        "source": "WordNet-3.0 5WN Prolog",
        "files": ["wn_s.pl", "wn_hyp.pl"],
        "lemma_count": len(lemmas),
        "lemmas": lemmas,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    built = build_index()

    if args.verify:
        if not OUT.exists():
            print(f"FAIL: missing {OUT}")
            return 1
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        if existing != built:
            print("FAIL: wordnet index mismatch; run --write")
            return 1
        print("OK: wordnet index deterministic")
        return 0

    if args.write or not args.verify:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(built, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        print(f"WROTE: {OUT}")
        print(f"lemmas: {built['lemma_count']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
