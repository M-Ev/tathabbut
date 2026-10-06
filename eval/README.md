# Evaluation set

| Set | Cases | Run | Report |
|---|---|---|---|
| Visitors' questions, live site | 25 (`personas.json`) | `python3 scripts/persona_check.py` | `personas_report.md` |
| Quran, generated from the Mushaf | 660 | `python3 eval/synth_quran.py --n 600 --seed 2026` | `synth_report.md` |
| General cases | 13 (`cases.jsonl`) | `python3 eval/run_eval.py [--via-space URL]` | `report.md` |
| Circulated hadith, checked on Dorar | 36 (`hadith_cases.jsonl`) | `eval/verify_hadith_cases.py` | `hadith_cases.md` |
| Sayings that share a hadith's words | 20 (`trap_cases.jsonl`) | `eval/run_trap_eval.py` | `trap_report.md` |
| Fatwa questions | 12 (`fatwa_cases.jsonl`) | `eval/run_fatwa_eval.py` | `fatwa_report.md` |
| Urdu and Indonesian verse quotes | 900 per language | `eval/translation_census.py` | `translation_report.md` |
| The two models on the live site | English hadith and timings, per model | live runs through `POST /api/check` (`eval/run_model_eval.py` measures each job alone) | `model_live_report.md` |
| Pillars page quotes | every quote and phrase | `pytest tests/test_pillars.py` | test output |

All sets are synthetic or public texts; no user data. Gradings come from live Dorar runs, never from memory.

## Visitors' questions (5 Oct)

`personas.json` holds 25 questions written the way real visitors of every age ask: a child in Saudi dialect, a teen without
punctuation, an older visitor without hamzas, a WhatsApp forward, a chatbot answer with a wrong surah, questions in English,
Urdu, Indonesian and Arabizi, a single word, an off-topic question. Each carries what it must get (a fatwa found, the hadith
searched without the dialect words, the fabrication shown, the wrong surah caught...). `scripts/persona_check.py` asks the
live site, paced under its limit, and writes `personas_report.md`. Every failure is fixed and becomes a unit test.


`cases.jsonl`: one case per line, all synthetic (drafted with Claude, no user data).

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

## Urdu and Indonesian verse quotes (plan item 36)

`python3 eval/translation_census.py` writes `translation_report.md`: 900 quotes per language taken from 300 seeded
ayat of the King Fahd Complex translation (as written, one word dropped, one word swapped), and 18 sentences per
language that are not ayat (`negatives/ur.txt`, `negatives/id.txt`, written by Claude for a speaker to review).
Same matcher as the app. The floor was chosen on these cases, so the numbers are optimistic until real quotes
are tried.
