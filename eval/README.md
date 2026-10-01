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
