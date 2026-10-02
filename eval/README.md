# Evaluation set

`cases.jsonl`: one case per line, all synthetic (written by the team, no user data).

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
