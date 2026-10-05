"use strict";

const T = {
  ar: {
    title: "تثبّت", tagline: "مدقق الاستشهادات الشرعية", mottoRef: "الحجرات ٦",
    verdictsTitle: "خلاصة أحكام علماء الحديث المعتمدين على هذا اللفظ",
    fAnswerTitle: "الجواب من فتاواهم",
    fNearTitle: "أقرب ما في فتاواهم (في مسألة قريبة من سؤالك)",
    fNearNote: "لم نجد في فتاواهما المنشورة جوابًا عن سؤالك نفسه؛ هذه أقرب فتوى إليه، ومسألتها قد تختلف عن مسألتك في قيد أو تفصيل. اقرأها كاملة، واسأل أهل العلم أو جهة الإفتاء عن حالتك.",
    fAnswerNote: "الجملة منقولة بنصها من الفتوى: اختارها النموذج اللغوي، وتحقّق النظام أنها فيها حرفًا بحرف، ولم يكتب منها شيئًا. اقرأ الفتوى كاملة قبل العمل بها.",
    navCheck: "الفحص", navArchive: "الأرشيف", navBot: "اسأل الثقات", navPillars: "أركان الإسلام", navDev: "للمطورين",
    historyTitle: "فحوصاتي على هذا الجهاز", historyNote: "تُحفظ في متصفحك وحده، ولا تصل إلينا. امسحها متى شئت.",
    historyClear: "امسح السجل", historyCount: (n) => `${n} استشهاد`,
    verdictLbl: { accepted: "صحيح أو حسن عند", weak: "ضعيف عند", fabricated: "موضوع أو لا أصل له عند" },
    verdictNote: "نقلٌ لأحكامهم كما وردت، بلا ترجيح بينها؛ وتفصيلها بنصها أدناه.",
    inputLabel: "النص المراد فحصه", intro: "الصق منشورًا أو درسًا أو إجابة مساعد ذكي، وسنتتبع كل آية وحديث فيه إلى مصدره.",
    placeholder: "الصق النص هنا", tryLabel: "أمثلة:", sampleAr: "منشور عربي", sampleEn: "English post",
    deep: "فحص معمّق: استعن بالنموذج اللغوي لاكتشاف ما فات الفحص الأساسي، وللنصوص الإنجليزية", check: "تحقّق من الاستشهادات",
    checking: "نستخرج الاستشهادات، ثم نطابق الآيات مع المصحف، ونبحث عن الأحاديث في الدرر السنية…", checkingDeep: "نراجع المصادر بالاستعانة بالنموذج اللغوي…",
    failed: "تعذّر الفحص الآن، حاول مرة أخرى.", reportTitle: "نتيجة الفحص",
    none: "لم نجد في النص آية أو حديثًا مستشهدًا به.",
    truncatedText: (a, b) => `النص أطول من حد الفحص، ففُحص أول ${a} حرف من ${b}.`,
    truncatedCits: (a, b) => `فُحص أول ${a} استشهادًا من ${b} وُجدت في النص. افحص الباقي في طلب آخر.`,
    dorarDown: "الموسوعة الحديثية غير متاحة الآن: الآيات تُفحص كالمعتاد، والأحاديث تُحال إلى المختص حتى تعود.",
    modelOff: "الفحص المعمّق غير متاح الآن لأن النموذج اللغوي متوقف، والفحص الأساسي يعمل كاملًا.",
    modelUsed: (n, m) => m && !/ALLaM/i.test(m) ? `استُعين بالنموذج اللغوي ${m} في هذا الفحص (${n} ث)، لأن علّام لم يكن متاحًا وقتها.` : `استُعين بعلّام في هذا الفحص (${n} ث).`,
    modelNotUsed: "لم يُستعن بالنموذج اللغوي في هذا الفحص.",
    busy: "طلبات كثيرة من هذا الجهاز في دقائق قليلة. انتظر قليلًا ثم أعد المحاولة.",
    unsupported: "هذه اللغة غير مدعومة بعد، فلم يُفحص النص. يفحص تثبّت اليوم النصوص العربية والإنجليزية، والآيات المنقولة بالترجمات المعتمدة الأردية والإندونيسية والفرنسية.",
    unsupportedPart: "وفي النص كلام بلغة غير مدعومة بعد، فلم يُفحص منه إلا الاستشهادات أعلاه.",
    summary: (s, n) => [`الاستشهادات <b>${n(s.total)}</b>`, s.documented && `مطابق للمصحف <b>${n(s.documented)}</b>`, s.supported && `تؤيده المصادر <b>${n(s.supported)}</b>`, s.not_supported && `لا تؤيده المصادر المعتمدة <b>${n(s.not_supported)}</b>`, s.verify && `يحتاج مزيدًا من التحقق <b>${n(s.verify)}</b>`, s.refer && `يُحال إلى مختص <b>${n(s.refer)}</b>`].filter(Boolean).join(" · "),
    howTitle: "منهج الأداة",
    m1t: "القرآن", m1: "يُطابق النص مع مصحف مجمع الملك فهد، ويُنبَّه على ما اختلف عن لفظ المصحف أو عن موضع الآية، مع إظهار النص الصحيح والسورة والآية. نص القرآن لا يُولَّد أبدًا.",
    m2t: "الحديث", m2: "يُبحث عنه في الموسوعة الحديثية للدرر السنية، وتُنقل أحكام أئمة الحديث ثم أحكام المحققين المعاصرين بنصها، مع اسم قائل كل حكم، دون ترجيح بينها.",
    m3t: "إذا لم نجد مصدرًا", m3: "يقال ذلك صراحة ويُحال إلى المختص، وأسئلة الفتوى الشخصية تُحال إلى جهة الإفتاء.",
    m4t: "النموذج اللغوي", m4: "يستخرج ويطابق فقط، ولا يحكم على حديث ولا يفتي. وكل ما يقترحه يجب أن يرد بلفظه في النص المفحوص، وإلا حُذف.",
    privacy: "لا نحفظ نصك، ولا يُرسل إلى الدرر السنية إلا لفظ الحديث المستخرج. وعند الفحص المعمّق يُرسل النص إلى علّام على خادم الفريق، وإن لم يكن متاحًا فإلى نموذج بديل لدى مزوّد استضافة، ويُذكر اسم النموذج في التقرير.",
    disclosure: "تثبّت أداة آلية مدعومة بالذكاء الاصطناعي، وليست عالمًا ولا مفتيًا.",
    apiLink: "الواجهة البرمجية لفحص إجابات المساعدات الذكية",
    botDemo: "اسأل الثقات: عن حكم شرعي أو حديث، أو افحص إجابة مساعد ذكي",
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
      loose_only: "لم نجد هذا النص بعينه، ووجدنا نصوصًا أخرى تشبهه في بعض ألفاظه", found_similar: "وُجدت روايات بلفظ مقارب، لا بلفظه",
      not_found: "لم نجد حكمًا لأحد علماء الحديث المعتمدين على هذا النص",
      needs_model: "النص مترجم، والبحث عن أصله العربي يحتاج إلى النموذج اللغوي",
      language_referral: "حديث بغير العربية والإنجليزية، فلم نبحث عن أصله آليًا، ونحيله إلى المختص",
      source_error: "تعذّر الوصول إلى الموسوعة الحديثية الآن",
      source_offline: "البحث في الموسوعة الحديثية غير مفعّل",
      error: "حدث خطأ أثناء الفحص",
    },
    surah: "سورة", ayahWord: "الآية", ayatWord: "الآيات",
    fixesHead: ["ورد في النص", "في المصحف"], missing: "(سقط من النص)", extra: "(ليس في المصحف)",
    translationLbl: "ترجمة معاني القرآن الكريم (الهلالي ومحسن خان، مجمع الملك فهد ١٤١٧هـ، عن موقع QuranEnc.com، الإصدار ١٫١٫٢)", trName: { hilali: "الهلالي ومحسن خان (مجمع الملك فهد)", saheeh: "صحيح إنترناشونال", ur_junagarhi: "جوناكري الأردية (مجمع الملك فهد)", id_kfc: "المجمع الإندونيسية (مع وزارة الشؤون الدينية الإندونيسية)", fr_hamidullah: "محمد حميد الله الفرنسية" },
    ayahLink: "الآية في موسوعة قرآنبيديا", trLink: "الترجمة الإنجليزية وحواشيها", trLinkOther: "الترجمة في قرآنبيديا",
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
    leveldGeneral: "هذا سؤال عن حكم شرعي، وتثبّت لا يفتي. ابحث عن المسألة في فتاوى العلماء الرسمية:",
    looseNote: "الأحاديث أدناه نصوص أخرى غير النص المنقول، تشبهه في بعض ألفاظه فقط. وأحكام العلماء المذكورة عليها هي، لا على نصك، فلا تُعدّ حكمًا عليه.",
    outOfScope: "تثبّت يتحقق من الآيات والأحاديث، ويعرض فتاوى العلماء في الأحكام الشرعية. وهذا السؤال ليس عن آية ولا حديث ولا حكم شرعي، فليس عندنا ما نعرضه فيه.",
    searchedAs: (w) => `بحثنا في الفتاوى بعنوان المسألة: «${w}»؛ صاغه النموذج اللغوي من سؤالك للبحث فقط، والفتاوى منقولة بنصها.`,
    leveldGeneralFound: "هذا سؤال عن حكم شرعي، وتثبّت لا يفتي. هذه فتاوى سماحة الشيخ عبدالعزيز بن باز وفضيلة الشيخ محمد بن صالح العثيمين رحمهما الله في مسائل قريبة من السؤال، منقولة بنصها من موقعيهما الرسميين مع مصدر كل فتوى ورابطها. اختيرت بتقارب الألفاظ، ولم يكتبها النموذج اللغوي ولم يخترها، فتأكد أنها تطابق مسألتك.",
    leveldRuling: "في النص حكم على حالة شخصية بعينها، والفتوى في الحالة الخاصة لمفتٍ يعرف الواقعة.",
    leveldBody: (b) => `فإن لم يوجد فيها ما يستوفي الحالة، فيُرجى سؤال ${b}.`,
    bodyLink: "موقع الرئاسة العامة للبحوث العلمية والإفتاء",
    fatwasOf: (n) => `فتاوى ${n}`, fq: "السؤال", fopen: "أول الجواب بنصه", fsource: "المصدر",
    ffull: "اعرض الفتوى كاملة", ffullSite: "اعرض الفتوى كاملة في موقع المؤسسة", flink: "رابط الفتوى في الموقع",
    fnone: "لم نجد في فتاواه المنشورة ما يقارب ألفاظ السؤال.", ferror: "تعذّر الوصول إلى موقعه الآن.", fsearch: "ابحث بنفسك في موقعه",
    why: "سبب هذه النتيجة",
    tier: { documented: "مطابق للمصحف", supported: "تؤيده المصادر", not_supported: "لا تؤيده المصادر المعتمدة", verify: "يحتاج مزيدًا من التحقق", refer: "يُحال إلى مختص" },
    rulesDraft: "قواعد حالة الدليل مسودة من الفريق، تنتظر توقيع المراجِعة الشرعية.", rulesSigned: (who, d) => `قواعد حالة الدليل راجعتها ووقّعتها ${who} في ${d}.`,
    copy: "انسخ الاستشهاد بمصدره", copied: "نُسخ",
    copyNo: { found_similar: "لا يُنسخ: اللفظ المنقول لا يطابق الروايات.", not_found: "لا يُنسخ: لم نجد له مصدرًا.", not_in_mushaf: "لا يُنسخ: لم نجده في المصحف.", other: "لا يُنسخ: لم يكتمل التحقق." },
    rawaHu: (b, n) => `رواه ${b} (${n})`, gradedBy: (who, g, src) => `حكم ${who}: «${g}» (${src})`,
    meta: (d, v) => `فحص تثبّت بتاريخ ${d}، الإصدار ${v}. هذا التقرير يخص الاستشهادات المذكورة فقط، وليس شهادة على النص كله.`,
    casesTitle: "جرّب حالات الاختبار", expected: "النتيجة المتوقعة",
    tierLbl: "حالة الدليل",
    tierShort: { documented: "مطابق", supported: "مؤيَّد", not_supported: "غير مؤيَّد", verify: "تحقَّق", refer: "إحالة" },
    textTitle: "النص المفحوص", textNote: "المعلَّم استشهادات فُحصت، والنقر عليه ينقل إلى نتيجته. وما سواه كلام الكاتب، لم يُفحص.",
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
      trDiffers: (pct, p, tr) => `الترجمة المنقولة لا تطابق حرفيًا ترجمة ${tr} التي نقارن بها (تقارب ${pct})، وأقرب آية لمعناها ${p}. ترجمات المعاني تختلف، فالمرجع هو الأصل العربي.`,
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
      modelWords: (w) => `اقترح النموذج اللغوي كلمات عربية للبحث: «${w}»، ثم اختار من نتائج المصادر الأصل الأقرب لمعنى النص المسؤول عنه.`,
      isQuran: "وجدنا هذا النص بلفظه في المصحف، فهو آية لا حديث.",
      needsModel: "النص بغير العربية، والبحث في الموسوعة الحديثية يكون باللفظ العربي، والنموذج اللغوي غير مفعّل الآن.",
    },
    credit: "يعمل بنموذج علّام من سدايا، ومصادره من الحزمة العلمية للتحدي.",
  },
  en: {
    verdictsTitle: "What the approved hadith scholars said of this wording",
    fAnswerTitle: "The answer, from their fatwas",
    fNearTitle: "The closest in their fatwas (on a question close to yours)",
    fNearNote: "Their published fatwas do not answer your exact question; this is the closest one, and its question may differ from yours in a condition or detail. Read it in full, and ask a scholar or the fatwa authority about your case.",
    fAnswerNote: "This sentence is quoted verbatim from the fatwa: the language model chose it and the system checked it is there word for word; nothing in it was written by the model. Read the whole fatwa before acting on it.",
    navCheck: "Check", navArchive: "Archive", navBot: "Ask the trusted", navPillars: "Pillars of Islam", navDev: "Developers",
    historyTitle: "My checks on this device", historyNote: "Kept in your browser only; they never reach us. Clear them any time.",
    historyClear: "Clear history", historyCount: (n) => `${n} citation${n === 1 ? "" : "s"}`,
    verdictLbl: { accepted: "Authentic or good according to", weak: "Weak according to", fabricated: "Fabricated or baseless according to" },
    verdictNote: "Their gradings as stated, not weighed against each other; each is quoted in full below.",
    title: "Tathabbut", tagline: "Islamic citation checker", mottoRef: "al-Hujurat 49:6 · “verify it” (King Fahd Complex translation)",
    inputLabel: "Text to check", intro: "Paste a post, a lecture or an AI assistant's answer, and we will trace every Quran verse and hadith in it to its source.",
    placeholder: "Paste your text here", tryLabel: "Examples:", sampleAr: "Arabic post", sampleEn: "English post",
    deep: "Deep check: use the language model to find what the basic check missed, and for English text", check: "Check citations",
    checking: "Extracting citations, matching verses with the Mushaf and searching hadith on Dorar…", checkingDeep: "Checking the sources with the language model…",
    failed: "The check failed. Please try again.", reportTitle: "Result",
    none: "No Quran verse or hadith citation was found in the text.",
    truncatedText: (a, b) => `The text is longer than the check limit; the first ${a} of ${b} characters were checked.`,
    truncatedCits: (a, b) => `The first ${a} of ${b} citations found were checked. Check the rest in another request.`,
    dorarDown: "The hadith encyclopedia cannot be reached right now: verses are checked as usual, and hadith are referred to a specialist until it is back.",
    modelOff: "The deep check is unavailable right now because the language model is off; the basic check works in full.",
    modelUsed: (n, m) => m && !/ALLaM/i.test(m) ? `The language model ${m} was used in this check (${n} s), because ALLaM was not available at the time.` : `ALLaM was used in this check (${n} s).`,
    modelNotUsed: "The language model was not used in this check.",
    busy: "Too many requests from this device in a few minutes. Please wait a little and try again.",
    unsupported: "This language is not supported yet, so the text was not checked. Tathabbut checks Arabic and English today, and verses quoted in the approved Urdu, Indonesian or French translation.",
    unsupportedPart: "Part of the text is in a language not supported yet; only the citations above were checked.",
    summary: (s, n) => [`Citations <b>${n(s.total)}</b>`, s.documented && `matches the Mushaf <b>${n(s.documented)}</b>`, s.supported && `supported by the sources <b>${n(s.supported)}</b>`, s.not_supported && `not supported by the approved sources <b>${n(s.not_supported)}</b>`, s.verify && `needs more verification <b>${n(s.verify)}</b>`, s.refer && `refer to a specialist <b>${n(s.refer)}</b>`].filter(Boolean).join(" · "),
    howTitle: "Method",
    m1t: "Quran", m1: "Matched against the King Fahd Complex Mushaf; any word or reference that differs is pointed out, with the correct text, surah and ayah shown. Quran text is never generated.",
    m2t: "Hadith", m2: "Looked up in the Dorar hadith encyclopedia. Gradings by the classical imams of hadith, then by modern hadith editors, are quoted verbatim, each with the name of the scholar who gave it, with no preference between them.",
    m3t: "When no source is found", m3: "The tool says so plainly and refers you to a specialist; personal fatwa questions go to a fatwa authority.",
    m4t: "Language model", m4: "Only extracts and matches; it never grades a hadith or gives a fatwa. Anything it suggests must appear verbatim in the checked text, or it is dropped.",
    privacy: "Your text is not stored. Only the extracted hadith wording is sent to Dorar. In the deep check the text is sent to ALLaM on the team's server or, when it is not available, to a fallback model at a hosting provider; the report names the model.",
    disclosure: "Tathabbut is an AI-assisted tool, not a scholar or a mufti.",
    apiLink: "API for checking AI assistants' answers",
    botDemo: "Try checking an AI assistant's answer before it is shown (Arabic page)",
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
      loose_only: "This text itself was not found; other texts that share some of its words were", found_similar: "Narrations with similar, not identical, wording were found",
      not_found: "No grading by the approved hadith scholars was found",
      needs_model: "This is a translation; finding its Arabic source needs the language model",
      language_referral: "A hadith in a language other than Arabic or English; its source was not searched automatically, so it is referred to a specialist",
      source_error: "The hadith encyclopedia could not be reached",
      source_offline: "Hadith encyclopedia lookup is turned off",
      error: "An error occurred during the check",
    },
    surah: "Surah", ayahWord: "ayah", ayatWord: "ayat",
    fixesHead: ["As quoted", "In the Mushaf"], missing: "(left out)", extra: "(not in the Mushaf)",
    translationLbl: "Translation of the meanings (al-Hilali & Muhsin Khan, King Fahd Complex 1417 AH; via QuranEnc.com v1.1.2)", trName: { hilali: "al-Hilali & Muhsin Khan (King Fahd Complex)", saheeh: "Saheeh International", ur_junagarhi: "Junagarhi Urdu (King Fahd Complex)", id_kfc: "King Fahd Complex Indonesian (with Indonesia's Ministry of Religious Affairs)", fr_hamidullah: "Muhammad Hamidullah's French" },
    ayahLink: "This verse on Quranpedia", trLink: "Full translation with the translators' notes", trLinkOther: "This translation on Quranpedia",
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
    leveldGeneral: "This is a question about a ruling, and Tathabbut does not issue fatwas. Look for it in the official fatwas of the scholars:",
    looseNote: "The hadiths below are other texts, not the one quoted; they share only some of its words. The scholars' gradings shown are on them, not on your text, so they are not a grading of it.",
    outOfScope: "Tathabbut checks Quran verses and hadith, and shows scholars' fatwas on rulings. This question is not about a verse, a hadith or a ruling, so there is nothing for us to show.",
    searchedAs: (w) => `The fatwas were searched with the topic «${w}»: the language model worded it from your question for the search only; the fatwas are quoted verbatim.`,
    leveldGeneralFound: "This is a question about a ruling, and Tathabbut does not issue fatwas. Below are published fatwas of Shaykh Abd al-Aziz ibn Baz and Shaykh Muhammad ibn Salih al-Uthaymeen on close questions, quoted in Arabic exactly as on their official sites with each fatwa's source and link. They were chosen by word overlap; the language model neither wrote nor chose them, so check that they match your question.",
    leveldRuling: "The text rules on one person's own case; a fatwa on a particular case belongs to a mufti who knows its facts.",
    leveldBody: (b) => `If they do not cover the case, ask ${b}.`,
    bodyLink: "General Presidency of Scholarly Research and Ifta (official site)",
    fatwasOf: (n) => `Fatwas of ${n}`, fq: "Question", fopen: "Opening of the answer, verbatim", fsource: "Source",
    ffull: "Show the full fatwa", ffullSite: "Read the full fatwa on the foundation's site", flink: "Fatwa page on the site",
    fnone: "None of his published fatwas is close to the question's wording.", ferror: "His site could not be reached right now.", fsearch: "Search his site yourself",
    why: "Why this result",
    tier: { documented: "Matches the Mushaf", supported: "Supported by the sources", not_supported: "Not supported by the approved sources", verify: "Needs more verification", refer: "Refer to a specialist" },
    rulesDraft: "The evidence-status rules are the team's draft, awaiting the Sharia reviewer's signature.", rulesSigned: (who, d) => `The evidence-status rules were reviewed and signed by ${who} on ${d}.`,
    copy: "Copy the citation with its source", copied: "Copied",
    copyNo: { found_similar: "Not copyable: the quoted wording does not match the narrations.", not_found: "Not copyable: no source was found.", not_in_mushaf: "Not copyable: not found in the Mushaf.", other: "Not copyable: the check is incomplete." },
    rawaHu: (b, n) => `Narrated by ${b} (${n})`, gradedBy: (who, g, src) => `${who}: «${g}» (${src})`,
    meta: (d, v) => `Tathabbut check of ${d}, version ${v}. This report covers the citations listed only; it does not vouch for the text as a whole.`,
    casesTitle: "Try the test cases", expected: "Expected result",
    tierLbl: "Evidence status",
    tierShort: { documented: "matches", supported: "supported", not_supported: "not supported", verify: "verify", refer: "refer" },
    textTitle: "The text checked", textNote: "Marked passages are the citations checked; select one to go to its result. Everything else is the writer's own words and was not checked.",
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
      trDiffers: (pct, p, tr) => `The quoted translation does not match the ${tr} translation word for word (${pct} close); the nearest verse in meaning is ${p}. Translations of the meanings vary; the Arabic is the reference.`,
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
      modelWords: (w) => `The language model suggested Arabic search words «${w}», then picked, among the sources' results, the one closest in meaning to the text asked about.`,
      isQuran: "This exact text is in the Mushaf, so it is a verse, not a hadith.",
      needsModel: "The text is not in Arabic; the hadith encyclopedia is searched in Arabic and the language model is off right now.",
    },
    credit: "Powered by SDAIA's ALLaM model; sources from the challenge's scientific package.",
  },
};

// Plan item 34: eight test cases a judge can run, each with the result the team expects.
const CASES = [
  { text: "قال تعالى: ﴿إن مع العسر يسرا﴾", ar: "آية صحيحة بالإملاء الشائع ← «مطابق للمصحف» (الشرح ٦)", en: "A correct ayah in common spelling → matches the Mushaf (al-Sharh 6)" },
  { text: "قال تعالى: ﴿يا أيها الذين آمنوا إن جاءكم فاسق بخبر فتبينوا﴾", ar: "آية منقولة بخطأ ← كلمة مخالفة ونص المصحف (الحجرات ٦)", en: "A misquoted ayah → one word differs, with the Mushaf text (al-Hujurat 6)" },
  { text: "قال تعالى: «إن الله مع الصابرين» (البقرة 200)", ar: "عزو خطأ ← الآية صحيحة والرقم خطأ، وموضعها البقرة ١٥٣", en: "Wrong reference → the ayah is right, the number wrong; it is al-Baqarah 153" },
  { text: "قال رسول الله ﷺ: «إنما الأعمال بالنيات» متفق عليه.", ar: "حديث في الصحيحين ← «تؤيده المصادر»، والعزو يوافق", en: "A hadith in both Sahihs → supported, and the written attribution agrees" },
  { text: "قال رسول الله ﷺ: «اطلبوا العلم ولو في الصين» رواه البخاري.", ar: "موضوع منسوب إلى البخاري ← «لا تؤيده المصادر المعتمدة» بالأحمر، ولم يوجد في صحيح البخاري", en: "Fabricated, attributed to al-Bukhari → not supported (red), not found in Sahih al-Bukhari" },
  { text: "قال رسول الله ﷺ: «أحب الأعمال إلى الله أدومها وإن كثر»", ar: "قول غُيّرت كلمة فيه («وإن قل») ← لفظ مقارب، لا يأخذ حكم الحديث", en: "One word changed («وإن قل») → a similar wording; it does not take the hadith's grading" },
  { text: "قال رسول الله ﷺ: «من غشنا فليس منا»", ar: "حديث في صحيح مسلم مع حكم على رواية أطول ← «تؤيده المصادر»، وحكم الرواية الأطول معروض بتنبيه", en: "In Sahih Muslim, with a grading of a longer narration → supported; the longer one is shown with a note" },
  { text: "أنا طلقت زوجتي وهي حائض، فهل يقع الطلاق؟", ar: "سؤال فتوى شخصية ← فتاوى الشيخين المنشورة ثم جهة الإفتاء، ولا حكم من الأداة", en: "A personal fatwa question → the two scholars' published fatwas, then the official body; no ruling from the tool" },
];

function renderCases() {
  $("cases-list").innerHTML = CASES.map((c, i) =>
    `<li><button type="button" class="linkish case" data-case="${i}">${esc(num(i + 1))}. ${esc(c.text)}</button><span class="fine">${esc(t().expected)}: ${esc(arData() ? c.ar : c.en)}</span></li>`).join("");
}

const SAMPLES = {
  ar: "أيها الإخوة، يقول الله تعالى: ﴿يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا جَاءَكُمْ فَاسِقٌ بِخَبَرٍ فَتَبَيَّنُوا﴾ (البقرة: 6).\nوقال رسول الله ﷺ: «إنما الأعمال بالنيات».\nوفي الحديث: «اطلبوا العلم ولو في الصين».\nومن يتق الله يجعل له مخرجا ويرزقه من حيث لا يحتسب، فلا تيأسوا.\nوقال تعالى: «النظافة من الإيمان».",
  en: "The Prophet (ﷺ) said: \"Actions are judged by intentions.\"\nAllah says in the Quran: \"Indeed, with hardship comes ease\" (94:6).\nThe Prophet (pbuh) said: \"Seek knowledge even if you have to go to China.\"",
};

const REPO = "https://github.com/M-Ev/tathabbut";
let lang = "ar";
let lastResult = null;
let lastText = "";
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
// Urdu and Indonesian (static/i18n.js) fall back to English for any missing key.
const merge = (base, over) => Object.fromEntries(Object.keys({ ...base, ...over }).map((k) =>
  [k, over && k in over ? (over[k] && typeof over[k] === "object" && !Array.isArray(over[k]) && base[k] ? merge(base[k], over[k]) : over[k]) : base[k]]));
if (typeof T_EXTRA !== "undefined") for (const k of Object.keys(T_EXTRA)) T[k] = merge(T.en, T_EXTRA[k]);
if (typeof T_MORE !== "undefined") for (const k of Object.keys(T_MORE)) T[k] = merge(T.en, T_MORE[k]);
const LANGS = Object.keys(T);
const arData = () => lang === "ar" || lang === "ur";  // Arabic names of scholars, books and surahs (Urdu readers read them)
const latin = () => !arData();  // English names and the English Jamhara gloss for every non-Arabic-script reader
const t = () => T[lang];
const num = (n) => (lang === "ar" ? Number(n).toLocaleString("ar-EG") : String(n));
const localDigits = (s) => (lang === "ar" ? String(s ?? "").replace(/[0-9]/g, (d) => "٠١٢٣٤٥٦٧٨٩"[d]) : String(s ?? ""));
const arDigits = (n) => Number(n).toLocaleString("ar-EG", { useGrouping: false });
// Arabic count of «موضع»: موضع واحد، موضعين، ٣–١٠ مواضع، ١١ موضعًا فأكثر.
const arPlaces = (n) => (n === 1 ? "موضع واحد" : n === 2 ? "موضعين" : `${arDigits(n)} ${n <= 10 ? "مواضع" : "موضعًا"}`);
const updateCounter = () => { $("counter").textContent = localDigits(`${$("text").value.length} / 8000`); };

function applyLang() {
  document.documentElement.lang = lang;
  document.documentElement.dir = arData() ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t()[el.dataset.i18n]; });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.placeholder = t()[el.dataset.i18nPh]; });
  $("lang").value = lang;
  updateCounter();
  document.title = `${t().title} · ${t().tagline}`;
  if (lastResult) render(lastResult);
  showBanner();
  renderCases();
  if (typeof HKEY !== "undefined") showHistory();
}

function place(q) {
  const name = arData() ? q.surah_name_ar : q.surah_name_en;
  const a = q.ayah_from === q.ayah_to ? num(q.ayah_from) : `${num(q.ayah_from)}–${num(q.ayah_to)}`;
  const word = q.ayah_from === q.ayah_to ? t().ayahWord : t().ayatWord;
  return `${t().surah} ${name}، ${word} ${a}`.replace("، ", arData() ? "، " : ", ");
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
  if (c.status === "found_similar" && hd.loose_only) return [v.loose_only, "warn"];
  const cls = { graded: "ok", found_similar: "warn", not_found: "warn", needs_model: "warn", language_referral: "warn", source_error: "warn", error: "bad" }[c.status] || "";
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
  const uiTr = lang !== "ar" && lang !== "en" && q.translations && q.translations[lang];
  if (uiTr) {
    // The reader's language: the King Fahd Complex translation of this verse, copied as published.
    h += `<p class="translation" dir="${arData() ? "rtl" : "ltr"}" lang="${lang}"><span class="lbl">${esc(t().translationLbl)}</span>${esc(uiTr.text)}</p>`;
  } else if (q.translation) {
    // Plan item 36: the approved translation in the quote's own language, beside the Mushaf text.
    const tr = q.translation;
    h += `<p class="translation" dir="${tr.lang === "ur" ? "rtl" : "ltr"}" lang="${esc(tr.lang)}"><span class="lbl" dir="${arData() ? "rtl" : "ltr"}">${esc(arData() ? tr.name_ar : tr.name_en)}</span>${esc(tr.text)}</p>`;
  } else if (lang === "en" || c.lang === "en") h += `<p class="translation"><span class="lbl">${esc(t().translationLbl)}</span>${esc(q.translation_en)}</p>`;
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
  if (uiTr) h += ` · <a href="${esc(uiTr.url)}" target="_blank" rel="noopener">${esc(t().trLinkOther)}</a>`;
  else if (q.translation) h += ` · <a href="${esc(q.translation.url)}" target="_blank" rel="noopener">${esc(t().trLinkOther)}</a>`;
  else if (lang === "en" || c.lang === "en") h += ` · <a href="${esc(q.translation_url)}" target="_blank" rel="noopener">${esc(t().trLink)}</a>`;
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
  if (arData()) return `<li>${esc(i.book)}، ${no}${link}</li>`;
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
  const fab = latin() && hd.fabricated_by_en ? hd.fabricated_by_en : hd.fabricated_by;
  if (hd.verdicts && hd.verdicts.length) {
    const cls = { accepted: "ok", weak: "warn", fabricated: "bad" };
    h += `<div class="verdicts"><p class="lbl">${esc(t().verdictsTitle)}</p>` + hd.verdicts.map((v) =>
      `<p class="line ${cls[v.verdict]}"><b>${esc(t().verdictLbl[v.verdict])}</b> ${esc((arData() ? v.scholars_ar : v.scholars_en).join(arData() ? "، " : ", "))}</p>`).join("")
      + `<p class="fine">${esc(t().verdictNote)}</p></div>`;
  } else if (fab && fab.length) h += `<p class="line bad">${esc(t().fabBy(fab.join(arData() ? "، " : ", ")))}</p>`;
  if (hd.loose_only) h += `<p class="line warn">${esc(t().looseNote)}</p>`;
  if (hd.sahihayn && hd.sahihayn.length) {
    const list = hd.sahihayn.map((x) => {
      const name = arData() ? `${esc(x.book)} (${esc(localDigits(x.number))})` : `${esc(x.book_en || x.book)} (no. ${esc(x.number)})`;
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
    h += `<table class="grades"><caption>${esc(arData() ? g.label_ar : g.label_en)}</caption>
      <thead><tr><th>${esc(t().gradeCols[0])}</th><th>${esc(t().gradeCols[1])}</th><th>${esc(t().gradeCols[2])}</th></tr></thead><tbody>`;
    for (const row of groupRows(g.items)) {
      const i = row.first;
      const gl = i.grade_gloss || {};
      let meaning = latin() ? glossLine(gl) : "";
      if (i.match === "longer") meaning += `<span class="gloss match-note">${esc(t().longerText(num(i.source_words)))}</span>`;
      if (i.match === "partial" && (i.missing_words || []).length) meaning += `<span class="gloss match-note">${bidi(esc(t().partialText(i.missing_words.join(" "))))}</span>`;
      h += `<tr>
        <td class="who">${esc(arData() ? i.scholar_ar : i.scholar_en)}<span class="died">${esc(t().died(localDigits(i.died_ah)))}</span></td>
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
  if (groups.length && latin()) h += `<p class="after">${esc(t().glossNote)}</p>`;
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
    } else if (c.status === "differs" && q.translation) out.push(r.trDiffers(pct(q.score), place(q), t().trName[q.matched_translation]));
    else if (c.status === "differs") out.push(r.enDiffers(pct(q.score), place(q)));
    if (q.reference_given && q.reference_ok === false && q.cited) {
      out.push(r.refWritten(q.reference_given));
      const cp = place({ surah_name_ar: q.cited.surah_name_ar, surah_name_en: q.cited.surah_name_en, ayah_from: q.cited.ayah, ayah_to: q.cited.ayah });
      if (q.cited.exists) out.push({ text: r.refHolds(cp), quran: q.cited.text });
      else out.push(r.refNoAyah(arData() ? q.cited.surah_name_ar : q.cited.surah_name_en, num(q.cited.surah_ayat)));
      out.push(r.refActual(place(q)));
    } else if (q.reference_given && q.reference_ok === false) {
      out.push(r.refWritten(q.reference_given), r.refActual(place(q)));  // a surah named without an ayah
    } else if (q.reference_given) out.push(r.refRight(q.reference_given));
  }
  if (c.type === "quran" && c.status === "not_in_mushaf") {
    out.push(c.lang === "ar" ? r.notInMushaf(num(6236)) : r.notInTranslation(num(6236)));
    if (c.marker && !["﴿﴾", "ref", "unmarked", "model", "bare", "asked"].includes(c.marker)) out.push(r.attributed(c.marker.replace(/[:：]\s*$/, "")));
  }
  if (c.type === "hadith") {
    if (c.search_wording_ar) out.push(r.modelWords((c.search_wordings_ar && c.search_wordings_ar.length ? c.search_wordings_ar : [c.search_wording_ar]).join("» · «")));
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
  return latin() ? escaped.replace(AR_RUN, (m) => `<bdi dir="rtl">${m}</bdi>`) : escaped;
}

function renderWhy(c, cls) {
  const items = reasonsFor(c);
  if (!items.length) return "";
  const li = items.map((x) => typeof x === "string"
    ? `<li>${bidi(esc(x))}</li>`
    : `<li>${bidi(esc(x.text))}<span class="cited">${esc(glyphs(x.quran))}</span></li>`).join("");
  return `<details class="why"${cls === "ok" ? "" : " open"}><summary>${esc(t().why)}</summary><ul>${li}</ul></details>`;
}

// Plan item 28: the copied text is built from the source fields only, never from the quote as written.
function copyFor(c) {
  const q = c.quran || {};
  if (c.type === "quran") {
    if (!(["verified", "differs"].includes(c.status) && q.surah != null && q.via === "arabic")) return { no: t().copyNo[c.status] || t().copyNo.other };
    const text = (q.ayat && q.ayat.length ? q.ayat.map((a) => a.text) : [q.mushaf_text]).join(" ");
    const a = q.ayah_from === q.ayah_to ? q.ayah_from : `${q.ayah_from}-${q.ayah_to}`;
    return { text: `﴿${glyphs(text)}﴾ [${q.surah_name_ar}: ${a}]` };
  }
  const hd = c.hadith || {};
  if (c.status !== "graded") return { no: t().copyNo[c.status] || t().copyNo.other };
  const items = (hd.groups || []).flatMap((g) => g.items);
  if ((hd.sahihayn || []).length) {
    const first = items.find((i) => i.book === hd.sahihayn[0].book && i.number === hd.sahihayn[0].number) || items[0];
    const by = hd.sahihayn.map((x) => `${x.book.replace("صحيح ", "")} (${x.number})`).join("، و");
    return { text: `«${first.text}» رواه ${by}.\n${hd.sahihayn[0].url || hd.search_url}` };
  }
  const same = items.filter((i) => (i.match || "same") === "same" && i.similarity >= 85);
  if (!same.length) return { no: t().copyNo.other };
  const lines = same.map((i) => `حكم ${i.scholar_ar}: «${i.grade}» (${i.book}، ${i.number}) ${i.url || ""}`.trim());
  return { text: `«${same[0].text}»\n${lines.join("\n")}` };
}

function copyButton(c) {
  const x = copyFor(c);
  if (x.no) return `<p class="after copy-row"><button type="button" class="linkish copy" disabled>${esc(t().copy)}</button> <span class="fine">${esc(x.no)}</span></p>`;
  return `<p class="after copy-row"><button type="button" class="linkish copy" data-copy="${esc(x.text)}">${esc(t().copy)}</button></p>`;
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
  let h = `<li class="entry" id="c-${c.id}" tabindex="-1" style="--i:${c.id - 1}"><div class="entry-no">${num(c.id)}</div><div>
    <p class="entry-kind">${esc(kind)}${c.found_by === "model" ? ` · ${esc(t().byModel)}` : ""}
      <span class="tier ${tierCls}">${esc(t().tierLbl)}: ${esc(t().tier[c.tier] || "")}</span></p>
    <p class="verdict ${cls}">${esc(verdict)}</p>
    <p class="as-quoted"><span class="lbl">${esc(t().asQuoted)}</span><q><bdi dir="${c.lang === "ar" || c.lang === "ur" ? "rtl" : "ltr"}">${esc(c.quote)}</bdi></q></p>`;
  // Evidence first, then the explanation, then what to do.
  for (const n of c.notes || []) if (t().notes[n]) h += `<p class="line ${n === "match_by_model" ? "warn" : "note"}">${esc(t().notes[n])}</p>`;
  if (c.matched_arabic) h += `<p class="as-quoted"><span class="lbl">${esc(t().matchedArabic)}</span>${esc(c.matched_arabic)}</p>`;
  if (c.quran && c.quran.surah != null && (c.type === "quran" || (c.notes || []).includes("hadith_is_quran"))) h += renderMushaf(c.quran, c);
  if (c.hadith) h += renderGradings(c.hadith);
  h += renderWhy(c, cls);
  if (c.referral) h += `<p class="refer">${esc(c.referral[lang])}</p>`;
  h += copyButton(c);
  h += reportLink(c);
  return h + `</div></li>`;
}

// The two scholars' fatwas: their words verbatim, the site's own source line and link; nothing written by the tool.
function renderScholarFatwas(sc) {
  const ar = (x) => `<bdi dir="rtl" lang="ar">${esc(x)}</bdi>`;
  let h = `<section class="fatwas"><h3 class="fatwas-h">${esc(t().fatwasOf(arData() ? sc.ar : sc.en))}</h3>`;
  if (sc.error) h += `<p class="fine">${esc(t().ferror)} <a href="${esc(sc.site)}" target="_blank" rel="noopener">${esc(arData() ? sc.site_ar : sc.site_en)}</a></p>`;
  else if (!sc.fatwas.length) h += `<p class="fine">${esc(t().fnone)} <a href="${esc(sc.search_url)}" target="_blank" rel="noopener">${esc(t().fsearch)}</a></p>`;
  for (const f of sc.fatwas) {
    h += `<article class="fatwa"><p class="fatwa-title">${ar(f.title)}</p>`;
    if (f.question) h += `<p class="fatwa-part"><span class="lbl">${esc(t().fq)}</span>${ar(f.question)}</p>`;
    if (f.opening) h += `<p class="fatwa-part"><span class="lbl">${esc(t().fopen)}</span>${ar(f.opening)}</p>`;
    if (f.answer) h += `<details class="fatwa-full"><summary>${esc(t().ffull)}</summary><div class="fatwa-text" dir="rtl" lang="ar">${esc(f.answer)}</div></details>`;
    const src = [arData() ? sc.site_ar : sc.site_en, f.source].filter(Boolean).join("، ");
    h += `<p class="after">${esc(t().fsource)}: ${esc(src)} · <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.answer || !f.opening ? t().flink : t().ffullSite)}</a></p></article>`;
  }
  h += `<p class="fine">${esc(arData() ? sc.terms_ar : sc.terms_en)}</p>`;
  return h + `</section>`;
}

// Plan item 27: the text as pasted, each citation marked with an icon and a word (never colour alone).
const TIER_ICON = { documented: "✓", supported: "✓", not_supported: "✕", verify: "!", refer: "؟" };
function tierClass(c) {
  const fab = ((c.hadith || {}).fabricated_by || []).length > 0;
  return { documented: "ok", supported: "ok", not_supported: fab ? "bad" : "warn", verify: "warn", refer: "warn" }[c.tier] || "";
}
function renderAnnotated(text, cits) {
  if (!text || !cits.length) return "";
  let h = "", at = 0;
  const sp = (c) => c.quote_span || c.span;
  for (const c of [...cits].filter(sp).sort((a, b) => sp(a)[0] - sp(b)[0])) {
    const [s, e] = sp(c);
    if (s < at || e > text.length) continue;
    h += esc(text.slice(at, s));
    h += `<a class="cite-mark ${tierClass(c)}" href="#c-${c.id}" data-c="${c.id}"><span class="cite-badge" aria-hidden="true">${TIER_ICON[c.tier] || ""} ${esc(num(c.id))}</span>${esc(text.slice(s, e))}<span class="cite-word">${esc(t().tierShort[c.tier] || "")}</span></a>`;
    at = e;
  }
  h += esc(text.slice(at));
  return `<details class="annot" open><summary>${esc(t().textTitle)}</summary><p class="fine">${esc(t().textNote)}</p><div class="annot-text" dir="auto">${h}</div></details>`;
}

function render(r) {
  $("report").hidden = false;
  if (r.summary.total) {
    const dr = r.display_rules || {};
    const rules = r.summary.hadith ? `<span class="fine rules-note">${esc(dr.status === "signed" ? t().rulesSigned(dr.reviewed_by, dr.reviewed_on) : t().rulesDraft)}</span>` : "";
    $("summary").innerHTML = t().summary(r.summary, (x) => esc(num(x))) + rules;
  }
  else $("summary").textContent = r.unsupported_language ? t().unsupported : r.asked_about === "other" ? t().outOfScope : t().none;
  if (r.summary.total && r.unsupported_language) $("summary").innerHTML += `<span class="fine rules-note">${esc(t().unsupportedPart)}</span>`;
  if (r.disclaimer) $("disclaimer").textContent = r.disclaimer[lang] || r.disclaimer.ar;
  const day = new Date().toLocaleDateString(({ ar: "ar-SA-u-ca-islamic-umalqura", ur: "ur-PK-u-ca-islamic-umalqura", en: "en-GB" }[lang] || lang), { year: "numeric", month: "long", day: "numeric" });
  $("report-meta").textContent = t().meta(day, (r.versions || {}).app || "—");
  const md = r.model || {};
  $("summary").innerHTML += `<span class="fine rules-note">${esc(md.used ? t().modelUsed(num(md.seconds), (md.answered_by || []).join("، ")) : t().modelNotUsed)}</span>`;
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
      h = `<p>${esc(r.level_d.form === "general" ? t().leveldGeneralFound : t().leveldFound)}</p>` + r.level_d.fatwas.scholars.map(renderScholarFatwas).join("");
    } else {
      const refs = (r.level_d.references || []).map((x) =>
        `<li><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(arData() ? x.ar : x.en)}</a></li>`).join("");
      h = `<p>${esc(r.level_d.form === "general" ? t().leveldGeneral : t().leveld)}</p>` + (refs ? `<ul class="refs">${refs}</ul>` : "");
    }
    if (r.level_d.search_by_model) h += `<p class="fine">${esc(t().searchedAs(r.level_d.search_by_model))}</p>`;
    if (r.level_d.form === "ruling_in_answer") h = `<p class="line warn">${esc(t().leveldRuling)}</p>` + h;
    const fa = r.level_d.answer;
    if (fa) h = `<section class="fatwa-answer${fa.same_question ? "" : " near"}"><h3 class="fatwas-h">${esc(fa.same_question ? t().fAnswerTitle : t().fNearTitle)}</h3>
      <blockquote lang="ar" dir="rtl">«${esc(fa.quote)}»</blockquote>
      <p class="fine">${esc(arData() ? fa.scholar_ar : fa.scholar_en)} · <a href="${esc(fa.url)}" target="_blank" rel="noopener"><bdi dir="rtl">${esc(fa.title)}</bdi></a>${fa.source ? " · " + esc(fa.source) : ""}</p>
      ${fa.same_question ? "" : `<p class="line warn">${esc(t().fNearNote)}</p>`}<p class="fine">${esc(t().fAnswerNote)}</p></section>` + h;
    ld.innerHTML = h + `<p class="body-ref">${esc(t().leveldBody(arData() ? b.ar : b.en))} <a href="${esc(b.url)}" target="_blank" rel="noopener">${esc(t().bodyLink)}</a></p>`;
  }
  $("annotated").innerHTML = renderAnnotated(lastText, r.citations);
  $("annotated").hidden = !r.citations.length;
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
    lastText = text;
    $("status").textContent = "";
    render(lastResult);
    saveHistory(text, deep, lastResult);
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
let modelOff = false;
async function health() {
  try {
    const h = await (await fetch("/api/health")).json();
    dorarDown = h.dorar_enabled && h.dorar_reachable === false;
    modelOff = !(h.model_ready || (h.models && h.models.fallback));
  } catch (e) { /* the check itself reports failures */ }
  showBanner();
}
function showBanner() {
  const b = $("banner");
  b.hidden = !dorarDown;
  if (dorarDown) b.textContent = t().dorarDown;
  // Plan item 21: the deep check is switched off, with its reason, while the model server is off.
  const d = $("deep");
  d.disabled = modelOff;
  if (modelOff) d.checked = false;
  $("deep-why").hidden = !modelOff;
  $("deep-why").textContent = modelOff ? t().modelOff : "";
}

$("go").addEventListener("click", check);
$("results").addEventListener("click", async (e) => {
  const b = e.target.closest("button.copy[data-copy]");
  if (!b) return;
  try { await navigator.clipboard.writeText(b.dataset.copy); } catch (err) {
    const ta = document.createElement("textarea"); ta.value = b.dataset.copy; document.body.append(ta); ta.select();
    try { document.execCommand("copy"); } catch (e2) { /* nothing more to try */ } ta.remove();
  }
  b.textContent = t().copied;
  setTimeout(() => { b.textContent = t().copy; }, 2000);
});
$("cases-list").addEventListener("click", (e) => {
  const b = e.target.closest("button.case");
  if (!b) return;
  $("text").value = CASES[+b.dataset.case].text;
  $("text").dispatchEvent(new Event("input"));
  check();
});
$("annotated").addEventListener("click", (e) => {
  const a = e.target.closest(".cite-mark");
  if (!a) return;
  e.preventDefault();
  const el = $("c-" + a.dataset.c);
  el.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
  el.focus({ preventScroll: true });
});
$("text").addEventListener("input", updateCounter);
$("text").addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) check(); });
document.querySelectorAll("[data-sample]").forEach((b) => b.addEventListener("click", () => {
  $("text").value = SAMPLES[b.dataset.sample];
  $("text").dispatchEvent(new Event("input"));
  $("text").focus();
}));
$("lang").addEventListener("change", () => {
  lang = LANGS.includes($("lang").value) ? $("lang").value : "ar";
  try { localStorage.setItem("tathabbut-lang", lang); } catch (e) { /* storage may be blocked */ }
  applyLang();
});
try { const saved = localStorage.getItem("tathabbut-lang"); if (LANGS.includes(saved)) lang = saved; } catch (e) { /* ignore */ }
// My checks: kept in this browser only (localStorage), never sent anywhere; the page works without it.
const HKEY = "tathabbut-history", HMAX = 12;
function readHistory() {
  try { const h = JSON.parse(localStorage.getItem(HKEY) || "[]"); return Array.isArray(h) ? h : []; } catch (e) { return []; }
}
function saveHistory(text, deep, result) {
  const h = readHistory().filter((x) => x.text !== text);
  h.unshift({ at: new Date().toISOString(), text, deep, result });
  for (let n = Math.min(h.length, HMAX); n > 0; n--) {  // drop the oldest if the browser's quota is reached
    try { localStorage.setItem(HKEY, JSON.stringify(h.slice(0, n))); break; } catch (e) { if (n === 1) return; }
  }
  showHistory();
}
function showHistory() {
  const h = readHistory(), box = $("history");
  if (!box) return;
  box.hidden = !h.length;
  const day = (iso) => new Date(iso).toLocaleDateString(({ ar: "ar-SA-u-ca-islamic-umalqura", ur: "ur-PK-u-ca-islamic-umalqura", en: "en-GB" }[lang] || lang), { day: "numeric", month: "long" });
  $("history-list").innerHTML = h.map((x, i) => {
    const s = (x.result && x.result.summary) || {};
    return `<li><button type="button" class="linkish case" data-h="${i}">${esc(x.text.slice(0, 90))}${x.text.length > 90 ? "…" : ""}</button>
      <span class="fine">${esc(day(x.at))} · ${esc(t().historyCount(num(s.total || 0)))}</span></li>`;
  }).join("");
}
$("history-list").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-h]");
  if (!b) return;
  const x = readHistory()[+b.dataset.h];
  if (!x) return;
  $("text").value = x.text; $("text").dispatchEvent(new Event("input"));
  lastText = x.text; lastResult = x.result;
  render(lastResult);
  $("report").scrollIntoView({ behavior: "smooth", block: "start" });
});
$("history-clear").addEventListener("click", () => {
  try { localStorage.removeItem(HKEY); } catch (e) { /* storage may be blocked */ }
  showHistory();
});

applyLang();
health();
showHistory();
// A link from the archive (/?q=...) opens with its text and checks it.
try {
  const q = new URLSearchParams(location.search).get("q");
  if (q) { $("text").value = q.slice(0, 8000); $("text").dispatchEvent(new Event("input")); check(); }
} catch (e) { /* ignore */ }
