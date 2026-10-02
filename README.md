---
title: Tathabbut
emoji: 📖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
license: apache-2.0
short_description: Traces Quran and hadith citations to their Arabic sources
---

# تثبّت · Tathabbut

**مدقق ذكي متعدد اللغات للاستشهادات الشرعية.** فريق «قيد الأوابد»، مسار أدوات المعرفة والتحقق لتمكين المعرّفين بالإسلام، تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي (مؤسسة باذل الأهلية، 2026).

يلصق المعرّف بالإسلام أو صانع المحتوى منشورًا أو درسًا أو إجابة روبوت محادثة، فيستخرج تثبّت كل آية وحديث، ويتتبع كل واحد إلى مصدره العربي:
- **الآيات** تُطابق مع نص مصحف مجمع الملك فهد، فيظهر موضعها، والكلمات المخالفة إن نُقلت بخطأ، وخطأ العزو إن كُتب رقم سورة أو آية غير صحيح. نص القرآن لا يُولَّد أبدًا.
- **الأحاديث** يُبحث عنها في الموسوعة الحديثية للدرر السنية، وتُعرض أحكام علماء الحديث المعتمدين حرفيًا مع اسم قائل كل حكم: أحكام أئمة الحديث أولًا ثم أحكام المحققين المعاصرين، كلٌّ مرتب بسنة الوفاة، دون ترجيح آلي.
- **إن لم يجد** قال ذلك صراحة وأحال إلى المختص. وأسئلة الفتوى الشخصية تُحال إلى الرئاسة العامة للبحوث العلمية والإفتاء.

النموذج اللغوي (علّام من سدايا) يستخرج ويطابق فقط، ولا يُصدر حكمًا ولا فتوى. وكل استشهاد يقترحه يجب أن يوجد حرفيًا في نص المستخدم وإلا يُحذف.

![واجهة تثبّت: آية منقولة بخطأ في كلمتين مع عزو خطأ، وحديث بأحكام العلماء](docs/screenshots/ui-ar.png)

### حالة الدليل لكل استشهاد

| الحالة | معناها |
|---|---|
| **موثّق المصدر** | آية مطابقة للمصحف، أو حديث وُجدت له أحكام العلماء المعتمدين |
| **يحتاج مزيدًا من التحقق** | لفظ مختلف، أو عزو خطأ، أو لفظ مقارب |
| **يُحال إلى مختص** | لم يوجد في المصدر، أو سؤال فتوى شخصية |

وتحت كل استشهاد «سبب الحكم»: كيف عرفت الأداة ما قالته، ورابط المصدر، وزر «أبلغ عن خطأ في هذه النتيجة».

## ما يعمل الآن وما يُبنى في أيام التحدي · Status

| يعمل الآن (نسخة البداية) | يُبنى من 4 إلى 6 أكتوبر |
|---|---|
| استخراج الآيات والأحاديث بالعربية والإنجليزية | التحقق الحي من الدرر السنية |
| مطابقة كل آية مع المصحف، وفروق الكلمات، وخطأ العزو | تشغيل علّام على الاستضافة وقياس سرعته |
| البحث في الدرر مقيدًا بالعلماء المعتمدين، بمجموعتين (اختُبر على نماذج ثابتة فقط) | أرقام التقييم على مجموعة المختصة الشرعية |
| حالة الدليل وسبب الحكم والإحالة | الأردية والإندونيسية والفرنسية، من ترجمات مجمع الملك فهد أو الواردة في quranpedia.net |
| واجهة عربية وإنجليزية، والواجهة البرمجية | عرض فحص إجابات روبوتات المحادثة |

## Tathabbut in English

Paste a post, a lecture or a chatbot answer. Tathabbut extracts every Quran verse and hadith and traces each one to its Arabic source. Verses are matched against the King Fahd Complex Mushaf text (word-level differences and wrong references are shown). Hadith are looked up in the Dorar hadith encyclopedia and the approved scholars' gradings are quoted verbatim, grouped as classical imams then modern editors, with no automated preference. When nothing is found it says so and refers to a specialist. The language model (SDAIA's ALLaM) only extracts and matches; it never grades or rules.

## التشغيل · Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --port 7860
# open http://localhost:7860  · API docs: http://localhost:7860/docs
```

مع علّام محليًا · With ALLaM in-process (downloads a 4-bit GGUF, about 4.5 GB):

```bash
pip install -r requirements-llm.txt
TATHABBUT_LLM=llamacpp uvicorn app.main:app --port 7860
```

أو أي خادم متوافق مع OpenAI · Or any OpenAI-compatible endpoint serving ALLaM:

```bash
TATHABBUT_LLM=openai TATHABBUT_LLM_BASE_URL=https://.../v1 TATHABBUT_LLM_API_KEY=... TATHABBUT_LLM_MODEL=... \
  uvicorn app.main:app --port 7860
```

Docker / Hugging Face Space: `docker build -t tathabbut . && docker run -p 7860:7860 tathabbut`. This README's header is the Space configuration.

| Variable | Default | Meaning |
|---|---|---|
| `TATHABBUT_LLM` | `none` (also in the Dockerfile: the live Space runs without the model until the team's ALLaM endpoint is connected) | `llamacpp`, `openai` or `none` |
| `TATHABBUT_GGUF_REPO` / `_FILE` | bartowski ALLaM-7B-Instruct Q4_K_M | GGUF to download |
| `TATHABBUT_DORAR` | `1` | `0` turns hadith lookup off |
| `TATHABBUT_MAX_CHARS` | `8000` | maximum text length |

## الواجهة البرمجية · API

`POST /api/check` with `{"text": "...", "deep": false}` returns every citation with its status, source, verbatim gradings and any referral. Use it to check an Islamic chatbot's answer before it is shown.

Each citation carries `tier`: `documented`, `verify` or `refer` (the track's evidence-status criterion). Statuses: `verified` (matches the Mushaf), `differs` (wording differs, see `diff`), `not_in_mushaf`, `graded` (found with approved gradings), `found_similar` (similar wording), `not_found` (referred), `needs_model`, `source_error`.

## الاختبارات والتقييم · Tests and evaluation

```bash
pip install -r requirements-dev.txt
pytest                      # offline unit tests (Dorar is mocked)
python eval/run_eval.py     # evaluation set, live sources -> eval/report.md
```

## البنية · Layout

| Path | What |
|---|---|
| `app/extract.py` | rule-based citation extraction (Arabic, English), references like (البقرة: 255) or (2:255) |
| `app/quran.py` | Mushaf matching on a consonant skeleton, word diff, reference check |
| `app/dorar.py` | Dorar hadith search filtered to the approved scholars, with cache and spacing |
| `app/scholars.py` | approved scholars, groups, wording rules, narrator-statement rule |
| `app/llm.py` | swappable model layer (ALLaM via llama.cpp or any OpenAI-compatible API) |
| `app/pipeline.py` | the checking pipeline and referral logic |
| `static/` | Arabic/English web interface in the challenge identity |
| `data/quran.json` | Mushaf text (King Fahd Complex) and its English translation by al-Hilali & Muhsin Khan (King Fahd Complex, 1417 AH); Saheeh International is kept only to recognise English quotes |
| `eval/` | synthetic evaluation set and runner |

## التوثيق · Documentation

| الملف | المحتوى |
|---|---|
| [docs/architecture.md](docs/architecture.md) | مسار الفحص، والمبدأ الحاكم، وحالة الدليل، والوحدات |
| [docs/operations.md](docs/operations.md) | الاستضافة والتكلفة، والتعطل والبدائل، والأدوار، وخطة الاستمرار |
| [docs/limitations.md](docs/limitations.md) | القيود المعروفة وكيف نتعامل معها |
| [docs/design-system.md](docs/design-system.md) | نظام التصميم |
| [eval/README.md](eval/README.md) | مجموعة التقييم ومقاييسها |

See [SOURCES_AND_LICENSES.md](SOURCES_AND_LICENSES.md) for every source, model, tool and license, and [STARTING_VERSION.md](STARTING_VERSION.md) for what existed before the challenge's build days.

## الترخيص · License

Code: Apache-2.0 (see LICENSE). Data and model keep their own licenses, listed in SOURCES_AND_LICENSES.md.
