# سجل المصادر والأدوات والتراخيص · Sources, tools and licenses log

As required by the challenge terms, every AI tool, model, data source and license used is listed here.
Items marked ⚠ still need confirmation by the team before final submission.

## Scientific sources (from the challenge's scientific package)

| Source | Used for | How | Terms |
|---|---|---|---|
| Mushaf of the King Fahd Glorious Qur'an Printing Complex (Uthmani script, Hafs) | Quran text, the only reference for verses | Bundled in `data/quran.json` from the npm package `quran-json` 3.1.2, which takes it from QuranEnc. Checked against Quranpedia's King Fahd Complex snapshot (qpc-hafs): the same on all 6,236 verses after encoding normalisation | quran-json: CC BY-SA 4.0 (its LICENSE.txt). ⚠ Confirm the Complex's terms for redistribution of the text |
| English translation of the meanings by Dr. Muhammad Taqi-ud-Din al-Hilali and Dr. Muhammad Muhsin Khan, King Fahd Complex, Madinah, 1417 AH (book 1948 on quranpedia.net) | The English shown beside every verse; matching English verse quotes | Bundled verbatim, footnotes kept, from QuranEnc.com `english_hilali_khan` v1.1.2 (pinned snapshot in github.com/risan/quran-json, sha256 checked by `scripts/build_quran_data.py`) | QuranEnc terms: no change to the text, credit the publisher and QuranEnc.com, state the version (v1.1.2), keep it updated |
| Saheeh International (books 1947 and 13638 on quranpedia.net) | Recognising English quotes in this wording only (most English posts use it); never shown as the translation | QuranEnc.com `english_saheeh` v1.1.2, same snapshot | As above |
| Quranpedia (quranpedia.net) | The link under every verse (`/ayahs/{surah}/{ayah}`) and to the English translation with its notes (`/surah/1/{surah}/book/1948`) | Links only | — |
| الموسوعة الحديثية، الدرر السنية (dorar.net/hadith) | Hadith texts and scholars' gradings, quoted verbatim with a link back | Live search of the public site (filtered to approved scholars), cached briefly in memory, requests spaced out; fallback to `dorar_api.json`, which Dorar offers to site owners «لعرض نتائج البحث في الموسوعة الحديثية في مواقعهم» (dorar.net/article/389) | ⚠ No terms-of-use page (dorar.net/terms is 404; «جميع الحقوق محفوظة لمؤسسة الدرر السنية»). What Dorar publishes: the JSON service «توفر لأصحاب المواقع والمنتديات عرض نتائج البحث في الموسوعة الحديثية في مواقعهم» (article/389); the search widget is free for site owners, who are asked to tell Dorar where it is installed (article/2107); FAQ 5 (dorar.net/feedback): «الموسوعات حالياً غير قابلة للتنزيل … ولا يسمح بنسخها»; the encyclopedia eases access to the scholars' books «لا الاستغناء عنها» (article/56, item 1). The JSON service is covered by article/389; the HTML site search the app uses first (for the approved-scholar filter) is not covered by any published text. So nothing is stored beyond a short in-memory cache, every grading links back to Dorar, and the team is to ask Dorar for permission |
| موسوعة الجمهرة - مفردات المحتوى الإسلامي (islamic-content.com/dictionary) | The English term shown beside a hadith grading in the English view | Only the entry's English headword (a few words), with a link to the entry; 27 entries checked by hand on 2 Oct 2026 (`app/glossary.py`) | The site allows «الاستفادة العلمية ... في الاستخدام الشخصي غير التجاري»; no definitions are copied. ⚠ Ask the site for permission to show the headwords |

### Fatwa referral for level د (team's choice, not in the package's reference table)

The package says that for personal fatwa questions the tool «لا يقدم … حكمًا مستقلًا؛ يوضح المعلومات العامة ويحيل إلى جهة مؤهلة», and names no body. The team relies on the following, in this order (team decision, 3 Oct 2026): the reader looks first in the published fatwas of the two scholars (may Allah have mercy on them), whose fatwas the team accepts; if none covers the case, the official fatwa body. The tool links to these only: it never quotes, searches, summarises or picks a fatwa, and nothing from them enters a result.

| Referral | Used for | How |
|---|---|---|
| الموقع الرسمي لسماحة الشيخ عبدالعزيز بن باز (binbaz.org.sa) | First: where the reader looks for the question in his published fatwas | Link only, no content copied |
| الموقع الرسمي لفضيلة الشيخ محمد بن صالح العثيمين (binothaimeen.net) | First: where the reader looks for the question in his published fatwas | Link only, no content copied |
| جهة الإفتاء الرسمية في بلد المستخدم، وفي المملكة: الرئاسة العامة للبحوث العلمية والإفتاء (alifta.gov.sa) | Then: where the question goes if the two scholars' fatwas do not cover the case | Link only |

### How each domain of the package's reference table is covered

| Package domain | In Tathabbut |
|---|---|
| القرآن الكريم | Used: King Fahd Complex Mushaf text and its English translation (al-Hilali & Muhsin Khan), links to quranpedia.net |
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

Only synthetic data: the evaluation cases in `eval/cases.jsonl` were written by the team. No user data is collected; user text is not stored or logged by the tool (the "report a problem" link opens a public GitHub issue containing the quoted text, and says so beside the link), and only extracted hadith wording is sent to Dorar. When the ALLaM option is used, the text is sent to the model on the team's own server.
