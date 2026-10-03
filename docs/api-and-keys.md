# الواجهات البرمجية والمفاتيح ومصادرها · APIs, keys and where they come from

هذا الملف يبيّن للمحكّم كل خدمة خارجية تتصل بها الأداة، ومن يملكها، وهل تحتاج مفتاحًا، ومن أين يأتي المفتاح، وما الذي يُرسل إليها. ولا يوجد في المستودع أي مفتاح أو كلمة سر: كل المفاتيح تُقرأ من متغيرات البيئة (`app/config.py`) وتوضع في إعدادات الاستضافة السرية.

This file lists every outside service the tool talks to, who runs it, whether it needs a key, where that key comes from, and what is sent to it. No key or password is stored in this repository: every key is read from environment variables (`app/config.py`) and set as a secret in the hosting settings.

## 1. الخدمات التي تستدعيها الأداة أثناء الفحص · Services called while checking

| الخدمة · Service | الجهة المالكة · Owner | ما يُرسل · What is sent | مفتاح؟ · Key? | مصدر المفتاح · Key source | في الشيفرة · Code |
|---|---|---|---|---|---|
| الموسوعة الحديثية (اتصال مباشر من خادم الأداة دون وسيط): البحث في `https://www.dorar.net/hadith/search`، وواجهة `https://dorar.net/dorar_api.json` بديلًا | مؤسسة الدرر السنية (dorar.net)، من مصادر الحزمة العلمية للتحدي | لفظ الحديث المستخرج فقط، لا نص المستخدم كاملًا · Only the extracted hadith wording | لا · No | عامة دون حساب · Public, no account. نحترم حدودها بفاصل 0.6 ثانية بين الطلبات وتخزين مؤقت للنتائج | `app/dorar.py` |
| النموذج اللغوي علّام (ALLaM-7B-Instruct-preview) عبر واجهة متوافقة مع OpenAI (`/v1/chat/completions`) | النموذج من سدايا (SDAIA)، مفتوح بترخيص Apache-2.0؛ والخادم Inference Endpoint خاص بالفريق على Hugging Face | النص المفحوص (حتى 3000 حرف) عند تفعيل «استعن بالنموذج اللغوي علّام» فقط · The checked text, only when the ALLaM option is ticked | نعم · Yes: `TATHABBUT_LLM_API_KEY` | مفتاح وصول (Access Token) من حساب الفريق في Hugging Face، يُنشأ من Settings ← Access Tokens، ويوضع سرًّا في إعدادات الـ Space · A Hugging Face access token from the team's account, stored as a Space secret | `app/llm.py` (`OpenAIBackend`)، والعنوان في `TATHABBUT_LLM_BASE_URL` |
| فتاوى سماحة الشيخ عبدالعزيز بن باز: البحث `https://binbaz.org.sa/api/search` (بحث الموقع نفسه)، ثم صفحة الفتوى `https://binbaz.org.sa/fatwas/{id}` | الموقع الرسمي لسماحة الشيخ (مؤسسة الشيخ عبدالعزيز بن باز الخيرية). اختيار الفريق في المستوى (د)، خارج جدول الحزمة | كلمات موضوع سؤال الفتوى فقط (دون صيغة السؤال ولا بقية النص) · Only the topic words of the fatwa question | لا · No | عامة دون حساب. تذييل الموقع: «النقل متاح لكل مسلم بشرط ذكر المصدر»، فتُعرض الفتوى كاملة بنصها مع مصدرها ورابطها. فاصل 0.5 ثانية وتخزين مؤقت | `app/fatwa.py` |
| فتاوى فضيلة الشيخ محمد بن صالح العثيمين: البحث `https://shekhcp.binothaimeen.net/api/search-data` (بحث الموقع نفسه)، ثم `https://shekhapi.binothaimeen.net/lessons/audios/show/{id}` | موقع مؤسسة الشيخ محمد بن صالح العثيمين الخيرية. اختيار الفريق في المستوى (د)، خارج جدول الحزمة | كلمات موضوع سؤال الفتوى فقط · Only the topic words of the fatwa question | لا · No | عامة دون حساب. الحقوق محفوظة للمؤسسة، فيُعرض السؤال وأول الجواب بنصه ورابط الفتوى في موقع المؤسسة، لا الفتوى كاملة · All rights reserved: question, opening line and link only | `app/fatwa.py` |
| تنزيل علّام لتشغيله داخل الحاوية (الطريقة المحلية `llamacpp`) | نسخة GGUF عامة على Hugging Face: `bartowski/ALLaM-AI_ALLaM-7B-Instruct-preview-GGUF` | لا شيء من نص المستخدم؛ تنزيل ملف النموذج مرة واحدة · Nothing from the user; a one-time model download | لا · No | المستودع عام · Public repository | `app/llm.py` (`LlamaCppBackend`) |

الرابط الحي الآن يعمل بـ `TATHABBUT_LLM=none`، أي دون علّام، فلا يُرسل إليه شيء حتى يُفعَّل خادم الفريق. · The live link currently runs with `TATHABBUT_LLM=none`, so nothing is sent to a model until the team's endpoint is switched on.

## 2. ما لا يُستدعى برمجيًا بل يُعرض رابطًا فقط · Shown as links only (no API call)

| المصدر · Source | الاستعمال · Use |
|---|---|
| نص مصحف مجمع الملك فهد وترجمته الإنجليزية | مضمّن في الأداة (`data/quran.json`)، فلا اتصال بأي خدمة لمطابقة الآيات · Bundled, no network call |
| quranpedia.net | رابط كل آية لموضعها · Link to each ayah |
| موسوعة الجمهرة (islamic-content.com/dictionary) | رابط المصطلح بجانب الحكم · Link beside each grading term |
| alifta.gov.sa | رابط جهة الإفتاء الرسمية بعد فتاوى الشيخين · Link to the official fatwa body after the two scholars' fatwas |
| GitHub Issues | زر «أبلغ عن خطأ» يفتح صفحة بلاغ عامة في متصفح المستخدم، دون مفتاح ودون إرسال من الخادم · Opens a public issue page in the user's browser |

## 3. واجهة تثبّت نفسها · Tathabbut's own API

`POST /api/check` مفتوحة دون مفتاح للعرض والتحكيم، ومحدودة بعشرين طلبًا كل عشر دقائق لكل عنوان IP لحماية المصادر التي نستدعيها (`app/main.py`). وتوجد أيضًا `GET /api/health` و`GET /api/sources` (قائمة المصادر والعلماء المعتمدين)، والتوثيق التفاعلي في `/docs`.

`POST /api/check` is open without a key for the demo and judging, limited to 20 requests per 10 minutes per IP to protect the sources we call (`app/main.py`). Also `GET /api/health`, `GET /api/sources` and interactive docs at `/docs`.

## 4. مفاتيح النشر · Deployment keys

| المفتاح · Key | الاستعمال · Use | أين يوضع · Where |
|---|---|---|
| `HF_TOKEN` | سير النشر اليدوي `.github/workflows/deploy-space.yml` فقط؛ النشر المعتاد بإعادة بناء الـ Space من هذا المستودع ولا يحتاجه · Manual deploy workflow only | GitHub ← Settings ← Secrets and variables ← Actions |
| `TATHABBUT_LLM_API_KEY` | الاتصال بخادم علّام · Calling the ALLaM endpoint | Hugging Face ← Space ← Settings ← Variables and secrets |

## 5. أدوات الذكاء الاصطناعي في بناء المشروع · AI tools used to build the project

الأداة نفسها لا تستدعي أي نموذج غير علّام، ولا تستدعي واجهة Claude البرمجية ولا تحمل مفتاحًا لها. أما أثناء التطوير فاستُعمل Claude من Anthropic عبر Claude Code بحساب الفريق: في الشيفرة والاختبارات، ومسودات حالات التقييم، والوثائق. والقائمة الكاملة ودور الفريق في سجل الأدوات والتراخيص [SOURCES_AND_LICENSES.md](../SOURCES_AND_LICENSES.md).

The running tool calls no model other than ALLaM; it never calls the Claude API and holds no Claude key. During development, Claude (Anthropic) was used through Claude Code on the team's account for code and tests, drafts of the evaluation cases, and documentation. The full list and the team's role are in the tools and licenses log, [SOURCES_AND_LICENSES.md](../SOURCES_AND_LICENSES.md).

## 6. كيف يتحقق المحكّم · How a judge can verify

```bash
grep -rnE "https?://" app/          # every outside address the server code uses
grep -rn "environ" app/config.py    # every setting and key comes from the environment
curl https://3rb-tathabbut.hf.space/api/health   # model_backend shows whether ALLaM is connected
```
