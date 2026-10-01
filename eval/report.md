# Tathabbut evaluation report

Cases: 13 · expected citations: 12 · deep model: False

| Metric | Value |
|---|---|
| Extraction recall | 12/12 (100%) |
| Tracing accuracy | 8/12 (67%) |
| Correct abstention | 1/2 (50%) |
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
| h-sahih-1 | graded | source_error | ✗ |
| h-sahih-2 | graded | source_error | ✗ |
| h-fabricated-1 | graded | source_error | ✗ |
| h-invented-1 | not_found | source_error | ✗ |
