# نسخة البداية · Starting version

The participant guide (FAQ 02) allows building on an earlier project with a documented starting version,
and states that only the work done from 4 to 6 October 2026 is evaluated.

This file documents the starting version: everything in this repository as of the commit tagged
`starting-version` was built **before 4 October 2026** (1 October 2026), after the team qualified,
with the AI tools listed in SOURCES_AND_LICENSES.md.

## What the starting version contains

- Rule-based extraction of Quran and hadith citations in Arabic and English, including written references.
- Quran matching against the Mushaf text (exact, multi-ayah, misquote with word diff, wrong reference).
- Dorar hadith search filtered to the approved scholars, two display groups, narrator-statement rule, fabricated flag.
- Swappable model layer (ALLaM through llama.cpp, any OpenAI-compatible endpoint, or none).
- Arabic/English web interface and `/api/check`.
- Unit tests with mocked sources, and a first synthetic evaluation set (not yet reviewed by the Sharia reviewer).

## Not verified in the starting version

- Live Dorar results: the build environment had no network access to dorar.net, so the site parser was written
  against the documented markup and tested with structural fixtures only.
- ALLaM speed and output quality on free CPU hosting.

## Work planned for 4 to 6 October (evaluated)

The list of changes made during the build days is kept in [CHANGELOG.md](CHANGELOG.md), each with its commit,
so the committee can see exactly what was added during the evaluated period.
