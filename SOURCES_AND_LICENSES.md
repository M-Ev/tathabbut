# سجل المصادر والأدوات والتراخيص · Sources, tools and licenses log

As required by the challenge terms, every AI tool, model, data source and license used is listed here.
Items marked ⚠ still need confirmation by the team before final submission.

## Scientific sources (from the challenge's scientific package)

| Source | Used for | How | Terms |
|---|---|---|---|
| Mushaf of the King Fahd Glorious Qur'an Printing Complex (Uthmani script), via QuranEnc | Quran text, the only reference for verses | Bundled in `data/quran.json` from the npm package `quran-json` 3.1.2 | quran-json: CC-BY-4.0. ⚠ Confirm the Complex's and QuranEnc's terms for redistribution of the text |
| الموسوعة الحديثية، الدرر السنية (dorar.net/hadith) | Hadith texts and scholars' gradings, quoted verbatim with a link back | Live search of the public site (filtered to approved scholars), cached, requests spaced out; fallback to the public `dorar_api.json` | ⚠ No published API license. Permission to display gradings automatically has been requested / is to be requested from Dorar |
| Saheeh International English translation, via Tanzil | English display and matching of English verse quotes | Bundled from `quran-json` 3.1.2 | ⚠ Tanzil translation terms (verbatim, with attribution) |
| الرئاسة العامة للبحوث العلمية والإفتاء (alifta.gov.sa) | Referral point for personal fatwa questions (level د) | Link only | — |

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
| quran-json 3.1.2 (data packaging) | CC-BY-4.0 |
| dorar-hadith-api by Ahmed El-Tabarani (reference for Dorar's page markup and scholar filter ids; no code copied) | MIT |

## Fonts

| Font | License |
|---|---|
| Readex Pro (challenge identity font), via Google Fonts | SIL Open Font License 1.1 |
| Amiri Quran, via Google Fonts | SIL Open Font License 1.1 |

## Data

Only synthetic data: the evaluation cases in `eval/cases.jsonl` were written by the team. No user data is collected; user text is not stored or logged, and only extracted hadith wording is sent to Dorar.
