# Tathabbut evaluation report

Cases: 13 (`cases.jsonl`) · expected citations: 12 · deep model: False
Run: 2026-10-03 22:16 UTC · live site https://3rb-tathabbut.hf.space (commit not reported)

| Metric | Value |
|---|---|
| Extraction recall | 12/12 (100%) |
| Tracing accuracy | 12/12 (100%) |
| Correct abstention | 2/2 (100%) |
| Wrongly referred | 0 |
| Extra citations (not expected) | 0 |

| Case | Expected | Got | OK |
|---|---|---|---|
| q-exact-1 | verified | verified | ✓ |
| q-misquote-1 | differs | differs | ✓ |
| q-wrongref-1 | verified | verified | ✓ |
| q-unmarked-1 | verified | verified | ✓ |
| q-span-1 | verified | verified | ✓ |
| q-notquran-1 | not_in_mushaf | not_in_mushaf | ✓ |
| q-en-1 | verified | verified | ✓ |
| q-en-wrongref | verified | verified | ✓ |
| h-sahih-1 | graded | graded | ✓ |
| h-sahih-2 | graded | graded | ✓ |
| h-fabricated-1 | graded | graded | ✓ |
| h-invented-1 | not_found | not_found | ✓ |
