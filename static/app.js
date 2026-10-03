"use strict";

const T = {
  ar: {
    title: "تثبّت", tagline: "مدقق الاستشهادات الشرعية", mottoRef: "الحجرات ٦",
    inputLabel: "النص المراد فحصه", intro: "الصق منشورًا أو درسًا أو إجابة روبوت محادثة، وسنتتبع كل آية وحديث فيه إلى مصدره.",
    placeholder: "الصق النص هنا", tryLabel: "أمثلة:", sampleAr: "منشور عربي", sampleEn: "English post",
    deep: "استعن بالنموذج اللغوي علّام لاكتشاف ما فات الفحص الأساسي (أبطأ)", check: "تحقّق من الاستشهادات",
    checking: "نستخرج الاستشهادات، ثم نطابق الآيات مع المصحف، ونبحث عن الأحاديث في الدرر السنية…", checkingDeep: "نراجع المصادر… وقد يستغرق النموذج اللغوي دقيقة أو أكثر.",
    failed: "تعذّر الفحص الآن، حاول مرة أخرى.", reportTitle: "نتيجة الفحص",
    none: "لم نجد في النص آية أو حديثًا مستشهدًا به.",
    truncatedText: (a, b) => `النص أطول من حد الفحص، ففُحص أول ${a} حرف من ${b}.`,
    truncatedCits: (a, b) => `فُحص أول ${a} استشهادًا من ${b} وُجدت في النص. افحص الباقي في طلب آخر.`,
    dorarDown: "الموسوعة الحديثية غير متاحة الآن: الآيات تُفحص كالمعتاد، والأحاديث تُحال إلى المختص حتى تعود.",
    busy: "طلبات كثيرة من هذا الجهاز في دقائق قليلة. انتظر قليلًا ثم أعد المحاولة.",
    unsupported: "هذه اللغة غير مدعومة بعد، فلم يُفحص النص. يفحص تثبّت اليوم النصوص العربية والإنجليزية.",
    unsupportedPart: "وفي النص كلام بلغة غير مدعومة بعد، فلم يُفحص منه إلا الاستشهادات العربية والإنجليزية أعلاه.",
    summary: (s, n) => [`الاستشهادات <b>${n(s.total)}</b>`, s.documented && `مطابق للمصحف <b>${n(s.documented)}</b>`, s.supported && `تؤيده المصادر <b>${n(s.supported)}</b>`, s.not_supported && `لا تؤيده المصادر المعتمدة <b>${n(s.not_supported)}</b>`, s.verify && `يحتاج مزيدًا من التحقق <b>${n(s.verify)}</b>`, s.refer && `يُحال إلى مختص <b>${n(s.refer)}</b>`].filter(Boolean).join(" · "),
    howTitle: "منهج الأداة",
    m1t: "القرآن", m1: "يُطابق النص مع مصحف مجمع الملك فهد، ويُنبَّه على ما اختلف عن لفظ المصحف أو عن موضع الآية، مع إظهار النص الصحيح والسورة والآية. نص القرآن لا يُولَّد أبدًا.",
    m2t: "الحديث", m2: "يُبحث عنه في الموسوعة الحديثية للدرر السنية، وتُنقل أحكام أئمة الحديث ثم أحكام المحققين المعاصرين بنصها، مع اسم قائل كل حكم، دون ترجيح بينها.",
    m3t: "إذا لم نجد مصدرًا", m3: "يقال ذلك صراحة ويُحال إلى المختص، وأسئلة الفتوى الشخصية تُحال إلى جهة الإفتاء.",
    m4t: "النموذج اللغوي", m4: "يستخرج ويطابق فقط، ولا يحكم على حديث ولا يفتي. وكل ما يقترحه يجب أن يرد بلفظه في النص المفحوص، وإلا حُذف.",
    privacy: "لا نحفظ نصك، ولا يُرسل إلى الدرر السنية إلا لفظ الحديث المستخرج. وعند الاستعانة بعلّام يُرسل النص إلى النموذج على خادم الفريق.",
    disclosure: "تثبّت أداة آلية مدعومة بالذكاء الاصطناعي، وليست عالمًا ولا مفتيًا.",
    apiLink: "الواجهة البرمجية لفحص إجابات روبوتات المحادثة",
    footer: "فريق قيد الأوابد · تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي",
    quran: "آية", hadith: "حديث", asQuoted: "ورد في النص", byModel: "اكتشفه النموذج اللغوي",
    v: {
      verified: "الآية منقولة بلفظ المصحف",
      verifiedBadRef: "الآية منقولة بلفظ المصحف، والعزو المكتوب يحتاج إلى تصحيح",
      badRefToo: "، والعزو المكتوب يحتاج إلى تصحيح",
      differs: (n) => `لفظ الآية يختلف عن المصحف في ${arPlaces(n)}`,
      differsEn: "الترجمة قريبة من هذه الآية، وليست بلفظ إحدى الترجمتين المعتمدتين في الأداة",
      not_in_mushaf: "لم نجد هذا النص في المصحف",
      too_short: "النص أقصر من أن نتحقق منه آليًا",
      not_in_translation: "لم نجد آية تقابل هذه الترجمة",
      graded: "وُجد في كتب الحديث، وهذه أحكام علماء الحديث المعتمدين عليه",
      gradedFab: "وُجد في كتب الحديث، ومن علماء الحديث المعتمدين من حكم عليه بالوضع أو البطلان أو بأنه لا أصل له",
      found_similar: "وُجدت روايات بلفظ مقارب، لا بلفظه",
      not_found: "لم نجد حكمًا لأحد علماء الحديث المعتمدين على هذا النص",
      needs_model: "النص مترجم، والبحث عن أصله العربي يحتاج إلى النموذج اللغوي",
      source_error: "تعذّر الوصول إلى الموسوعة الحديثية الآن",
      source_offline: "البحث في الموسوعة الحديثية غير مفعّل",
      error: "حدث خطأ أثناء الفحص",
    },
    surah: "سورة", ayahWord: "الآية", ayatWord: "الآيات",
    fixesHead: ["ورد في النص", "في المصحف"], missing: "(سقط من النص)", extra: "(ليس في المصحف)",
    translationLbl: "ترجمة معاني القرآن الكريم (الهلالي ومحسن خان، مجمع الملك فهد ١٤١٧هـ، عن موقع QuranEnc.com، الإصدار ١٫١٫٢)", trName: { hilali: "الهلالي ومحسن خان (مجمع الملك فهد)", saheeh: "صحيح إنترناشونال" },
    ayahLink: "الآية في موسوعة قرآنبيديا", trLink: "الترجمة الإنجليزية وحواشيها",
    occurrences: (n) => `تتكرر هذه العبارة في ${arPlaces(n)} من المصحف، وهذا أحدها.`,
    wrongRef: (given, where) => `العزو المكتوب ${given} يحتاج إلى تصحيح، والصواب: ${where}.`,
    rightRef: (given) => `العزو المكتوب ${given} صحيح.`,
    notes: {
      hadith_is_quran: "هذا النص آية من القرآن، وقد نُسب في النص إلى النبي ﷺ.",
      quran_claim_found_in_hadith: "نُسب هذا النص إلى القرآن، ووجدناه في كتب الحديث:",
      match_by_model: "المطابقة بين الترجمة والأصل العربي اقترحها النموذج اللغوي، فراجع النص العربي بنفسك.",
      wording_differs: "الأَولى نقل الحديث بلفظه كما في المصدر.",
    },
    fabBy: (names) => `حكم عليه بالوضع أو البطلان أو بأنه لا أصل له: ${names}. فلا يُذكر إلا مع بيان حكمه.`,
    ijtihad: "اختلفت أحكام علماء الحديث المعتمدين، وكلها اجتهاد يُعرض كما هو دون ترجيح.",
    gradeCols: ["العالِم", "الحكم بنصه", "المصادر"], died: (y) => `ت ${y}هـ`,
    sourceText: "نص الحديث في المصدر", rawi: "الراوي", openDorar: "في الدرر السنية",
    bookName: { bukhari: "صحيح البخاري", muslim: "صحيح مسلم" },
    longerText: (n) => `هذا الحكم على رواية أطول (${n} كلمة) ورد فيها اللفظ المنقول، لا على اللفظ المنقول وحده، فلا تُبنى عليه حالة الدليل.`,
    partialText: (w) => `في النص المنقول ما لم نجده في هذه الرواية: «${w}». فالحكم على لفظ مقارب، لا على النص المنقول.`,
    narrator: (n) => `أُخفي ${n} من أقوال علماء الحديث المعتمدين لأنها حكم على راوٍ لا على الحديث.`,
    onlyApproved: "تُعرض أحكام علماء الحديث المعتمدين في الأداة فقط.",
    sahihayn: (list) => `ورد بهذا اللفظ أو بلفظ قريب منه في ${list}، بحسب نتائج الدرر السنية.`, and: " و",
    brackets: "ما بين المعقوفين [ ] من صياغة الدرر السنية لا من لفظ المحدّث: تضعه حين تختصر كلامه أو تعبّر عن معناه، أو حين يُفهم الحكم من كلامه دون تصريح، أو حين يُبنى على شرطٍ نصّ عليه المحدّث في مقدمة كتابه. وما خارج المعقوفين فهو لفظه.", bracketsLink: "تنبيهات الدرر السنية العلمية", searchDorar: "ابحث بنفسك في الدرر السنية",
    matchedArabic: "الأصل العربي الذي طابقه النموذج",
    leveld: "يبدو أن في النص سؤالًا عن حالة شخصية، وتثبّت لا يفتي. فيُرجى البحث عن المسألة في فتاوى العالمين الجليلين:",
    leveldFound: "يبدو أن في النص سؤالًا عن حالة شخصية، وتثبّت لا يفتي. هذه فتاوى منشورة للعالمين الجليلين في مسائل قريبة من السؤال، منقولة بنصها من موقعيهما. اختيرت بتقارب الألفاظ بين السؤال وعناوين الفتاوى، ولم يكتبها النموذج اللغوي ولم يخترها، فتأكد أنها تطابق حالتك.",
    leveldBody: (b) => `فإن لم يوجد فيها ما يستوفي الحالة، فيُرجى سؤال ${b}.`,
    bodyLink: "موقع الرئاسة العامة للبحوث العلمية والإفتاء",
    fatwasOf: (n) => `فتاوى ${n}`, fq: "السؤال", fopen: "أول الجواب بنصه", fsource: "المصدر",
    ffull: "اعرض الفتوى كاملة", ffullSite: "اعرض الفتوى كاملة في موقع المؤسسة", flink: "رابط الفتوى في الموقع",
    fnone: "لم نجد في فتاواه المنشورة ما يقارب ألفاظ السؤال.", ferror: "تعذّر الوصول إلى موقعه الآن.", fsearch: "ابحث بنفسك في موقعه",
    why: "سبب هذه النتيجة",
    tier: { documented: "مطابق للمصحف", supported: "تؤيده المصادر", not_supported: "لا تؤيده المصادر المعتمدة", verify: "يحتاج مزيدًا من التحقق", refer: "يُحال إلى مختص" },
    rulesDraft: "قواعد حالة الدليل مسودة من الفريق، تنتظر توقيع المراجِعة الشرعية.", rulesSigned: (who, d) => `قواعد حالة الدليل راجعتها ووقّعتها ${who} في ${d}.`,
    tierLbl: "حالة الدليل",
    report: "أبلغ عن خطأ في هذه النتيجة", reportNote: "يُنشر البلاغ علنًا في GitHub ومعه النص المقتبس.",
    r: {
      compared: "قارنّا كلمات النص بنص المصحف حرفًا حرفًا، دون اعتبار للتشكيل ولا لفروق الرسم العثماني والإملائي.",
      foundAt: (p) => `فوجدناه مطابقًا لـ${p}.`,
      enMatched: (pct, p, tr) => `طابقنا النص مع ترجمة ${tr} لمعاني القرآن (تقارب ${pct})، وأقرب آية له ${p}، ثم عرضناها بلفظ المصحف.`,
      nearest: (p, pct) => `أقرب موضع له في المصحف ${p}، وتقارب اللفظ ${pct}.`,
      changed: (a, b) => `كُتب «${a}»، والذي في المصحف «${b}».`,
      missing: (b) => `سقط من النص «${b}».`,
      extra: (a) => `زيد في النص «${a}»، وليس في الآية.`,
      copyRule: "نص القرآن يُنقل بلفظه كما في المصحف، والأسلم نسخه من مصدر موثوق.",
      alefChanged: (a, b) => `في «${a}» ألف ليست في رسم المصحف «${b}»، فهي لفظ آخر.`,
      riwaya: "قارنّا بمصحف مجمع الملك فهد برواية حفص عن عاصم. فإن كان النقل على قراءة متواترة أخرى فليس خطأً، ويُراجَع فيه مختص في القراءات.",
      enDiffers: (pct, p) => `الترجمة المنقولة لا تطابق حرفيًا أيًّا من الترجمتين اللتين نقارن بهما (تقارب ${pct})، وأقرب آية لمعناها ${p}. ترجمات المعاني تختلف، فالمرجع هو الأصل العربي.`,
      notInMushaf: (n) => `بحثنا في آيات المصحف كلها (${n} آية)، فلم نجد نصًا يطابقه أو يقاربه.`,
      notInTranslation: (n) => `قارنّا النص بترجمة معاني آيات المصحف كلها (${n} آية)، فلم نجد ما يقاربه. والمقارنة بالترجمة لا تكفي للحكم بأنه ليس آية، ولذلك نحيله إلى المختص.`,
      attributed: (m) => `وقد نُسب في النص إلى القرآن بعبارة «${m}».`,
      refWritten: (g) => `ذُكر في النص العزو ${g}.`,
      refHolds: (p) => `والذي في ${p}:`,
      refNoAyah: (name, n) => `وسورة ${name} عدد آياتها ${n}، فلا توجد آية بهذا الرقم.`,
      refActual: (p) => `أما النص المنقول فموضعه ${p}.`,
      refRight: (g) => `العزو المكتوب ${g} يطابق موضع النص.`,
      searched: (q) => `بحثنا عن «${q}» في الموسوعة الحديثية للدرر السنية، مقصورًا على علماء الحديث المعتمدين في الأداة.`,
      foundN: (n, pct) => `عدد أحكامهم التي وجدناها على روايات هذا الحديث: ${n}، وأقرب الروايات لفظًا إلى النص بنسبة ${pct}.`,
      notWord: "اللفظ المنقول لا يطابق ألفاظ الروايات تمامًا.",
      attrOk: (w, b) => `كُتب في النص «${w}»، ووافق ذلك نتائج البحث: ورد في ${b}.`,
      attrMissing: (w, b) => `كُتب في النص «${w}»، ولم نجده في ${b} ضمن نتائج البحث في الموسوعة الحديثية.`,
      attrUnchecked: (w) => `كُتب في النص «${w}»، ولم نتمكن من مقارنته بالمصدر الآن.`,
      firmForm: "نُسب في النص بصيغة الجزم، وأحكام العلماء المعتمدين على لفظه لا تؤيده. وما لم يثبت يُذكر بصيغة «رُوي» مع بيان حكمه.",
      longerOnly: "وجدنا اللفظ المنقول داخل روايات أطول، وأحكامها على الرواية كلها، فلا نبني عليها حالة الدليل.",
      quoteOnly: "الأحكام منقولة بنصها من مصادرها، والأداة لا تعلّل حكمًا ولا ترجّح بين الأحكام؛ فتعليلها في كتب علماء الحديث المعتمدين.",
      noneFound: "فلم نجد لأحدهم حكمًا على نص يقارب هذا.",
      notMeaning: "وعدم وجوده هنا ليس حكمًا عليه، ولذلك نحيله إلى المختص.",
      modelWords: (w) => `استعان النموذج اللغوي علّام بكلمات عربية للبحث: «${w}»، ثم اختار الأصل الأقرب لمعنى الترجمة.`,
      isQuran: "وجدنا هذا النص بلفظه في المصحف، فهو آية لا حديث.",
      needsModel: "النص بغير العربية، والبحث في الموسوعة الحديثية يكون باللفظ العربي، والنموذج اللغوي غير مفعّل الآن.",
    },
    credit: "يعمل بنموذج علّام من سدايا، ومصادره من الحزمة العلمية للتحدي.",
  },
  en: {
    title: "Tathabbut", tagline: "Islamic citation checker", mottoRef: "al-Hujurat 49:6 · “verify it” (King Fahd Complex translation)",
    inputLabel: "Text to check", intro: "Paste a post, a lecture or a chatbot answer, and we will trace every Quran verse and hadith in it to its source.",
    placeholder: "Paste your text here", tryLabel: "Examples:", sampleAr: "Arabic post", sampleEn: "English post",
    deep: "Use the ALLaM language model to find what the basic check missed (slower)", check: "Check citations",
    checking: "Extracting citations, matching verses with the Mushaf and searching hadith on Dorar…", checkingDeep: "Checking the sources… the language model may take a minute or more.",
    failed: "The check failed. Please try again.", reportTitle: "Result",
    none: "No Quran verse or hadith citation was found in the text.",
    truncatedText: (a, b) => `The text is longer than the check limit; the first ${a} of ${b} characters were checked.`,
    truncatedCits: (a, b) => `The first ${a} of ${b} citations found were checked. Check the rest in another request.`,
    dorarDown: "The hadith encyclopedia cannot be reached right now: verses are checked as usual, and hadith are referred to a specialist until it is back.",
    busy: "Too many requests from this device in a few minutes. Please wait a little and try again.",
    unsupported: "This language is not supported yet, so the text was not checked. Tathabbut checks Arabic and English today.",
    unsupportedPart: "Part of the text is in a language not supported yet; only the Arabic and English citations above were checked.",
    summary: (s, n) => [`Citations <b>${n(s.total)}</b>`, s.documented && `matches the Mushaf <b>${n(s.documented)}</b>`, s.supported && `supported by the sources <b>${n(s.supported)}</b>`, s.not_supported && `not supported by the approved sources <b>${n(s.not_supported)}</b>`, s.verify && `needs more verification <b>${n(s.verify)}</b>`, s.refer && `refer to a specialist <b>${n(s.refer)}</b>`].filter(Boolean).join(" · "),
    howTitle: "Method",
    m1t: "Quran", m1: "Matched against the King Fahd Complex Mushaf; any word or reference that differs is pointed out, with the correct text, surah and ayah shown. Quran text is never generated.",
    m2t: "Hadith", m2: "Looked up in the Dorar hadith encyclopedia. Gradings by the classical imams of hadith, then by modern hadith editors, are quoted verbatim, each with the name of the scholar who gave it, with no preference between them.",
    m3t: "When no source is found", m3: "The tool says so plainly and refers you to a specialist; personal fatwa questions go to a fatwa authority.",
    m4t: "Language model", m4: "Only extracts and matches; it never grades a hadith or gives a fatwa. Anything it suggests must appear verbatim in the checked text, or it is dropped.",
    privacy: "Your text is not stored. Only the extracted hadith wording is sent to Dorar. When ALLaM is used, the text is sent to the model on the team's server.",
    disclosure: "Tathabbut is an AI-assisted tool, not a scholar or a mufti.",
    apiLink: "API for checking chatbot answers",
    footer: "Team Qayd al-Awabid · AI Challenge in Serving Islamic Content",
    quran: "Quran", hadith: "Hadith", asQuoted: "As quoted", byModel: "found by the language model",
    v: {
      verified: "Quoted exactly as in the Mushaf",
      verifiedBadRef: "Quoted exactly as in the Mushaf; the reference needs correcting",
      badRefToo: "; the reference also needs correcting",
      differs: (n) => n === 1 ? "The wording differs from the Mushaf in one place" : `The wording differs from the Mushaf in ${n} places`,
      differsEn: "Close to this verse, but not in the wording of either approved translation",
      not_in_mushaf: "We did not find this text in the Mushaf",
      too_short: "The text is too short to check automatically",
      not_in_translation: "We could not match this to any verse",
      graded: "Found in hadith sources, with these gradings by the approved hadith scholars",
      gradedFab: "Found in hadith sources; some of the approved hadith scholars graded it fabricated, false or baseless",
      found_similar: "Narrations with similar, not identical, wording were found",
      not_found: "No grading by the approved hadith scholars was found",
      needs_model: "This is a translation; finding its Arabic source needs the language model",
      source_error: "The hadith encyclopedia could not be reached",
      source_offline: "Hadith encyclopedia lookup is turned off",
      error: "An error occurred during the check",
    },
    surah: "Surah", ayahWord: "ayah", ayatWord: "ayat",
    fixesHead: ["As quoted", "In the Mushaf"], missing: "(left out)", extra: "(not in the Mushaf)",
    translationLbl: "Translation of the meanings (al-Hilali & Muhsin Khan, King Fahd Complex 1417 AH; via QuranEnc.com v1.1.2)", trName: { hilali: "al-Hilali & Muhsin Khan (King Fahd Complex)", saheeh: "Saheeh International" },
    ayahLink: "This verse on Quranpedia", trLink: "Full translation with the translators' notes",
    occurrences: (n) => `This phrase occurs in ${n} places in the Mushaf; this is one of them.`,
    wrongRef: (given, where) => `The reference ${given} needs correcting; it should be ${where}.`,
    rightRef: (given) => `The reference ${given} is correct.`,
    notes: {
      hadith_is_quran: "This text is a Quran verse, but it was attributed to the Prophet ﷺ.",
      quran_claim_found_in_hadith: "This was attributed to the Quran; it was found in hadith sources:",
      match_by_model: "The language model matched the translation to the Arabic source. Please verify the Arabic text, or ask someone who reads Arabic.",
      wording_differs: "It is best to quote the hadith in the wording of its source.",
    },
    fabBy: (names) => `Graded fabricated, false or baseless by: ${names}. It should be mentioned only together with its grading.`,
    ijtihad: "The approved hadith scholars' gradings differ; each is scholarly ijtihad (reasoned judgment), shown as it is with no preference.",
    gradeCols: ["Scholar", "Grading (verbatim Arabic)", "Sources"], died: (y) => `d. ${y} AH`,
    sourceText: "Hadith text in the source", rawi: "Narrator", openDorar: "on Dorar",
    bookName: { bukhari: "Sahih al-Bukhari", muslim: "Sahih Muslim" },
    longerText: (n) => `This grading is of a longer narration (${n} words) that contains the quoted words, not of the quoted words alone, so it does not decide the evidence status.`,
    partialText: (w) => `The quote has words not found in this narration: «${w}». The grading is of a similar wording, not of the quoted text.`,
    narrator: (n) => `${n} statement(s) by the approved hadith scholars are not shown, as they assess a narrator, not this hadith.`,
    onlyApproved: "Only gradings by the tool's approved hadith scholars are shown.",
    sahihayn: (list) => `This wording, or one very close to it, is in ${list}, according to Dorar's results.`, and: " and ",
    jamhara: "Jamhara (Islamic Content Vocabulary):",
    jamharaAr: "Arabic entry only",
    noGloss: "No English entry in Jamhara (Islamic Content Vocabulary); please ask a specialist about the Arabic wording.",
    chainOnly: "This grading is about the chain of narration only.",
    category: { authentic: "Group: accepted (authentic)", good: "Group: accepted (good)", weak: "Group: weak", very_weak: "Group: very weak", fabricated: "Group: fabricated or baseless", narrators: "Group: about its narrators", mixed: "More than one judgment: read the Arabic as a whole" },
    glossNote: "Each grading is in Arabic exactly as the scholar wrote it. The English term beside it is the English headword in Jamhara, Islamic Content Vocabulary (islamic-content.com/dictionary), the term reference named in the challenge's scientific package; the group is Tathabbut's grouping for colour. Neither is a new grading.",
    brackets: "Text in square brackets [ ] is Dorar's wording, not the scholar's: Dorar uses it when it shortens or rephrases his statement, when the grading is understood from his words rather than stated outright, or when it follows from a condition he set in the introduction of his book. Words outside the brackets are his.", bracketsLink: "Dorar's scientific notes", searchDorar: "Search Dorar yourself",
    matchedArabic: "Arabic source matched by the model",
    leveld: "The text seems to include a personal fatwa question, and Tathabbut does not issue fatwas. Look for the question in the published fatwas of these two scholars:",
    leveldFound: "The text seems to include a personal fatwa question, and Tathabbut does not issue fatwas. Below are published fatwas of the two scholars on close questions, quoted in Arabic exactly as on their sites. They were chosen by word overlap between the question and the fatwa titles; the language model neither wrote nor chose them, so check that they match your case.",
    leveldBody: (b) => `If they do not cover the case, ask ${b}.`,
    bodyLink: "General Presidency of Scholarly Research and Ifta (official site)",
    fatwasOf: (n) => `Fatwas of ${n}`, fq: "Question", fopen: "Opening of the answer, verbatim", fsource: "Source",
    ffull: "Show the full fatwa", ffullSite: "Read the full fatwa on the foundation's site", flink: "Fatwa page on the site",
    fnone: "None of his published fatwas is close to the question's wording.", ferror: "His site could not be reached right now.", fsearch: "Search his site yourself",
    why: "Why this result",
    tier: { documented: "Matches the Mushaf", supported: "Supported by the sources", not_supported: "Not supported by the approved sources", verify: "Needs more verification", refer: "Refer to a specialist" },
    rulesDraft: "The evidence-status rules are the team's draft, awaiting the Sharia reviewer's signature.", rulesSigned: (who, d) => `The evidence-status rules were reviewed and signed by ${who} on ${d}.`,
    tierLbl: "Evidence status",
    report: "Report a problem with this result", reportNote: "Reports are public GitHub issues and include the quoted text.",
    r: {
      compared: "We compared the text with the Mushaf letter by letter, ignoring diacritics and Uthmani versus standard spelling.",
      foundAt: (p) => `It matches ${p}.`,
      enMatched: (pct, p, tr) => `We matched the text with the ${tr} translation of the meanings (${pct} close); the nearest verse is ${p}, shown here in the Mushaf's wording.`,
      nearest: (p, pct) => `The nearest place in the Mushaf is ${p}, ${pct} close in wording.`,
      changed: (a, b) => `Written «${a}»; the Mushaf has «${b}».`,
      missing: (b) => `«${b}» is missing from the text.`,
      extra: (a) => `«${a}» was added; it is not in the verse.`,
      copyRule: "Quran text must be quoted exactly as in the Mushaf; it is safest to copy it from a reliable source.",
      alefChanged: (a, b) => `«${a}» has an alef that the Mushaf's «${b}» does not have, so it is a different word.`,
      riwaya: "We compared with the King Fahd Complex Mushaf in the narration of Hafs from Asim. If the quote follows another mutawatir reading, it is not an error; a specialist in the readings can confirm.",
      enDiffers: (pct, p) => `The quoted translation does not match the approved translations word for word (${pct} close); the nearest verse in meaning is ${p}. Translations of the meanings vary; the Arabic is the reference.`,
      notInMushaf: (n) => `We searched all ${n} verses of the Mushaf and found nothing matching or close to it.`,
      notInTranslation: (n) => `We compared the text with a translation of the meanings of all ${n} verses and found nothing close. A translation comparison is not enough to say it is not a verse, which is why it is referred to a specialist.`,
      attributed: (m) => `The text attributed it to the Quran with «${m}».`,
      refWritten: (g) => `The text gives the reference ${g}.`,
      refHolds: (p) => `What is at ${p}:`,
      refNoAyah: (name, n) => `Surah ${name} has ${n} verses, so there is no verse with that number.`,
      refActual: (p) => `The quoted text is at ${p}.`,
      refRight: (g) => `The reference ${g} matches where the text is.`,
      searched: (q) => `We searched for «${q}» in the Dorar hadith encyclopedia, limited to the tool's approved hadith scholars.`,
      foundN: (n, pct) => `We found ${n} of their gradings on narrations of this hadith; the closest wording is ${pct} close to the text.`,
      notWord: "The quoted wording does not exactly match the narrations.",
      attrOk: (w, b) => `The text says «${w}», and the search agrees: it is in ${b}.`,
      attrMissing: (w, b) => `The text says «${w}», but we did not find it in ${b} among the hadith encyclopedia's search results.`,
      attrUnchecked: (w) => `The text says «${w}»; we could not compare this with the source right now.`,
      firmForm: "The text attributes it firmly («the Prophet ﷺ said»), while the approved scholars' gradings of this wording do not support it. What is not established is cited with «it is narrated» together with its grading.",
      longerOnly: "The quoted words were found inside longer narrations; their gradings are of the whole narration, so the evidence status is not based on them.",
      quoteOnly: "Gradings are quoted verbatim from their sources. The tool neither explains nor weighs them; the reasons are in the scholars' own books.",
      noneFound: "None of them has a grading on a text close to this one.",
      notMeaning: "Not finding it here is not a judgment on it, which is why it is referred to a specialist.",
      modelWords: (w) => `The ALLaM model suggested Arabic search words «${w}», then picked the source closest in meaning to the translation.`,
      isQuran: "This exact text is in the Mushaf, so it is a verse, not a hadith.",
      needsModel: "The text is not in Arabic; the hadith encyclopedia is searched in Arabic and the language model is off right now.",
    },
    credit: "Powered by SDAIA's ALLaM model; sources from the challenge's scientific package.",
  },
};

const SAMPLES = {
  ar: "أيها الإخوة، يقول الله تعالى: ﴿يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا جَاءَكُمْ فَاسِقٌ بِخَبَرٍ فَتَبَيَّنُوا﴾ (البقرة: 6).\nوقال رسول الله ﷺ: «إنما الأعمال بالنيات».\nوفي الحديث: «اطلبوا العلم ولو في الصين».\nومن يتق الله يجعل له مخرجا ويرزقه من حيث لا يحتسب، فلا تيأسوا.\nوقال تعالى: «النظافة من الإيمان».",
  en: "The Prophet (ﷺ) said: \"Actions are judged by intentions.\"\nAllah says in the Quran: \"Indeed, with hardship comes ease\" (94:6).\nThe Prophet (pbuh) said: \"Seek knowledge even if you have to go to China.\"",
};

const REPO = "https://github.com/M-Ev/tathabbut";
let lang = "ar";
let lastResult = null;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const t = () => T[lang];
const num = (n) => (lang === "ar" ? Number(n).toLocaleString("ar-EG") : String(n));
const localDigits = (s) => (lang === "ar" ? String(s ?? "").replace(/[0-9]/g, (d) => "٠١٢٣٤٥٦٧٨٩"[d]) : String(s ?? ""));
const arDigits = (n) => Number(n).toLocaleString("ar-EG", { useGrouping: false });
// Arabic count of «موضع»: موضع واحد، موضعين، ٣–١٠ مواضع، ١١ موضعًا فأكثر.
const arPlaces = (n) => (n === 1 ? "موضع واحد" : n === 2 ? "موضعين" : `${arDigits(n)} ${n <= 10 ? "مواضع" : "موضعًا"}`);
const updateCounter = () => { $("counter").textContent = localDigits(`${$("text").value.length} / 8000`); };

function applyLang() {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t()[el.dataset.i18n]; });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.placeholder = t()[el.dataset.i18nPh]; });
  $("lang").textContent = lang === "ar" ? "English" : "العربية";
  updateCounter();
  document.title = lang === "ar" ? "تثبّت · مدقق الاستشهادات الشرعية" : "Tathabbut · Islamic citation checker";
  if (lastResult) render(lastResult);
  showBanner();
}

function place(q) {
  const name = lang === "ar" ? q.surah_name_ar : q.surah_name_en;
  const a = q.ayah_from === q.ayah_to ? num(q.ayah_from) : `${num(q.ayah_from)}–${num(q.ayah_to)}`;
  const word = q.ayah_from === q.ayah_to ? t().ayahWord : t().ayatWord;
  return `${t().surah} ${name}، ${word} ${a}`.replace("، ", lang === "ar" ? "، " : ", ");
}

function verdictFor(c) {
  const v = t().v;
  const q = c.quran || {};
  const hd = c.hadith || {};
  if (c.type === "quran") {
    if (c.status === "verified") return [q.reference_ok === false ? v.verifiedBadRef : v.verified, q.reference_ok === false ? "warn" : "ok"];
    if (c.status === "differs") {
      if (q.via !== "arabic") return [v.differsEn, "warn"];
      const n = (q.diff || []).filter((d) => d.op !== "equal").length || 1;
      return [v.differs(n) + (q.reference_ok === false ? v.badRefToo : ""), "warn"];  // gentle: attention, not alarm
    }
    if (c.status === "too_short") return [v.too_short, "warn"];
    if (c.status === "not_in_mushaf") return c.lang === "ar" ? [v.not_in_mushaf, "warn"] : [v.not_in_translation, "warn"];
  }
  if (c.status === "graded" && hd.fabricated_by && hd.fabricated_by.length) return [v.gradedFab, "bad"];
  const cls = { graded: "ok", found_similar: "warn", not_found: "warn", needs_model: "warn", source_error: "warn", error: "bad" }[c.status] || "";
  return [v[c.status] || c.status, cls];
}

// U+065E (open fatha tanween in this Mushaf encoding) shows as a box in many fonts; U+08F1 is the same mark
// and renders (plan item 9). Display only: matching always uses the data as published.
const glyphs = (x) => (x || "").replace(/\u065E/g, "\u08F1");

function markWords(text, words) {
  let html = esc(text);
  for (const w of words) {
    const e = esc(w);
    if (e && html.includes(e)) html = html.replace(e, `<mark>${e}</mark>`);
  }
  return html;
}

function renderMushaf(q, c) {
  const changed = (q.diff || []).filter((d) => d.op !== "equal");
  const marked = changed.flatMap((d) => (d.mushaf ? d.mushaf.split(" ") : []));
  const ayat = (q.ayat && q.ayat.length ? q.ayat : [{ ayah: q.ayah_from, text: q.mushaf_text }])
    .map((a) => `${markWords(glyphs(a.text), marked.map(glyphs))}<span class="ayah-end">۝${arDigits(a.ayah)}</span>`).join(" ");
  let h = `<div class="mushaf"><div class="mushaf-inner">
    <div class="mushaf-head">${esc(place(q))}</div>
    <p class="ayat">${ayat}</p>`;
  if (lang === "en" || c.lang === "en") h += `<p class="translation"><span class="lbl">${esc(t().translationLbl)}</span>${esc(q.translation_en)}</p>`;
  h += `</div></div>`;
  if (changed.length) {
    h += `<table class="fixes"><thead><tr><th>${esc(t().fixesHead[0])}</th><th>${esc(t().fixesHead[1])}</th></tr></thead><tbody>`;
    for (const d of changed) {
      h += `<tr><td class="was">${esc(d.quoted || t().missing)}</td><td class="is">${esc(glyphs(d.mushaf) || t().extra)}</td></tr>`;
    }
    h += `</tbody></table>`;
  }
  if (q.occurrences > 1) h += `<p class="line note">${esc(t().occurrences(q.occurrences))}</p>`;
  h += `<p class="after"><a href="${esc(q.url)}" target="_blank" rel="noopener">${esc(t().ayahLink)}</a>`;
  if (lang === "en" || c.lang === "en") h += ` · <a href="${esc(q.translation_url)}" target="_blank" rel="noopener">${esc(t().trLink)}</a>`;
  h += `</p>`;
  return h;
}

// One row per scholar and wording: the same grading from the same scholar in several books is one judgment.
function groupRows(items) {
  const rows = [];
  for (const i of items) {
    const key = i.scholar_key + "|" + i.grade.trim() + "|" + (i.match || "same");
    const row = rows.find((r) => r.key === key);
    if (row) row.sources.push(i);
    else rows.push({ key, first: i, sources: [i] });
  }
  return rows;
}

function sourceLine(i) {
  const no = esc(localDigits(i.number));
  const link = i.url ? ` · <a href="${esc(i.url)}" target="_blank" rel="noopener">${esc(t().openDorar)}</a>` : "";
  if (lang === "ar") return `<li>${esc(i.book)}، ${no}${link}</li>`;
  const title = i.book_en ? esc(i.book_en) : `<bdi lang="ar" dir="rtl">${esc(i.book)}</bdi>`;
  const arTitle = i.book_en ? `<bdi class="ar-inline" lang="ar" dir="rtl">${esc(i.book)}</bdi>` : "";
  return `<li>${title}, no. ${no}${link}${arTitle}</li>`;
}

// English help for a grading: the Jamhara dictionary's own English headword with a link, never our own wording.
function glossLine(gl) {
  const link = (u, text) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(text)}</a>`;
  const terms = gl.terms || [];
  let h = "";
  if (gl.category && t().category[gl.category]) h += `<span class="gloss cat">${esc(t().category[gl.category])}</span>`;
  // One line per term: its transliteration, then Jamhara's English headword (or its Arabic entry) with the link.
  for (const x of terms) {
    const tr = `<i class="tr">${esc(x.tr)}</i> · `;
    if (x.en) h += `<span class="gloss">${tr}${esc(t().jamhara)} ${link(x.url, x.en)}</span>`;
    else if (x.url) h += `<span class="gloss">${tr}${esc(t().jamhara)} ${link(x.url, t().jamharaAr)}</span>`;
    else h += `<span class="gloss">${tr}${esc(t().noGloss)}</span>`;
  }
  if (!terms.length && gl.category !== "mixed") h += `<span class="gloss">${esc(t().noGloss)}</span>`;
  if (gl.chain_only) h += `<span class="gloss">${esc(t().chainOnly)}</span>`;
  return h;
}

function renderGradings(hd) {
  if (!hd) return "";
  let h = "";
  const fab = lang === "en" && hd.fabricated_by_en ? hd.fabricated_by_en : hd.fabricated_by;
  if (fab && fab.length) h += `<p class="line bad">${esc(t().fabBy(fab.join(lang === "ar" ? "، " : ", ")))}</p>`;
  if (hd.sahihayn && hd.sahihayn.length) {
    const list = hd.sahihayn.map((x) => {
      const name = lang === "ar" ? `${esc(x.book)} (${esc(localDigits(x.number))})` : `${esc(x.book_en || x.book)} (no. ${esc(x.number)})`;
      return x.url ? `<a href="${esc(x.url)}" target="_blank" rel="noopener">${name}</a>` : name;
    }).join(t().and);
    h += `<p class="line ok">${t().sahihayn(list)}</p>`;
  }
  const groups = hd.groups || [];
  const all = groups.flatMap((g) => g.items);
  // Disagreement is about this wording only; a longer narration or a near wording is another text.
  const cats = new Set(all.filter((i) => !i.match || i.match === "same").map((i) => (i.grade_gloss || {}).category).filter((c) => c && c !== "narrators"));
  if (cats.size > 1) h += `<p class="line note">${esc(t().ijtihad)}</p>`;
  for (const g of groups) {
    h += `<table class="grades"><caption>${esc(lang === "ar" ? g.label_ar : g.label_en)}</caption>
      <thead><tr><th>${esc(t().gradeCols[0])}</th><th>${esc(t().gradeCols[1])}</th><th>${esc(t().gradeCols[2])}</th></tr></thead><tbody>`;
    for (const row of groupRows(g.items)) {
      const i = row.first;
      const gl = i.grade_gloss || {};
      let meaning = lang === "en" ? glossLine(gl) : "";
      if (i.match === "longer") meaning += `<span class="gloss match-note">${esc(t().longerText(num(i.source_words)))}</span>`;
      if (i.match === "partial" && (i.missing_words || []).length) meaning += `<span class="gloss match-note">${bidi(esc(t().partialText(i.missing_words.join(" "))))}</span>`;
      h += `<tr>
        <td class="who">${esc(lang === "ar" ? i.scholar_ar : i.scholar_en)}<span class="died">${esc(t().died(localDigits(i.died_ah)))}</span></td>
        <td><span class="g" lang="ar" dir="rtl">${esc(i.grade)}</span>${meaning}
          <details><summary>${esc(t().sourceText)}</summary><div class="htext" lang="ar" dir="rtl">${esc(i.text)}${i.rawi ? `<div class="after">${esc(t().rawi)}: ${esc(i.rawi)}</div>` : ""}</div></details></td>
        <td class="src"><ul class="srcs">${row.sources.map(sourceLine).join("")}</ul></td>
      </tr>`;
    }
    h += `</tbody></table>`;
  }
  if (all.some((i) => (i.grade_gloss || {}).bracketed)) {
    h += `<p class="after">${esc(t().brackets)} <a href="https://dorar.net/article/56" target="_blank" rel="noopener">${esc(t().bracketsLink)}</a></p>`;
  }
  if (hd.hidden_narrator_statements) h += `<p class="after">${esc(t().narrator(num(hd.hidden_narrator_statements)))}</p>`;
  if (groups.length) h += `<p class="after">${esc(t().onlyApproved)}</p>`;
  if (groups.length && lang === "en") h += `<p class="after">${esc(t().glossNote)}</p>`;
  if (hd.search_url) h += `<p class="after"><a href="${esc(hd.search_url)}" target="_blank" rel="noopener">${esc(t().searchDorar)}</a></p>`;
  return h;
}

const pct = (x) => (lang === "ar" ? `${num(Math.round(x))}٪` : `${Math.round(x)}%`);

function reasonsFor(c) {
  const r = t().r;
  const q = c.quran || {};
  const hd = c.hadith || {};
  const out = [];
  if (c.type === "quran" && q.surah != null) {
    if (c.status === "verified" && q.via === "arabic") out.push(r.compared, r.foundAt(place(q)));
    else if (c.status === "verified") out.push(r.enMatched(pct(q.score), place(q), t().trName[q.matched_translation] || t().trName.hilali));
    else if (c.status === "differs" && q.via === "arabic") {
      out.push(r.compared, r.nearest(place(q), pct(q.score)));
      for (const d of (q.diff || []).filter((d) => d.op !== "equal")) {
        if (d.op === "delete") out.push(r.extra(d.quoted));
        else if (d.op === "insert") out.push(r.missing(d.mushaf));
        else if (d.kind === "alef") out.push(r.alefChanged(d.quoted, d.mushaf));
        else out.push(r.changed(d.quoted, d.mushaf));
      }
      out.push(r.riwaya, r.copyRule);
    } else if (c.status === "differs") out.push(r.enDiffers(pct(q.score), place(q)));
    if (q.reference_given && q.reference_ok === false && q.cited) {
      out.push(r.refWritten(q.reference_given));
      const cp = place({ surah_name_ar: q.cited.surah_name_ar, surah_name_en: q.cited.surah_name_en, ayah_from: q.cited.ayah, ayah_to: q.cited.ayah });
      if (q.cited.exists) out.push({ text: r.refHolds(cp), quran: q.cited.text });
      else out.push(r.refNoAyah(lang === "ar" ? q.cited.surah_name_ar : q.cited.surah_name_en, num(q.cited.surah_ayat)));
      out.push(r.refActual(place(q)));
    } else if (q.reference_given && q.reference_ok === false) {
      out.push(r.refWritten(q.reference_given), r.refActual(place(q)));  // a surah named without an ayah
    } else if (q.reference_given) out.push(r.refRight(q.reference_given));
  }
  if (c.type === "quran" && c.status === "not_in_mushaf") {
    out.push(c.lang === "ar" ? r.notInMushaf(num(6236)) : r.notInTranslation(num(6236)));
    if (c.marker && !["﴿﴾", "ref", "unmarked", "model"].includes(c.marker)) out.push(r.attributed(c.marker.replace(/[:：]\s*$/, "")));
  }
  if (c.type === "hadith") {
    if (c.search_wording_ar) out.push(r.modelWords(c.search_wording_ar));
    if (hd.query) out.push(r.searched(hd.query));
    if (c.status === "graded" || c.status === "found_similar") {
      out.push(r.foundN(num(hd.count), pct(hd.best_similarity)));
      if (c.status === "found_similar") out.push(r.notWord);
      if (hd.longer_only) out.push(r.longerOnly);
      out.push(r.quoteOnly);
    }
    if (c.status === "not_found" && hd.query) out.push(r.noneFound, r.notMeaning);
    if ((c.notes || []).includes("hadith_is_quran")) out.push(r.isQuran);
    const at = c.attribution;
    if (at) {
      const names = (ks) => ks.map((k) => t().bookName[k]).join(t().and);
      if (!at.checked) out.push(r.attrUnchecked(at.written));
      else if (at.not_found_in.length) out.push(r.attrMissing(at.written, names(at.not_found_in)));
      else out.push(r.attrOk(at.written, names(at.confirmed)));
    }
    if ((c.notes || []).includes("firm_form")) out.push(r.firmForm);
  }
  return out;
}

// In the English view an Arabic reference such as «(البقرة: 154)» must keep its own direction inside the sentence.
const AR_RUN = /[(\[]?[\u0600-\u06FF][\u0600-\u06FF\u0660-\u06690-9\s:،.\-–]*[\u0600-\u06FF\u0660-\u06690-9][)\]]?/g;
function bidi(escaped) {
  return lang === "en" ? escaped.replace(AR_RUN, (m) => `<bdi dir="rtl">${m}</bdi>`) : escaped;
}

function renderWhy(c, cls) {
  const items = reasonsFor(c);
  if (!items.length) return "";
  const li = items.map((x) => typeof x === "string"
    ? `<li>${bidi(esc(x))}</li>`
    : `<li>${bidi(esc(x.text))}<span class="cited">${esc(glyphs(x.quran))}</span></li>`).join("");
  return `<details class="why"${cls === "ok" ? "" : " open"}><summary>${esc(t().why)}</summary><ul>${li}</ul></details>`;
}

function reportLink(c) {
  const q = c.quran || {};
  const body = [
    `Type: ${c.type}`, `Status: ${c.status}`, `Evidence tier: ${c.tier}`,
    q.ref ? `Mushaf reference: ${q.ref}` : "", c.hadith && c.hadith.query ? `Hadith search: ${c.hadith.query}` : "",
    "", "Quoted text:", c.quote, "", "What is wrong / ما الخطأ:", "",
  ].filter((x) => x !== null).join("\n");
  const url = `${REPO}/issues/new?labels=result-review&title=${encodeURIComponent("[مراجعة نتيجة] " + c.quote.slice(0, 60))}&body=${encodeURIComponent(body)}`;
  return `<p class="after report-link"><a href="${esc(url)}" target="_blank" rel="noopener">${esc(t().report)}</a> <span class="fine">${esc(t().reportNote)}</span></p>`;
}

function renderEntry(c) {
  const [verdict, cls] = verdictFor(c);
  const kind = c.type === "quran" ? t().quran : t().hadith;
  // One colour, one meaning: green only when the sources support it, red only for a fabricated grading,
  // orange for everything that needs attention or a specialist (data/display_rules.json).
  const fab = ((c.hadith || {}).fabricated_by || []).length > 0;
  const tierCls = { documented: "ok", supported: "ok", not_supported: fab ? "bad" : "warn", verify: "warn", refer: "warn" }[c.tier] || "";
  let h = `<li class="entry" style="--i:${c.id - 1}"><div class="entry-no">${num(c.id)}</div><div>
    <p class="entry-kind">${esc(kind)}${c.found_by === "model" ? ` · ${esc(t().byModel)}` : ""}
      <span class="tier ${tierCls}">${esc(t().tierLbl)}: ${esc(t().tier[c.tier] || "")}</span></p>
    <p class="verdict ${cls}">${esc(verdict)}</p>
    <p class="as-quoted"><span class="lbl">${esc(t().asQuoted)}</span><q><bdi dir="${c.lang === "ar" ? "rtl" : "ltr"}">${esc(c.quote)}</bdi></q></p>`;
  // Evidence first, then the explanation, then what to do.
  for (const n of c.notes || []) if (t().notes[n]) h += `<p class="line ${n === "match_by_model" ? "warn" : "note"}">${esc(t().notes[n])}</p>`;
  if (c.matched_arabic) h += `<p class="as-quoted"><span class="lbl">${esc(t().matchedArabic)}</span>${esc(c.matched_arabic)}</p>`;
  if (c.quran && c.quran.surah != null && (c.type === "quran" || (c.notes || []).includes("hadith_is_quran"))) h += renderMushaf(c.quran, c);
  if (c.hadith) h += renderGradings(c.hadith);
  h += renderWhy(c, cls);
  if (c.referral) h += `<p class="refer">${esc(c.referral[lang])}</p>`;
  h += reportLink(c);
  return h + `</div></li>`;
}

// The two scholars' fatwas: their words verbatim, the site's own source line and link; nothing written by the tool.
function renderScholarFatwas(sc) {
  const ar = (x) => `<bdi dir="rtl" lang="ar">${esc(x)}</bdi>`;
  let h = `<section class="fatwas"><h3 class="fatwas-h">${esc(t().fatwasOf(lang === "ar" ? sc.ar : sc.en))}</h3>`;
  if (sc.error) h += `<p class="fine">${esc(t().ferror)} <a href="${esc(sc.site)}" target="_blank" rel="noopener">${esc(lang === "ar" ? sc.site_ar : sc.site_en)}</a></p>`;
  else if (!sc.fatwas.length) h += `<p class="fine">${esc(t().fnone)} <a href="${esc(sc.search_url)}" target="_blank" rel="noopener">${esc(t().fsearch)}</a></p>`;
  for (const f of sc.fatwas) {
    h += `<article class="fatwa"><p class="fatwa-title">${ar(f.title)}</p>`;
    if (f.question) h += `<p class="fatwa-part"><span class="lbl">${esc(t().fq)}</span>${ar(f.question)}</p>`;
    if (f.opening) h += `<p class="fatwa-part"><span class="lbl">${esc(t().fopen)}</span>${ar(f.opening)}</p>`;
    if (f.answer) h += `<details class="fatwa-full"><summary>${esc(t().ffull)}</summary><div class="fatwa-text" dir="rtl" lang="ar">${esc(f.answer)}</div></details>`;
    const src = [lang === "ar" ? sc.site_ar : sc.site_en, f.source].filter(Boolean).join("، ");
    h += `<p class="after">${esc(t().fsource)}: ${esc(src)} · <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.answer || !f.opening ? t().flink : t().ffullSite)}</a></p></article>`;
  }
  h += `<p class="fine">${esc(lang === "ar" ? sc.terms_ar : sc.terms_en)}</p>`;
  return h + `</section>`;
}

function render(r) {
  $("report").hidden = false;
  if (r.summary.total) {
    const dr = r.display_rules || {};
    const rules = r.summary.hadith ? `<span class="fine rules-note">${esc(dr.status === "signed" ? t().rulesSigned(dr.reviewed_by, dr.reviewed_on) : t().rulesDraft)}</span>` : "";
    $("summary").innerHTML = t().summary(r.summary, (x) => esc(num(x))) + rules;
  }
  else $("summary").textContent = r.unsupported_language ? t().unsupported : t().none;
  if (r.summary.total && r.unsupported_language) $("summary").innerHTML += `<span class="fine rules-note">${esc(t().unsupportedPart)}</span>`;
  const tr = r.truncated;
  if (tr && tr.text_chars > tr.checked_chars) $("summary").innerHTML += `<span class="fine rules-note">${esc(t().truncatedText(num(tr.checked_chars), num(tr.text_chars)))}</span>`;
  if (tr && tr.citations_found > tr.citations_checked) $("summary").innerHTML += `<span class="fine rules-note">${esc(t().truncatedCits(num(tr.citations_checked), num(tr.citations_found)))}</span>`;
  const ld = $("leveld");
  ld.hidden = !r.level_d;
  if (r.level_d) {
    const b = r.level_d.body;
    const found = r.level_d.fatwas && r.level_d.fatwas.scholars && r.level_d.fatwas.scholars.length;
    let h;
    if (found) {
      h = `<p>${esc(t().leveldFound)}</p>` + r.level_d.fatwas.scholars.map(renderScholarFatwas).join("");
    } else {
      const refs = (r.level_d.references || []).map((x) =>
        `<li><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(lang === "ar" ? x.ar : x.en)}</a></li>`).join("");
      h = `<p>${esc(t().leveld)}</p>` + (refs ? `<ul class="refs">${refs}</ul>` : "");
    }
    ld.innerHTML = h + `<p class="body-ref">${esc(t().leveldBody(lang === "ar" ? b.ar : b.en))} <a href="${esc(b.url)}" target="_blank" rel="noopener">${esc(t().bodyLink)}</a></p>`;
  }
  $("results").innerHTML = r.citations.map(renderEntry).join("");
}

async function check() {
  const text = $("text").value.trim();
  if (text.length < 3) return;
  const deep = $("deep").checked;
  $("go").disabled = true;
  $("status").textContent = deep ? t().checkingDeep : t().checking;
  try {
    const res = await fetch("/api/check", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, deep }) });
    if (res.status === 429) { $("status").textContent = t().busy; return; }
    if (!res.ok) throw new Error(res.status);
    lastResult = await res.json();
    $("status").textContent = "";
    render(lastResult);
    health();
    $("report").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (e) {
    $("status").textContent = t().failed;
  } finally {
    $("go").disabled = false;
  }
}

// Plan item 17: say plainly when Dorar is down, before the visitor checks a hadith.
let dorarDown = false;
async function health() {
  try {
    const h = await (await fetch("/api/health")).json();
    dorarDown = h.dorar_enabled && h.dorar_reachable === false;
  } catch (e) { /* the check itself reports failures */ }
  showBanner();
}
function showBanner() {
  const b = $("banner");
  b.hidden = !dorarDown;
  if (dorarDown) b.textContent = t().dorarDown;
}

$("go").addEventListener("click", check);
$("text").addEventListener("input", updateCounter);
$("text").addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) check(); });
document.querySelectorAll("[data-sample]").forEach((b) => b.addEventListener("click", () => {
  $("text").value = SAMPLES[b.dataset.sample];
  $("text").dispatchEvent(new Event("input"));
  $("text").focus();
}));
$("lang").addEventListener("click", () => {
  lang = lang === "ar" ? "en" : "ar";
  try { localStorage.setItem("tathabbut-lang", lang); } catch (e) { /* storage may be blocked */ }
  applyLang();
});
try { const saved = localStorage.getItem("tathabbut-lang"); if (saved === "en" || saved === "ar") lang = saved; } catch (e) { /* ignore */ }
applyLang();
health();
