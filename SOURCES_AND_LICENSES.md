# سجل المصادر والأدوات والتراخيص · Sources, tools and licenses log

As required by the challenge terms, every AI tool, model, data source and license used is listed here.
Items marked ⚠ still need confirmation by the team before final submission.

## Scientific sources (from the challenge's scientific package)

| Source | Used for | How | Terms |
|---|---|---|---|
| Mushaf of the King Fahd Glorious Qur'an Printing Complex (Uthmani script, Hafs) | Quran text, the only reference for verses | Bundled in `data/quran.json` from the npm package `quran-json` 3.1.2, which takes it from QuranEnc. Checked against Quranpedia's King Fahd Complex snapshot (qpc-hafs): the same on all 6,236 verses after encoding normalisation | quran-json: CC BY-SA 4.0 (its LICENSE.txt). ⚠ Confirm the Complex's terms for redistribution of the text |
| English translation of the meanings by Dr. Muhammad Taqi-ud-Din al-Hilali and Dr. Muhammad Muhsin Khan, King Fahd Complex, Madinah, 1417 AH (book 1948 on quranpedia.net) | The English shown beside every verse; matching English verse quotes | Bundled verbatim, footnotes kept, from QuranEnc.com `english_hilali_khan` v1.1.2 (pinned snapshot in github.com/risan/quran-json, sha256 checked by `scripts/build_quran_data.py`) | QuranEnc terms: no change to the text, credit the publisher and QuranEnc.com, state the version (v1.1.2), keep it updated |
| Saheeh International (books 1947 and 13638 on quranpedia.net) | Recognising English quotes in this wording only (most English posts use it); never shown as the translation | QuranEnc.com `english_saheeh` v1.1.2, same snapshot | As above |
| Urdu translation of the meanings by Muhammad Ibrahim Junagarhi, King Fahd Complex print (book 1966 on quranpedia.net) | Matching Urdu verse quotes; shown beside the Mushaf text for an Urdu quote (plan item 36) | Fetched page by page from quranpedia.net by `scripts/fetch_translations.py` on 2026-10-03T22:21Z (each surah's verse count checked against the Mushaf), stored verbatim in `data/translations/ur_junagarhi.json`, sha256 `571fb4301cf0fe5bbc7f8dd041643c6966a577a6d24afb30b146445da0beed31`, checked at every start; a changed file is not used. One footnote marker (6:28) is dropped for display; the link opens the full text | Quranpedia's footer: «الاستفادةُ من الموسوعةِ حقٌّ لكلِّ مسلم»; its About page says it aims to make its data available to developers. ⚠ The translation is the King Fahd Complex's: confirm the Complex's terms, as for the Mushaf text |
| Indonesian translation of the meanings, King Fahd Complex with Indonesia's Ministry of Religious Affairs (book 1961 on quranpedia.net) | Matching Indonesian verse quotes; shown beside the Mushaf text for an Indonesian quote (plan item 36) | As above, on 2026-10-03T22:24Z, `data/translations/id_kfc.json`, sha256 `502d06b449214b7ae226d07a8392d3cb93286af47b9d7f2d83ccc2c1998fef5d`. The text's 1,593 footnote markers (numbers 1 to 1610) are dropped for matching and display; the file keeps them | As above ⚠ |
| Quranpedia (quranpedia.net) | The link under every verse (`/ayahs/{surah}/{ayah}`) and to the English translation with its notes (`/surah/1/{surah}/book/1948`) | Links only | — |
| الموسوعة الحديثية، الدرر السنية (dorar.net/hadith) | Hadith texts and scholars' gradings, quoted verbatim with a link back | Live search of the public site (filtered to approved scholars), cached briefly in memory, requests spaced out; fallback to `dorar_api.json`, which Dorar offers to site owners «لعرض نتائج البحث في الموسوعة الحديثية في مواقعهم» (dorar.net/article/389) | ⚠ No terms-of-use page (dorar.net/terms is 404; «جميع الحقوق محفوظة لمؤسسة الدرر السنية»). What Dorar publishes: the JSON service «توفر لأصحاب المواقع والمنتديات عرض نتائج البحث في الموسوعة الحديثية في مواقعهم» (article/389); the search widget is free for site owners, who are asked to tell Dorar where it is installed (article/2107); FAQ 5 (dorar.net/feedback): «الموسوعات حالياً غير قابلة للتنزيل … ولا يسمح بنسخها»; the encyclopedia eases access to the scholars' books «لا الاستغناء عنها» (article/56, item 1). The JSON service is covered by article/389; the HTML site search the app uses first (for the approved-scholar filter) is not covered by any published text. So nothing is stored beyond a short in-memory cache, every grading links back to Dorar, and the team is to ask Dorar for permission |
| موسوعة الجمهرة - مفردات المحتوى الإسلامي (islamic-content.com/dictionary) | The English term shown beside a hadith grading in the English view | Only the entry's English headword (a few words), with a link to the entry; 27 entries checked by hand on 2 Oct 2026 (`app/glossary.py`) | The site allows «الاستفادة العلمية ... في الاستخدام الشخصي غير التجاري»; no definitions are copied. ⚠ Ask the site for permission to show the headwords |

### Fatwa referral for level د (team's choice, not in the package's reference table)

The package says that for personal fatwa questions the tool «لا يقدم … حكمًا مستقلًا؛ يوضح المعلومات العامة ويحيل إلى جهة مؤهلة», and names no body. The team relies on the following, in this order (team decision, 3 Oct 2026): the reader looks first in the published fatwas of the two scholars (may Allah have mercy on them), whose fatwas the team accepts; if none covers the case, the official fatwa body. Since 4 Oct 2026 (owner's decision on 3 Oct: «تجيب فتاويهم لازم», then «نص الفتوى»), the tool shows the two scholars' published fatwas on close questions, verbatim, with their source and link (`app/fatwa.py`). They are found through each site's own search and ordered by word overlap with the question; the language model never writes, summarises or picks a fatwa. A fatwa is shown as published, never as the tool's answer to the user's case, and the official body is always named after them.

| Referral | Used for | How |
|---|---|---|
| الموقع الرسمي لسماحة الشيخ عبدالعزيز بن باز (binbaz.org.sa) | First: his published fatwas on close questions | Full text verbatim with source and link. Terms (site footer, checked 3 Oct 2026): «جميع الحقوق محفوظة والنقل متاح لكل مسلم بشرط ذكر المصدر» |
| موقع مؤسسة الشيخ محمد بن صالح العثيمين الخيرية (binothaimeen.net) | First: his published fatwas on close questions | Question and the opening line of the answer verbatim, source and a link to the full fatwa on the foundation's site. Terms (checked 3 Oct 2026): «جميع الحقوق محفوظة © لمؤسسة الشيخ محمد بن صالح العثيمين الخيرية», and the Shaykh's word on the homepage asks that his words not be published elsewhere without permission. The full text is not shown unless the foundation permits it; any permission request is sent by the team, and none has been sent or received yet |
| جهة الإفتاء الرسمية في بلد المستخدم، وفي المملكة: الرئاسة العامة للبحوث العلمية والإفتاء (alifta.gov.sa) | Then: where the question goes if the two scholars' fatwas do not cover the case | Link only |

### Translations of the meanings shown to readers (5 Oct)

From quranpedia.net (named in the package), fetched by `scripts/fetch_translations.py`, each with its source URL, fetch date and sha256 in `data/translations/`: Bengali (Abu Bakr Muhammad Zakaria, book 1967), Turkish (King Fahd Complex, 1959), French (Muhammad Hamidullah, 27812), Spanish (Muhammad Isa Garcia, 1950), Hindi (Aziz ul-Haq al-Umari, 1986), Chinese (Muhammad Makin / Ma Jian, 1974), Japanese (Ryoichi Mita, 1976). Shown beside the Mushaf text for readers of these languages; not used to match quotes.

### The pillars page «أركان الإسلام» (owner's request, 5 Oct)

- Every ruling sentence on the page is quoted word for word from eight fatwas on binbaz.org.sa, the official site of Shaykh Abd al-Aziz ibn Baz (the site publishes its fatwas in full): the description of the prayer from the takbir to the salam (fatwas 10166 and 6122), of wudu (18835, 10255), raising the hands (4103), placing them on the chest (12198), and one who cannot recite al-Fatiha (20532, 3711). The fetched texts are kept in `data/pillars_sources.json`; `tests/test_pillars.py` fails if any quote or any phrase given to say is not in them.
- The links to the Shaykh's treatise «كيفية صلاة النبي ﷺ» and its official translations (English, Urdu, Spanish, Bengali, Turkish, Chinese, French, Hindi, Japanese) point to his site; nothing is copied from them.
- The hadith «بني الإسلام على خمس» is shown as Dorar gives it (al-Bukhari 8, Muslim 16), found by Tathabbut's own check. The verses come from the Mushaf file and their meanings from the approved translations above (`/api/pillars`).
- The drawn figures and the Latin-letter pronunciations were made by the team (with Claude Code) as learning aids; faceless figures, no photographs.

### How each domain of the package's reference table is covered

| Package domain | In Tathabbut |
|---|---|
| القرآن الكريم | Used: King Fahd Complex Mushaf text and its English (al-Hilali & Muhsin Khan), Urdu (Junagarhi) and Indonesian translations, links to quranpedia.net |
| الحديث النبوي | Used: dorar.net/hadith, gradings of the 13 approved scholars only; the Sahihayn are marked first. Shamela (shamela.ws) is planned, not used yet |
| الترجمة والمصطلحات | Used: موسوعة الجمهرة - مفردات المحتوى الإسلامي, for the English of hadith grading terms |
| الموضوعات الدعوية (dawa.center، الجمهرة) | Not used: the tool writes no da'wah content |
| التفسير | Not used: the tool does not explain ayat |
| العقيدة، الفقه العام، السيرة والتاريخ، الشبهات (بينات) | Not used: the tool answers no questions; personal fatwa questions are referred (level د) |

## Model

| Model | Used for | License |
|---|---|---|
| ALLaM-7B-Instruct-preview (SDAIA / HUMAIN), `humain-ai/ALLaM-7B-Instruct-preview` | Spotting citations the rules missed; Arabic search wording for non-Arabic quotes; picking which Arabic source text matches a translation. Never grades or rules. | Apache-2.0 (per the model's Hugging Face listing) |
| GGUF 4-bit build: `bartowski/ALLaM-AI_ALLaM-7B-Instruct-preview-GGUF` (Q4_K_M) | Running ALLaM on a free CPU | Apache-2.0 |
| Fast model (owner's decisions, 4 and 5 Oct): `openai/gpt-oss-120b` on Groq's free tier (earlier `Qwen/Qwen3-235B-A22B-Instruct-2507` through Hugging Face Inference Providers). On the live site it answers first for the jobs listed in `TATHABBUT_LLM_FALLBACK_FIRST` (citation extraction, Arabic search wording, picking the matching source, reading what a free question asks about, choosing the fatwa sentence to quote); ALLaM answers when it fails, and answers every other job | The same narrow jobs under the same guards (verbatim extraction, verbatim fatwa sentence, pick checked against its own wording); each report names the model that answered (`model.answered_by`) | Apache-2.0 (gpt-oss-120b; Qwen3 likewise) |

## AI tools used to build the project

| Tool | Used for | Human role |
|---|---|---|
| Claude (Anthropic), through Claude Code | Writing the code, tests, documentation and the first draft of the evaluation cases | The team set the requirements and the Sharia rules (approved scholars, wording, display order), reviews the output, and the Sharia reviewer reviews the evaluation set. The code is AI-assisted and is not presented as original human work. |

## Software libraries

| Library | License |
|---|---|
| FastAPI | MIT |
| Uvicorn | BSD-3-Clause |
| HTTPX | BSD-3-Clause |
| Beautiful Soup 4 | MIT |
| RapidFuzz | MIT |
| llama-cpp-python | MIT |
| huggingface_hub | Apache-2.0 |
| pytest (tests only) | MIT |
| quran-json 3.1.2 (data packaging) | CC BY-SA 4.0 (package.json says CC-BY-4.0; its LICENSE.txt is BY-SA) |
| dorar-hadith-api by Ahmed El-Tabarani (reference for Dorar's page markup and scholar filter ids; no code copied) | MIT |

## Fonts

| Font | License |
|---|---|
| Readex Pro (challenge identity font, bundled from @fontsource/readex-pro) | SIL Open Font License 1.1 |
| Amiri Quran (bundled, from @fontsource/amiri-quran) | SIL Open Font License 1.1 |

## Data

Only synthetic data: the evaluation cases in `eval/cases.jsonl` were drafted with Claude (see the tools table above); their review by the team's Sharia reviewer is pending. No user data is collected; user text is not stored or logged by the tool (the "report a problem" link opens a public GitHub issue containing the quoted text, and says so beside the link), and only extracted hadith wording is sent to Dorar. In the deep check the text is sent to ALLaM on the team's own server or, when ALLaM is not available, to the fallback model at its hosting provider; the report names the model.
