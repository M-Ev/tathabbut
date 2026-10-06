# ما طوّرناه وبرمجناه · What we built

طوّرنا تثبّت وبرمجناه في فريق «قيد الأوابد» خلال أيام البناء (4 إلى 6 أكتوبر 2026)، مستعينين بـ Claude Code في كتابة الكود تحت توجيهنا ومراجعتنا. لكل ميزة هنا: صورتها من الموقع، وما تفعله، والـcommit الذي بنيت فيه. التفاصيل في [CHANGELOG.md](../CHANGELOG.md)، وقرارات الفريق في [team.md](team.md).

الصور من 6 أكتوبر 2026، والنتائج فيها من الموقع المباشر https://3rb-tathabbut.hf.space.

---

## 1. الفحص · Checking a text

يلصق الزائر منشورًا أو درسًا أو إجابة مساعد ذكي، فتُستخرج آياته وأحاديثه وتُتتبع إلى مصادرها، ولكل استشهاد حالة دليل وسبب الحكم.

| الصفحة | التقرير: آية منقولة بخطأ، وحديث في الصحيحين، وحديث موضوع |
|---|---|
| ![الفحص](screenshots/features/01-check-home.png) | ![تقرير الفحص](screenshots/features/02-check-report.png) |

- الحديث الملصوق لحاله أو المسؤول عنه، ومن حكم عليه بماذا: `fd9f161` (5 أكتوبر)
- فهم الأسئلة بالعامية السعودية وبغير العربية، والعزو بلا أقواس: `433cf91`، `e72209a` (5 أكتوبر)

## 2. المشاركة صورةً ونصًا · Sharing as an image and text

كل ما ثبت يُشارك بطاقةً ونصًا مع رابط يفحصه، من حقول المصدر وحدها. والحديث الذي لا تؤيده المصادر يُشارك تصحيحًا بأحكام العلماء. `252dede` (6 أكتوبر)

| نافذة المشاركة | بطاقة تصحيح لحديث موضوع | بطاقة حديث في الصحيحين |
|---|---|---|
| ![المشاركة](screenshots/features/03-share-dialog.png) | ![بطاقة تصحيح](screenshots/features/04-share-card-correction.png) | ![بطاقة الصحيحين](screenshots/features/05-share-card-sahihayn.png) |

## 3. اسأل الثقات · Ask the trusted

سؤال عن حكم بأي صياغة، فيأتي الجواب جملةً من فتوى ابن باز أو ابن عثيمين بنصها، متحققًا منها حرفًا بحرف؛ وأقرب فتوى إن لم توجد في المسألة نفسها؛ وفحص إجابات المساعدات الذكية: تُعرض، أو بملاحظة، أو تُوقف.

![اسأل الثقات](screenshots/features/06-ask-the-trusted.png)

- فتاوى الشيخين بنصها: `2450397`، والجواب المنقول المتحقق منه: `e5f9de8`، `b388cb3`، وأقرب فتوى: `8aca70b`، والاسم: `fe54573` (5 أكتوبر)

## 4. الأرشيف · The public archive

استشهادات متداولة فحصتها الأداة، بأحكام العلماء بنصها وروابطها. `31f114f`، `3f7b9e4` (5 أكتوبر)

![الأرشيف](screenshots/features/07-archive.png)

## 5. الأذكار الموثّقة · Verified adhkar

كل ذكر فحصه تثبّت نفسه في الموسوعة الحديثية: لا يُعرض إلا على رواية فيها لفظه كاملًا بحكم مقبول من العلماء المعتمدين، وفي وقته إن ذكرته الرواية، وبعدده إن نصّت عليه. `5e67e78`، `0470f94`، `130e1fc` (5 أكتوبر)

| الصفحة الرئيسية | أذكار الصباح، بعدّاد اللمس | أدعية من القرآن |
|---|---|---|
| ![الأذكار](screenshots/features/11-adhkar-home.png) | ![أذكار الصباح](screenshots/features/12-adhkar-morning.png) | ![أدعية من القرآن](screenshots/features/13-adhkar-quran-duas.png) |

| ما لم يُعرض ولماذا | المصحف (تجريبي) | متابعة العبادات |
|---|---|---|
| ![لم تُعرض هنا](screenshots/features/14-adhkar-not-shown.png) | ![المصحف](screenshots/features/15-mushaf.png) | ![متابعة العبادات](screenshots/features/16-tracker.png) |

| أسماء الله الحسنى بآياتها | التسبيح | آية اليوم |
|---|---|---|
| ![أسماء الله الحسنى](screenshots/features/17-names-of-allah.png) | ![التسبيح](screenshots/features/18-tasbih.png) | ![آية اليوم](screenshots/features/19-ayah-of-day.png) |

## 6. أركان الإسلام · The pillars of Islam

الأركان الخمسة، والوضوء والصلاة خطوة خطوة برسوم متحركة، بكلام الشيخ ابن باز بنصه ورابطه، ولغير العرب. `0e4aa4d`، `fd8b813` (5 أكتوبر)

| الأركان الخمسة | الوضوء | مشغّل الصلاة |
|---|---|---|
| ![أركان الإسلام](screenshots/features/08-pillars.png) | ![الوضوء](screenshots/features/09-wudu.png) | ![مشغّل الصلاة](screenshots/features/10-prayer-player.png) |

## 7. إحدى عشرة لغة، والجوال · Eleven languages, and phones

الواجهة بإحدى عشرة لغة، ومعاني الآيات من الترجمات المعتمدة، والمصدر يبقى عربيًا. `d68d28c`، `ee4d161` (5 أكتوبر)

| English | Français | اردو | 中文 | الجوال | المشاركة على الجوال |
|---|---|---|---|---|---|
| ![English](screenshots/features/20-lang-en.png) | ![Français](screenshots/features/20-lang-fr.png) | ![اردو](screenshots/features/20-lang-ur.png) | ![中文](screenshots/features/20-lang-zh.png) | ![الجوال](screenshots/features/21-mobile-adhkar.png) | ![المشاركة](screenshots/features/22-mobile-share.png) |

## 8. للمطورين · For developers

- `POST /api/check`: الفحص كاملًا مع قرار المساعدات الذكية ([api.md](api.md)).
- خادم MCP في `/mcp` لوكلاء الذكاء الاصطناعي: `check_citations`، `get_ayah`، `list_sources` ([mcp.md](mcp.md)). `2500705` (4 أكتوبر)
- `GET /api/adhkar`، `/api/mushaf`، `/api/asma`، `/api/pillars`، `/api/archive`، `/api/health`.

## 9. تحت الغطاء · Under the hood

- النموذجان: علّام 7B داخل الحاوية، و`gpt-oss-120b` على Groq المجاني، لكل منهما مهام ضيقة محروسة: `93f428c`، `6570ca1`، `a6c409c` (4 و5 أكتوبر). القياس: [eval/model_live_report.md](../eval/model_live_report.md).
- إعادة التصميم بهوية التحدي: `dba8bb8` (5 أكتوبر).
- اختبار 25 زائرًا على الموقع المباشر: [eval/personas_report.md](../eval/personas_report.md).
- 122 اختبارًا آليًا (`pytest`)، وكل خطأ وجدناه صار اختبارًا.
