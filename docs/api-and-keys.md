# الواجهات البرمجية والمفاتيح ومصادرها · APIs, keys and where they come from

هذا الملف للمحكّم: كل خدمة خارجية تتصل بها الأداة، ومن يملكها، وهل تحتاج مفتاحًا، ومن أين جاء المفتاح، وأين يُحفظ، وما الذي يُرسل إليها. آخر تحديث: 5 أكتوبر 2026، مطابق للموقع المباشر.

This file is for the judges: every outside service the tool calls, who runs it, whether it needs a key, where the key came from, where it is kept, and what is sent to it. Updated 5 Oct 2026 to match the live site.

> **لا يوجد في هذا المستودع أي مفتاح ولا كلمة سر، ولن يوجد.** المفتاح المكتوب في مستودع عام يقرؤه أي أحد ويستعمله على حساب الفريق، وتلغيه بعض الجهات تلقائيًا إذا ظهر علنًا. لذلك تُقرأ كل المفاتيح من متغيرات البيئة (`app/config.py`) وتُحفظ «أسرارًا» في إعدادات الاستضافة، ويبيّن هذا الملف مصدر كل مفتاح دون قيمته.
>
> **No key or password is in this repository, by design.** Keys are read from environment variables (`app/config.py`) and kept as secrets in the hosting settings; this file says where each key comes from, never its value.

## 1. المفاتيح على الموقع المباشر الآن · Keys on the live site now

| المفتاح · Key | الجهة · Provider | من أين جاء · Where it came from | التكلفة · Cost | أين يُحفظ · Kept in | لماذا · Why |
|---|---|---|---|---|---|
| `TATHABBUT_LLM_FALLBACK_API_KEY` | **Groq** (groq.com) | أنشأه الفريق من حسابه في https://console.groq.com ← API Keys ← Create API Key (يبدأ بـ `gsk_`) · Created by the team in its Groq console | الطبقة المجانية، دون بطاقة ائتمان (قرابة 1000 طلب يوميًا) · Free tier, no card | Hugging Face ← Space `3rb/tathabbut` ← Settings ← Variables and secrets ← **Secret** | تشغيل النموذج المفتوح `openai/gpt-oss-120b` (ترخيص Apache-2.0) في مهامه الضيقة · Runs the open model gpt-oss-120b |

هذا هو المفتاح الوحيد الذي يحتاجه الموقع المباشر. علّام يعمل داخل الحاوية نفسها فلا مفتاح له، والدرر وموقعا الشيخين وquranpedia عامة دون حساب.

This is the only key the live site needs: ALLaM runs inside the container (no key), and Dorar, the two Shaykhs' sites and quranpedia are public.

**المتغيرات غير السرية في الـSpace** (قيمها ظاهرة هنا لأنها ليست أسرارًا) · Non-secret Space variables:

| المتغير · Variable | القيمة على الموقع · Live value |
|---|---|
| `TATHABBUT_LLM` | `llamacpp` (علّام داخل الحاوية) |
| `TATHABBUT_LLM_FALLBACK_BASE_URL` | `https://api.groq.com/openai/v1` |
| `TATHABBUT_LLM_FALLBACK_MODEL` | `openai/gpt-oss-120b` |
| `TATHABBUT_LLM_FALLBACK_FIRST` | `arabic,citations,match` (ومعها `fatwa` و`intent` تلقائيًا) |

يمكن التحقق منها في أي وقت: `curl https://3rb-tathabbut.hf.space/api/health` يعرض النموذجين، وأي المهام تذهب للنموذج السريع، وآخر نجاح وآخر خطأ لكل نموذج (نوع الخطأ ورقمه فقط، دون مفاتيح ولا نصوص).

## 2. الخدمات التي تستدعيها الأداة أثناء الفحص · Services called while checking

| الخدمة · Service | الجهة المالكة · Owner | ما يُرسل إليها · What is sent | مفتاح؟ | في الشيفرة |
|---|---|---|---|---|
| الموسوعة الحديثية: `https://www.dorar.net/hadith/search`، وبديلًا `https://dorar.net/dorar_api.json` | مؤسسة الدرر السنية، من مصادر الحزمة العلمية للتحدي | لفظ الحديث المستخرج وحده · Only the hadith wording | لا · No. فاصل 0.6 ثانية وتخزين مؤقت | `app/dorar.py` |
| فتاوى ابن باز: `https://binbaz.org.sa/api/search` ثم `https://binbaz.org.sa/fatwas/{id}` | الموقع الرسمي لسماحة الشيخ عبدالعزيز بن باز | كلمات موضوع السؤال وحدها · Topic words only | لا. الموقع: «النقل متاح لكل مسلم بشرط ذكر المصدر» | `app/fatwa.py` |
| فتاوى ابن عثيمين: `https://shekhcp.binothaimeen.net/api/search-data` ثم `https://shekhapi.binothaimeen.net/lessons/audios/show/{id}` | مؤسسة الشيخ محمد بن صالح العثيمين الخيرية | كلمات موضوع السؤال وحدها | لا. الحقوق محفوظة: السؤال وأول الجواب ورابطه فقط | `app/fatwa.py` |
| النموذج السريع على Groq: `https://api.groq.com/openai/v1/chat/completions` | Groq؛ والنموذج `gpt-oss-120b` من OpenAI بترخيص Apache-2.0 | بحسب المهمة: النص المفحوص (حتى 3000 حرف) في الفحص المعمّق؛ أو الاقتباس المترجم وحده؛ أو السؤال الذي لم تعرفه القواعد (حتى 400 حرف)؛ أو سؤال الحكم مع نصوص الفتاوى المنشورة. ولا يُحفظ شيء | نعم: `TATHABBUT_LLM_FALLBACK_API_KEY` (القسم 1) | `app/llm.py` |
| علّام ALLaM-7B-Instruct-preview | سدايا (SDAIA)، ترخيص Apache-2.0. يعمل داخل الحاوية بـ llama.cpp | لا يغادر شيء الخادم · Nothing leaves the server | لا | `app/llm.py` (`LlamaCpp`) |
| تنزيل نسخة علّام GGUF عند بناء الحاوية: `bartowski/ALLaM-AI_ALLaM-7B-Instruct-preview-GGUF` | مستودع عام على Hugging Face | لا شيء من نص الزائر | لا | `app/llm.py` |

## 3. ما جُلب مرة واحدة وحُفظ في المستودع · Fetched once, kept in the repository

| البيانات · Data | المصدر · Source | كيف جُلبت · How | التحقق · Check |
|---|---|---|---|
| نص مصحف مجمع الملك فهد وترجمته الإنجليزية (`data/quran.json`) | مجمع الملك فهد، عبر حزمة quran-json | `scripts/build_quran_data.py` | مطابق لنص quranpedia في 6236 آية (`eval/mushaf_check.md`) |
| ترجمات معاني القرآن بتسع لغات (`data/translations/`) | quranpedia.net (من مصادر الحزمة) | `scripts/fetch_translations.py` | بصمة sha256 لكل ملف تُتحقق عند كل تشغيل |
| فتاوى ابن باز في صفحة أركان الإسلام (`data/pillars_sources.json`) | binbaz.org.sa | جُلبت بشيفرة الأداة نفسها (`app/fatwa.py`) في 5 أكتوبر | `tests/test_pillars.py`: كل اقتباس في الصفحة موجود فيها بنصه |
| الأرشيف (`data/archive.json`) | الموقع المباشر نفسه | `scripts/build_archive.py` | كل حكم برابطه في الدرر |

## 4. ما يُعرض رابطًا فقط · Shown as links only

| المصدر | الاستعمال |
|---|---|
| quranpedia.net | رابط كل آية وترجمتها |
| موسوعة الجمهرة (islamic-content.com/dictionary) | رابط المصطلح بجانب الحكم |
| alifta.gov.sa | جهة الإفتاء الرسمية بعد فتاوى الشيخين |
| binbaz.org.sa/books | رسالة «كيفية صلاة النبي ﷺ» وترجماتها الرسمية في صفحة أركان الإسلام |
| GitHub Issues | زر «أبلغ عن خطأ» يفتح صفحة بلاغ في متصفح الزائر، دون مفتاح |

## 5. واجهة تثبّت نفسها · Tathabbut's own API

`POST /api/check` مفتوحة دون مفتاح للعرض والتحكيم، ومحدودة بعشرين طلبًا كل عشر دقائق لكل زائر لحماية المصادر. ومعها `GET /api/health`، و`GET /api/sources`، و`GET /api/archive`، و`GET /api/pillars`، وخادم MCP في `/mcp`، والتوثيق التفاعلي في `/docs`. انظر [api.md](api.md) و[mcp.md](mcp.md).

## 6. مفاتيح الحسابات والنشر · Account and deployment keys

| المفتاح · Key | الاستعمال · Use | أين يُحفظ · Where |
|---|---|---|
| `TATHABBUT_LLM_FALLBACK_API_KEY` | النموذج السريع (القسم 1) | Hugging Face ← Space ← Settings ← Variables and secrets |
| `HF_TOKEN` | اختياري، لسير النشر اليدوي `.github/workflows/deploy-space.yml` فقط. النشر الفعلي بإعادة بناء الـSpace (Factory rebuild)، والـSpace ينسخ هذا المستودع العام فلا يحتاجه | GitHub ← Settings ← Secrets and variables ← Actions |
| `TATHABBUT_LLM_API_KEY` | غير مستعمل الآن: لعلّام على خادم خارجي متوافق مع OpenAI إن نُقل إليه | Hugging Face ← Space ← Settings |

## 7. أدوات الذكاء الاصطناعي في بناء المشروع · AI tools used to build the project

الأداة أثناء عملها تستدعي علّام والنموذج السريع فقط، ولا تستدعي واجهة Claude البرمجية ولا تحمل مفتاحًا لها. أما في التطوير فقد استعنّا بـ Claude (Anthropic) عبر Claude Code بحساب الفريق في كتابة الكود والاختبارات والتوثيق ومسودات حالات التقييم. التفاصيل في [SOURCES_AND_LICENSES.md](../SOURCES_AND_LICENSES.md) و[team.md](team.md).

At run time the tool calls ALLaM and the fast model only; it never calls the Claude API and holds no Claude key. During development we used Claude (Anthropic) through Claude Code on the team's account to write code, tests, documentation and drafts of the evaluation cases.

## 8. كيف يتحقق المحكّم · How a judge can verify

```bash
grep -rnE "https?://" app/*.py              # every outside address the server code calls
grep -n "_env(" app/config.py                # every setting and key comes from the environment
git log -p | grep -E "gsk_|hf_[A-Za-z0-9]{20}"   # no key in the whole history (prints nothing)
curl https://3rb-tathabbut.hf.space/api/health   # models, which jobs go to the fast model, Dorar, deployed commit
```
