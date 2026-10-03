# Evaluation set

`cases.jsonl`: one case per line, all synthetic (drafted with Claude, review by the team's Sharia reviewer pending, no user data).

```json
{"id": "...", "text": "text to check",
 "expected": [{"type": "quran|hadith", "status": "verified|differs|not_in_mushaf|graded|found_similar|not_found",
               "ref": "49:6", "reference_ok": true, "scholars_any": ["bukhari"], "fabricated": true}]}
```

The starting cases were drafted with AI help and **must be reviewed by the team's Sharia reviewer**;
her reviewed and extended set replaces them. Quran cases run offline; hadith cases need access to dorar.net.

Run: `python eval/run_eval.py` (writes `eval/report.md`). Add `--deep` to include the language model.

## Hadith set checked against Dorar

`hadith_cases.jsonl` (36 cases) holds hadith texts commonly circulated online, for the Sharia reviewer.
Each case carries the exact search wording the app sends to Dorar, a `verification_status`
(`verified`, `not_found`, or `pending_live_check`), the approved scholars' gradings copied verbatim with
their Dorar links, and `"review": "pending"`. No grading is written from memory: a case that has not been
read on Dorar keeps empty grading fields and `"status": null` in `expected`.
`hadith_cases.md` is the reviewer's table, in Arabic, generated from the JSONL.

1. `python3 eval/verify_hadith_cases.py`: from a machine that can reach dorar.net. Searches every case
   with the app's own Dorar client and records what Dorar returns. Fills an expected result only where it
   is still empty, and keeps what the reviewer wrote in `hadith_cases.md`.
   `--dry-run` works offline: it prints each case's queries and URLs and flags extraction mismatches.
2. `python3 eval/run_eval.py --cases eval/hadith_cases.jsonl --deep`: the four English cases need the
   model (`--deep`). Like every run, this rewrites `eval/report.md`.

## Fatwa matching (plan item 45)

`fatwa_cases.jsonl` (12 questions, drafted by Claude except the package's own p.6 case and one from the plan)
are personal fatwa questions. `python3 eval/run_fatwa_eval.py` sends each one, as the app does, to
binbaz.org.sa and binothaimeen.net and writes `fatwa_report.md`: the words searched and the fatwas shown.
The team's Sharia reviewer marks, per question, the fatwa URLs she judges fitting in `acceptable`; only then
does the report give a hit rate ("a fitting fatwa among those shown"). Until then it claims none.

## Sayings that share words with a hadith (plan item 14)

`trap_cases.jsonl` (20, drafted by Claude, reviewer to confirm): known narrations with a word changed or a clause
added. `python3 eval/run_trap_eval.py --via-space https://3rb-tathabbut.hf.space` records what the live site shows,
then applies the rules before and after the coverage guard offline; without `--via-space` it re-scores the
recorded results. Writes `trap_report.md`, including the cost on `hadith_cases.jsonl`.
