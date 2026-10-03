# Changelog

## Build days (4 to 6 October 2026), evaluated

Starting point: `1bc66fb` (see STARTING_VERSION.md). Each entry names what was wrong before and what the tool does now.

### 4 October

- **Evidence status follows written rules (plan item 13, preflight B1).** Before: a hadith graded fabricated by al-Albani showed «حالة الدليل: موثّق المصدر» beside a red verdict, and the API returned `tier: documented`. After: the hadith tiers come from `data/display_rules.json` (team draft, awaiting the Sharia reviewer's signature, and the interface says so): `supported` (in the two Sahihs, or every matching grading accepted), `not_supported` (every matching grading weak or fabricated; red only for fabricated), `verify`, `refer` (orange, not red). `documented` now means only "the Quran quote matches the Mushaf". Tests: `test_fabricated_hadith_is_never_tagged_as_supported`, `test_weak_only_hadith_is_not_supported`.
- **A hadith listed with a bare «وقال:» is checked (preflight B2).** Before: in «وقال ﷺ: «...». وقال: «اطلبوا العلم ولو بالصين»» the second hadith was skipped silently. After: «وقال:», «وقال أيضًا:» and «وعنه:» right after a hadith in the same paragraph are extracted as hadith.
- **A reference without a colon ends the ayah (preflight B3).** Before: «إن الله مع الصابرين (البقرة 200)» became one quote and was called "not in the Mushaf". After: the ayah is found (al-Baqarah 153, al-Anfal 46) and the wrong number 200 is pointed out.
- **No distant hadith under a quote missing from the Mushaf (preflight B4).** Before: a Dorar result at 70% similarity was shown, with its grading, under the quote. After: only a strong match (85+) is shown there.

## Starting version (1 October 2026), not evaluated

See STARTING_VERSION.md.
- **The two scholars' fatwas, verbatim (plan items 42-44, owner's decision 3 Oct).** Before: a personal fatwa question got three links (the two scholars' sites, then the official body). After: the tool searches each site with its own search (`app/fatwa.py`), keeps the fatwas whose title shares most of the question's words (at most three per scholar, floor 60%), and shows them as published: Ibn Baz's fatwa in full with source and link (the site allows copying with the source named); Ibn al-Uthaymeen's question and the opening line of the answer with its series (e.g. «فتاوى نور على الدرب، الشريط رقم [270]») and a link to the full fatwa on the foundation's site (its rights are reserved). The official fatwa body follows, named by its title instead of a bare address (preflight D6). ALLaM is not involved. Only the question's topic words are sent to the two sites. Tests: `test_fatwa_question_shows_the_two_scholars_fatwas_verbatim`, `test_fatwa_question_with_nothing_close_still_refers`. Docs: README, SOURCES_AND_LICENSES.md, docs/api-and-keys.md, architecture, operations.
