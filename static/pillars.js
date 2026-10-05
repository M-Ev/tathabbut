// أركان الإسلام: the five pillars, then wudu and the prayer step by step. Every ruling sentence on this page is
// quoted word for word from Shaykh Ibn Baz's official site (data/pillars_sources.json, checked by
// tests/test_pillars.py); the verses come from the Mushaf file and their meanings from the approved translations
// (/api/pillars); the hadith was checked with Tathabbut itself. Nothing here is the tool's own ruling.
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const LANGS = ["ar", "en", "ur", "id", "bn", "tr", "fr", "es", "hi", "zh", "ja"];
let lang = "ar";
try { const s = localStorage.getItem("tathabbut-lang"); if (LANGS.includes(s)) lang = s; } catch (e) { /* ignore */ }
const RTL = ["ar", "ur"];
const num = (n) => (lang === "ar" ? String(n).replace(/\d/g, (d) => "٠١٢٣٤٥٦٧٨٩"[d]) : String(n));

const SRC = {
  salah: { url: "https://binbaz.org.sa/fatwas/10166", title: "صفة صلاة النبي ﷺ من التكبير إلى التسليم" },
  salah_rest: { url: "https://binbaz.org.sa/fatwas/6122", title: "تتمة صفة صلاة النبي صلى الله عليه وسلم" },
  wudu: { url: "https://binbaz.org.sa/fatwas/18835", title: "صفة الوضوء الشرعي وما يقال عقبه" },
  wudu_prophet: { url: "https://binbaz.org.sa/fatwas/10255", title: "صفة وضوء النبي صلى الله عليه وسلم" },
  raise_hands: { url: "https://binbaz.org.sa/fatwas/4103", title: "صفة رفع اليدين عند التكبير في الصلاة" },
  hands_chest: { url: "https://binbaz.org.sa/fatwas/12198", title: "السنة في وضع اليدين في الصلاة" },
  no_fatiha: { url: "https://binbaz.org.sa/fatwas/20532", title: "حكم صلاة من لا يحسن الفاتحة" },
  no_fatiha_2: { url: "https://binbaz.org.sa/fatwas/3711", title: "ما حكم صلاة من لا يحسن قراءة الفاتحة؟" },
};

// The treatise «كيفية صلاة النبي ﷺ» in the official translations published on the Shaykh's site.
const TREATISE = {
  ar: ["العربية", "https://binbaz.org.sa/books/369/%D9%83%D9%8A%D9%81%D9%8A%D8%A9-%D8%B5%D9%84%D8%A7%D8%A9-%D8%A7%D9%84%D9%86%D8%A8%D9%8A-%D8%B5%D9%84%D9%89-%D8%A7%D9%84%D9%84%D9%87-%D8%B9%D9%84%D9%8A%D9%87-%D9%88%D8%B3%D9%84%D9%85"],
  en: ["English", "https://binbaz.org.sa/books/347"], ur: ["اردو", "https://binbaz.org.sa/books/344"],
  es: ["Español", "https://binbaz.org.sa/books/345"], bn: ["বাংলা", "https://binbaz.org.sa/books/352"],
  tr: ["Türkçe", "https://binbaz.org.sa/books/355"], zh: ["中文", "https://binbaz.org.sa/books/359"],
  fr: ["Français", "https://binbaz.org.sa/books/361"], hi: ["हिन्दी", "https://binbaz.org.sa/books/364"],
  ja: ["日本語", "https://binbaz.org.sa/books/365"],
};

const HADITH = {
  text: "بُنيَ الإسلامُ على خَمسٍ : شَهادةِ أن لا إلَهَ إلَّا اللهُ وأنَّ مُحَمَّدًا رَسولُ اللهِ، وإقامِ الصَّلاةِ، وإيتاءِ الزَّكاةِ، والحَجِّ، وصَومِ رَمَضانَ.",
  where: [["صحيح البخاري", "Sahih al-Bukhari", "8", "https://www.dorar.net/h/JDqeTpYd"], ["صحيح مسلم", "Sahih Muslim", "16", "https://www.dorar.net/h/TCubdkk0"]],
};

const PILLARS = [
  { key: "shahada", ar: "الشهادتان", en: "The two testimonies of faith", ask: "ما معنى شهادة أن لا إله إلا الله؟" },
  { key: "salah", ar: "إقام الصلاة", en: "Establishing the prayer", jump: "#salah" },
  { key: "zakah", ar: "إيتاء الزكاة", en: "Giving zakah", ask: "ما شروط وجوب الزكاة؟" },
  { key: "sawm", ar: "صوم رمضان", en: "Fasting Ramadan", ask: "ما مفسدات الصيام؟" },
  { key: "hajj", ar: "حج البيت لمن استطاع", en: "Pilgrimage to the House, for whoever is able", ask: "ما شروط وجوب الحج؟" },
];

const WUDU = [
  { part: "none", ar: "التسمية", en: "Saying the name of Allah", say: "بسم الله", tr: "Bismillāh",
    quotes: [{ src: "wudu", q: "فالسنة في الوضوء إذا قام إليه الإنسان يسمي الله عند بدئه" }] },
  { part: "hands", ar: "غسل الكفين", en: "Washing the hands", n: 3,
    quotes: [{ src: "wudu", q: "ثم يغسل كفيه ثلاث مرات" }] },
  { part: "mouth", ar: "المضمضة والاستنشاق", en: "Rinsing the mouth and the nose", n: 3,
    quotes: [{ src: "wudu", q: "ثم يتمضمض ويستنشق ثلاثًا بثلاث غرفات" }] },
  { part: "face", ar: "غسل الوجه", en: "Washing the face", n: 3,
    quotes: [{ src: "wudu_prophet", q: "ويغسل وجهه عمومًا من منابت شعر الرأس إلى الذقن طولًا، وعرضًا إلى فروع الأذنين" }] },
  { part: "arms", ar: "غسل اليدين مع المرفقين", en: "Washing the arms up to and including the elbows", n: 3,
    quotes: [{ src: "wudu", q: "ثم يغسل ذراعيه ثلاثًا مع المرفقين" }] },
  { part: "head", ar: "مسح الرأس والأذنين", en: "Wiping the head and the ears", n: 1,
    quotes: [{ src: "wudu_prophet", q: "يمسحه مرة واحدة بيديه مع الأذنين، والأفضل أن يبدأ بالمقدم ثم يمر يديه إلى قفاه" },
      { src: "wudu", q: "ويدخل إصبعه في أذنيه ويمسح بإبهاميه ظاهر أذنيه" }] },
  { part: "feet", ar: "غسل الرجلين مع الكعبين", en: "Washing the feet up to and including the ankles", n: 3,
    quotes: [{ src: "wudu", q: "ثم يغسل رجليه مع الكعبين ثلاث مرات" }] },
  { part: "none", ar: "الذكر بعد الوضوء", en: "What is said after wudu",
    say: "أشهد أن لا إله إلا الله وحده لا شريك له، وأشهد أن محمدًا عبده ورسوله، اللهم اجعلني من التوابين واجعلني من المتطهرين",
    tr: "Ashhadu an lā ilāha illa-llāhu waḥdahu lā sharīka lah, wa ashhadu anna Muḥammadan ʿabduhu wa rasūluh. Allāhumma-jʿalnī mina-t-tawwābīna wa-jʿalnī mina-l-mutaṭahhirīn",
    quotes: [{ src: "wudu", q: "وبعد الفراغ يقول: أشهد أن لا إله إلا الله وحده لا شريك له، وأشهد أن محمدًا عبده ورسوله، اللهم اجعلني من التوابين واجعلني من المتطهرين" }] },
];
const WUDU_ONCE = { src: "wudu_prophet", q: "فالمرة الواحدة هذه فريضة، والمرة الثانية سنة، والثلاث هي الكمال" };

const TASHAHHUD = "التحيات لله، والصلوات والطيبات، السلام عليك أيها النبي ورحمة الله وبركاته، السلام علينا وعلى عباد الله الصالحين، أشهد أن لا إله إلا الله وأشهد أن محمداً عبده ورسوله";
const TASHAHHUD_TR = "At-taḥiyyātu lillāhi wa-ṣ-ṣalawātu wa-ṭ-ṭayyibāt, as-salāmu ʿalayka ayyuha-n-nabiyyu wa raḥmatu-llāhi wa barakātuh, as-salāmu ʿalaynā wa ʿalā ʿibādi-llāhi-ṣ-ṣāliḥīn, ashhadu an lā ilāha illa-llāh, wa ashhadu anna Muḥammadan ʿabduhu wa rasūluh";
const IBRAHIMIYYA = "اللهم صل على محمد وعلى آل محمد كما صليت على إبراهيم وعلى آل إبراهيم إنك حميد مجيد، اللهم بارك على محمد وعلى آل محمد كما باركت على إبراهيم وعلى آل إبراهيم إنك حميد مجيد";
const IBRAHIMIYYA_TR = "Allāhumma ṣalli ʿalā Muḥammadin wa ʿalā āli Muḥammad, kamā ṣallayta ʿalā Ibrāhīma wa ʿalā āli Ibrāhīm, innaka ḥamīdun majīd. Allāhumma bārik ʿalā Muḥammadin wa ʿalā āli Muḥammad, kamā bārakta ʿalā Ibrāhīma wa ʿalā āli Ibrāhīm, innaka ḥamīdun majīd";

const SALAH = [
  { pose: "takbir", ar: "تكبيرة الإحرام", en: "The opening takbir", say: "الله أكبر", tr: "Allāhu akbar",
    quotes: [{ src: "salah", q: "يبدؤها بالتكبير: الله أكبر" },
      { src: "raise_hands", q: "السنة للمصلي أن يرفع يديه حذاء منكبيه أو حذاء أذنيه عند تكبيرة الإحرام" }] },
  { pose: "qiyam", ar: "وضع اليدين على الصدر", en: "Placing the hands on the chest",
    quotes: [{ src: "salah_rest", q: "يضع اليمنى كف اليمنى على كف اليسرى على صدره" },
      { src: "hands_chest", q: "السنة في وضع اليدين في الصلاة على الصدر، هذا هو المحفوظ عن النبي ﷺ" }] },
  { pose: "qiyam", ar: "دعاء الاستفتاح", en: "The opening supplication",
    say: "سبحانك اللهم وبحمدك، وتبارك اسمك، وتعالى جدك، ولا إله غيرك",
    tr: "Subḥānaka-llāhumma wa biḥamdika, wa tabāraka-smuka, wa taʿālā jadduka, wa lā ilāha ghayruk",
    quotes: [{ src: "salah", q: "وإن استفتح بالحديث الآخر: سبحانك اللهم وبحمدك، وتبارك اسمك، وتعالى جدك، ولا إله غيرك فحسن، كله طيب" }] },
  { pose: "qiyam", ar: "الاستعاذة والبسملة والفاتحة", en: "Seeking refuge, the basmala, and al-Fatiha", fatiha: true,
    say: "أعوذ بالله من الشيطان الرجيم، بسم الله الرحمن الرحيم", tr: "Aʿūdhu billāhi mina-sh-shayṭāni-r-rajīm. Bismi-llāhi-r-raḥmāni-r-raḥīm",
    quotes: [{ src: "salah", q: "ثم يقول: أعوذ بالله من الشيطان الرجيم، بسم الله الرحمن الرحيم، ثم يقرأ الحمد، الفاتحة يقرؤها قراءة مرتلة ومطمئنة، يعطي الحروف حقها" }] },
  { pose: "qiyam", ar: "قراءة ما تيسر بعد الفاتحة", en: "Reciting what is easy after al-Fatiha",
    quotes: [{ src: "salah", q: "ثم يقرأ ما تيسر من السور، أو الآيات" }] },
  { pose: "ruku", ar: "الركوع", en: "Bowing (ruku')", say: "سبحان ربي العظيم", tr: "Subḥāna rabbiya-l-ʿaẓīm",
    quotes: [{ src: "salah_rest", q: "يرفع يديه إلى حذو منكبيه أو إلى حيال أذنيه ويكبر قائلاً: الله أكبر، ثم يسوي ظهره -كما تقدم- ويجعل يديه على ركبتيه مفرجتي الأصابع ويقول: سبحان ربي العظيم" },
      { src: "salah_rest", q: "وهذا يستوي فيه المرأة والرجل جميعاً" }] },
  { pose: "itidal", ar: "الرفع من الركوع", en: "Rising from bowing",
    say: "سمع الله لمن حمده، ربنا ولك الحمد، حمدًا كثيرًا طيبًا مباركًا فيه، ملء السماوات، وملء الأرض، وملء ما بينهما، وملء ما شئت من شيء بعد",
    tr: "Samiʿa-llāhu liman ḥamidah. Rabbanā wa laka-l-ḥamd, ḥamdan kathīran ṭayyiban mubārakan fīh, mil'a-s-samāwāti wa mil'a-l-arḍi wa mil'a mā baynahumā wa mil'a mā shi'ta min shay'in baʿd",
    quotes: [{ src: "salah", q: "ثم يرفع رأسه قائلًا: (سمع الله لمن حمده) إذا كان إمامًا، أو منفردًا، وإن كان مأمومًا يرفع يقول: (ربنا ولك الحمد)" },
      { src: "salah_rest", q: "والواجب الاعتدال في هذا الركن، لا يعجل" }] },
  { pose: "sujud", ar: "السجود", en: "Prostration (sujud)", say: "سبحان ربي الأعلى", tr: "Subḥāna rabbiya-l-aʿlā",
    quotes: [{ src: "salah_rest", q: "ينحط ساجداً قائلاً: (الله أكبر) من دون رفع اليدين" },
      { src: "salah", q: "ثم يسجد، ويعتدل في السجود على أعضائه السبعة: أطراف قدميه وركبتيه وكفيه ووجهه، يجعل جبهته وأنفه على الأرض" },
      { src: "salah", q: "أقرب ما يكون العبد من ربه وهو ساجد؛ فأكثروا الدعاء" }] },
  { pose: "jalsa", ar: "الجلوس بين السجدتين", en: "Sitting between the two prostrations", say: "رب اغفر لي، رب اغفر لي", tr: "Rabbi-ghfir lī, rabbi-ghfir lī",
    quotes: [{ src: "salah", q: "بين السجدتين يطمئن، ويجلس على رجله اليسرى، يفرشها، ويجلس عليها، وينصب اليمنى إذا استطاع ذلك" }] },
  { pose: "sujud", ar: "السجدة الثانية", en: "The second prostration", say: "سبحان ربي الأعلى", tr: "Subḥāna rabbiya-l-aʿlā",
    quotes: [{ src: "salah", q: "ثم يسجد الثانية مثل الأولى، يطمئن فيها، ويقول فيها مثلما قال في الأولى" }] },
  { pose: "qiyam", ar: "القيام إلى الركعة الثانية", en: "Standing for the second rak'ah", say: "الله أكبر", tr: "Allāhu akbar",
    quotes: [{ src: "salah_rest", q: "ثم يفعل في الثانية كما فعل في الأولى" }] },
  { pose: "tashahhud", ar: "التشهد الأول", en: "The first tashahhud", say: TASHAHHUD, tr: TASHAHHUD_TR,
    quotes: [{ src: "salah", q: "وفي آخرها بعد الثنتين يجلس للتحيات يقرأ التحيات إلى قوله: (أشهد أن لا إله إلا الله، وأشهد أن محمدًا عبده ورسوله) ثم ينهض إلى الثالثة" }] },
  { pose: "qiyam", ar: "الركعة الثالثة والرابعة", en: "The third and fourth rak'ahs",
    quotes: [{ src: "salah", q: "ثم يقرأ في الثالثة الحمد فقط" },
      { src: "raise_hands", q: "وعند القيام من التشهد الأول إلى الثالثة" }] },
  { pose: "tashahhud", ar: "التشهد الأخير والصلاة على النبي ﷺ", en: "The final tashahhud and the prayer upon the Prophet ﷺ",
    say: TASHAHHUD + "، " + IBRAHIMIYYA, tr: TASHAHHUD_TR + ". " + IBRAHIMIYYA_TR,
    quotes: [{ src: "salah", q: "ثم يجلس بعد الثالثة في المغرب، وبعد الرابعة في الظهر والعصر والعشاء، وبعد الثانية في الفجر، يقرأ التحيات ويصلي على النبي ﷺ" },
      { src: "salah_rest", q: "اللهم إني أعوذ بك من عذاب جهنم، ومن عذاب القبر، ومن فتنة المحيا والممات، ومن فتنة المسيح الدجال" }] },
  { pose: "salamR", ar: "التسليم عن اليمين", en: "The salam to the right", say: "السلام عليكم ورحمة الله", tr: "As-salāmu ʿalaykum wa raḥmatu-llāh",
    quotes: [{ src: "salah", q: "ثم يسلم تسليمتين: (السلام عليكم ورحمة الله) عن يمينه (السلام عليكم ورحمة الله) عن يساره، هذا تمام الصلاة، يفتحها بالتكبير، ويختمها بالتسليم" }] },
  { pose: "salamL", ar: "التسليم عن اليسار", en: "The salam to the left", say: "السلام عليكم ورحمة الله", tr: "As-salāmu ʿalaykum wa raḥmatu-llāh", quotes: [] },
];

const RAKAT = [["الفجر", "Fajr", 2], ["الظهر", "Dhuhr", 4], ["العصر", "Asr", 4], ["المغرب", "Maghrib", 3], ["العشاء", "Isha", 4]];
const RAKAT_Q = { src: "salah", q: "ثم يجلس بعد الثالثة في المغرب، وبعد الرابعة في الظهر والعصر والعشاء، وبعد الثانية في الفجر" };

const AJAM = [
  { src: "no_fatiha", q: "الواجب على كل مسلم ومسلمة تعلم الفاتحة، حتى يقرأها في صلاته" },
  { src: "no_fatiha", q: "فإن عجز المسلم عن تعلم الفاتحة وحان وقت الصلاة قبل أن يتعلمها، قام مقامها: سبحان الله، والحمد لله، ولا إله إلا الله، والله أكبر، ولا حول ولا قوة إلا بالله العلي العظيم" },
  { src: "no_fatiha_2", q: "علِّموه، يتعلَّم، وإذا عجز فصلاته صحيحة" },
];
const AJAM_TR = "Subḥāna-llāh, wa-l-ḥamdu lillāh, wa lā ilāha illa-llāh, wa-llāhu akbar, wa lā ḥawla wa lā quwwata illā billāhi-l-ʿaliyyi-l-ʿaẓīm";
const FATIHA_TR = "Bismi-llāhi-r-raḥmāni-r-raḥīm. Al-ḥamdu lillāhi rabbi-l-ʿālamīn. Ar-raḥmāni-r-raḥīm. Māliki yawmi-d-dīn. Iyyāka naʿbudu wa iyyāka nastaʿīn. Ihdina-ṣ-ṣirāṭa-l-mustaqīm. Ṣirāṭa-lladhīna anʿamta ʿalayhim, ghayri-l-maghḍūbi ʿalayhim wa la-ḍ-ḍāllīn. Āmīn";

const T = {
  ar: {
    title: "أركان الإسلام", tagline: "الأركان الخمسة، ثم الوضوء والصلاة خطوة خطوة: من التكبير إلى التسليم",
    jPillars: "الأركان الخمسة", jWudu: "الوضوء", jSalah: "الصلاة", jAjam: "لغير العرب",
    hPillars: "الأركان الخمسة", hWudu: "الوضوء قبل الصلاة", hSalah: "صفة الصلاة من التكبير إلى التسليم",
    hAjam: "هل يقولها غير العربي بالعربية؟", hSources: "المصادر",
    hadithBy: (w) => `رواه ${w}، وتحقّق منه تثبّت في الموسوعة الحديثية`, and: " و",
    verse: "الآية من المصحف", askIt: "اسأل الثقات عن أحكامه", howTo: "صفة الوضوء والصلاة ↓",
    wuduLead: "كما وصفه سماحة الشيخ عبدالعزيز بن باز رحمه الله، والكلام تحت كل خطوة منقول بنصه من موقعه الرسمي. اضغط «تشغيل» لترى الخطوات متتابعة، أو اختر خطوة.",
    salahLead: "صلاة من أربع ركعات كالظهر، كما وصفها سماحة الشيخ ابن باز رحمه الله بنصه. اضغط «تشغيل» لترى الصلاة تتحرك من التكبير إلى التسليم.",
    rakatT: "عدد الركعات", times: (n) => `${num(n)} مرات`, once: "مرة واحدة", say: "يقول:", tr: "النطق بالحروف اللاتينية",
    fatiha: "سورة الفاتحة من المصحف", amin: "ثم يقول: آمين", meaning: "معنى الآيات",
    from: "من فتوى:", play: "▶ تشغيل", pause: "❚❚ إيقاف", prev: "السابق", next: "التالي",
    ajamLead: "ذكر سماحة الشيخ ابن باز رحمه الله أن الواجب تعلّم الفاتحة ليقرأها في صلاته، ومن عجز عنها حتى حضرت الصلاة قال بدلها ذكرًا علّمه النبي ﷺ:",
    ajamHelp: "وللتعلّم: تحت كل خطوة نطقها بالحروف اللاتينية، ورسالة الشيخ «كيفية صلاة النبي ﷺ» مترجمة ترجمة رسمية في موقعه:",
    review: "الأحكام في هذه الصفحة منقولة بنصها من كلام سماحة الشيخ ابن باز رحمه الله مع رابط كل فتوى؛ والرسوم توضيح للهيئة لا يُستدل بها، والنطق بالحروف اللاتينية تقريب للتعلّم والعبرة باللفظ العربي. لم تراجع المختصة الشرعية في الفريق هذه الصفحة بعد.",
    footer: "فريق قيد الأوابد · تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي",
    credit: "المصادر: مصحف مجمع الملك فهد، والموسوعة الحديثية في الدرر السنية، وموقع سماحة الشيخ عبدالعزيز بن باز رحمه الله.",
  },
  en: {
    title: "The pillars of Islam", tagline: "The five pillars, then wudu and the prayer step by step, from the takbir to the salam",
    jPillars: "The five pillars", jWudu: "Wudu", jSalah: "Prayer", jAjam: "For non-Arabs",
    hPillars: "The five pillars", hWudu: "Wudu before the prayer", hSalah: "The prayer from the takbir to the salam",
    hAjam: "Does a non-Arab say these words in Arabic?", hSources: "Sources",
    hadithBy: (w) => `Narrated by ${w}; checked by Tathabbut in Dorar's hadith encyclopedia`, and: " and ",
    verse: "The verse from the Mushaf", askIt: "Ask the trusted about its rulings", howTo: "How to make wudu and pray ↓",
    wuduLead: "As described by Shaykh Abd al-Aziz ibn Baz (may Allah have mercy on him); the Arabic under each step is quoted word for word from his official site. Press Play to watch the steps, or choose one.",
    salahLead: "A four-rak'ah prayer such as Dhuhr, as Shaykh Ibn Baz described it, quoted verbatim. Press Play to watch the prayer move from the takbir to the salam.",
    rakatT: "Number of rak'ahs", times: (n) => `${n} times`, once: "once", say: "Say:", tr: "Pronunciation in Latin letters",
    fatiha: "Surah al-Fatiha from the Mushaf", amin: "Then say: Āmīn", meaning: "Meaning of the verses",
    from: "From the fatwa:", play: "▶ Play", pause: "❚❚ Pause", prev: "Back", next: "Next",
    ajamLead: "Shaykh Ibn Baz said that one must learn al-Fatiha to recite it in prayer, and that whoever cannot yet recite it when the prayer is due says, in its place, words of remembrance the Prophet ﷺ taught:",
    ajamHelp: "To learn: each step shows its pronunciation in Latin letters, and the Shaykh's treatise on the Prophet's prayer is on his site in official translations:",
    review: "The rulings on this page are quoted word for word from Shaykh Ibn Baz, with a link to each fatwa. The drawings show the positions and are not evidence; the Latin-letter pronunciation is a learning aid, and the Arabic is what counts. The team's Sharia reviewer has not yet reviewed this page.",
    footer: "Team Qayd al-Awabid · AI Challenge: Serving Islamic Content",
    credit: "Sources: the King Fahd Complex Mushaf, Dorar's hadith encyclopedia, and the official site of Shaykh Abd al-Aziz ibn Baz.",
  },
};
const NAV = { navPillars: { ar: "أركان الإسلام", en: "Pillars of Islam", ur: "ارکانِ اسلام", id: "Rukun Islam", bn: "ইসলামের স্তম্ভ", tr: "İslam'ın şartları", fr: "Piliers de l'islam", es: "Pilares del islam", hi: "इस्लाम के स्तंभ", zh: "伊斯兰五功", ja: "イスラームの五行" } };
// Nine more languages (static/pillars-i18n.js): the page's own words and the step names; anything missing reads English.
if (typeof PL_I18N !== "undefined") {
  for (const [k, pack] of Object.entries(PL_I18N)) {
    const main = (typeof T_EXTRA !== "undefined" && T_EXTRA[k]) || (typeof T_MORE !== "undefined" && T_MORE[k]) || {};
    T[k] = { ...T.en, ...pack.ui, footer: main.footer || T.en.footer, credit: T.en.credit };
    PILLARS.forEach((x, i) => { if (pack.pillars[i]) x[k] = pack.pillars[i]; });
    WUDU.forEach((x, i) => { if (pack.wudu[i]) x[k] = pack.wudu[i]; });
    SALAH.forEach((x, i) => { if (pack.salah[i]) x[k] = pack.salah[i]; });
    RAKAT.forEach((x, i) => { if (pack.rakat[i]) (x.names = x.names || {})[k] = pack.rakat[i]; });
  }
}
const t = () => T[lang] || T.en;
const navWord = (k) => {
  if (k === "navPillars") return NAV.navPillars[lang];
  if (k === "navAdhkar") return { ar: "الأذكار الموثّقة", en: "Verified adhkar", ur: "مستند اذکار", id: "Zikir terverifikasi", bn: "যাচাইকৃত যিকির", tr: "Doğrulanmış zikirler", fr: "Invocations vérifiées", es: "Adhkar verificados", hi: "प्रमाणित अज़कार", zh: "经核实的记念词", ja: "検証済みのズィクル" }[lang];
  const pack = lang === "ar" ? null : (typeof T_EXTRA !== "undefined" && T_EXTRA[lang]) || (typeof T_MORE !== "undefined" && T_MORE[lang]);
  return (pack && pack[k]) || { navCheck: { ar: "الفحص", en: "Check" }, navArchive: { ar: "الأرشيف", en: "Archive" }, navBot: { ar: "اسأل الثقات", en: "Ask the trusted" }, navDev: { ar: "للمطورين", en: "Developers" } }[k][lang === "ar" ? "ar" : "en"];
};
const name = (x) => x[lang] || x.en;

function quote(x) {
  const s = SRC[x.src];
  return `<figure class="pl-quote"><blockquote lang="ar" dir="rtl">«${esc(x.q)}»</blockquote><figcaption>${esc(t().from)} <a href="${esc(s.url)}" target="_blank" rel="noopener" lang="ar" dir="rtl">${esc(s.title)}</a></figcaption></figure>`;
}
const sayBlock = (s) => (s.say ? `<p class="pl-say"><span class="lbl">${esc(t().say)}</span><span lang="ar" dir="rtl">${esc(s.say)}</span></p>` : "")
  + (s.tr && lang !== "ar" ? `<p class="pl-tr"><span class="lbl">${esc(t().tr)}</span><span lang="ar-Latn" dir="ltr">${esc(s.tr)}</span></p>` : "");

let VERSES = null;
function verseBlock(v) {
  if (!v) return "";
  const text = v.ayat.map((a) => `${esc(a.text)} <span class="ayah-no">﴿${num(a.ayah)}﴾</span>`).join(" ");
  const tr = lang !== "ar" && v.translations[lang] ? `<p class="pl-meaning" dir="auto"><span class="lbl">${esc(t().meaning)}</span>${esc(v.translations[lang].text)} <span class="fine">(${esc(v.translations[lang].name)})</span></p>` : "";
  return `<p class="pl-verse quran" lang="ar" dir="rtl">${text}</p><p class="fine">[${esc(lang === "ar" ? v.surah_ar : v.surah_en)}: ${num(v.ayah_from)}${v.ayah_to !== v.ayah_from ? "–" + num(v.ayah_to) : ""}]</p>${tr}`;
}

function renderPillars() {
  const where = HADITH.where.map(([ar, en, n, url]) => `<a href="${url}" target="_blank" rel="noopener">${esc(lang === "ar" ? ar : en)} (${num(n)})</a>`).join(t().and);
  $("hadith").innerHTML = `<blockquote lang="ar" dir="rtl">«${esc(HADITH.text)}»</blockquote><figcaption>${t().hadithBy(where)}</figcaption>`;
  $("pillar-list").innerHTML = PILLARS.map((p, k) => `<li class="pillar">
      <span class="pillar-n" aria-hidden="true">${num(k + 1)}</span>
      <h3>${esc(name(p))}</h3>
      <details><summary>${esc(t().verse)}</summary>${verseBlock(VERSES && VERSES[p.key])}</details>
      ${p.jump ? `<a class="pillar-go" href="${p.jump}">${esc(t().howTo)}</a>` : `<a class="pillar-go" href="/?q=${encodeURIComponent(p.ask)}">${esc(t().askIt)}</a>`}
    </li>`).join("");
}

function stepCard(s, k, kind) {
  const count = s.n ? `<span class="pl-count">${esc(s.n === 1 ? t().once : t().times(s.n))}</span>` : "";
  const fig = kind === "wudu" ? FIG.wudu(s.part) : FIG.prayer(s.pose, RTL.includes(lang) || lang === "ar");
  const fat = s.fatiha && VERSES ? `<div class="pl-fatiha"><p class="lbl">${esc(t().fatiha)}</p>${verseBlock(VERSES.fatiha)}
      ${lang !== "ar" ? `<p class="pl-tr"><span class="lbl">${esc(t().tr)}</span><span dir="ltr">${esc(FATIHA_TR)}</span></p>` : ""}<p class="fine">${esc(t().amin)}</p></div>` : "";
  return `<li class="step" data-k="${k}">
      <button type="button" class="step-fig" aria-label="${esc(name(s))}">${fig.outerHTML}</button>
      <div class="step-body">
        <h3><span class="step-n">${num(k + 1)}</span>${esc(name(s))}${count}</h3>
        ${sayBlock(s)}${fat}${s.quotes.map(quote).join("")}
      </div></li>`;
}

function renderSteps(list, host, kind, playerHost, extra) {
  host.innerHTML = list.map((s, k) => stepCard(s, k, kind)).join("") + (extra || "");
  const steps = list.map((s) => ({ pose: s.pose, part: s.part, title: name(s), say: s.say && s.say.length < 60 ? s.say : "" }));
  const p = FIG.player(playerHost, steps, {
    kind, rtl: RTL.includes(lang) || lang === "ar", num,
    labels: { play: t().play, pause: t().pause, prev: t().prev, next: t().next },
    onStep: (k) => host.querySelectorAll(".step").forEach((el) => el.classList.toggle("is-on", Number(el.dataset.k) === k)),
  });
  host.querySelectorAll(".step-fig").forEach((b) => (b.onclick = () => { p.show(Number(b.closest(".step").dataset.k)); playerHost.scrollIntoView({ behavior: "smooth", block: "center" }); }));
}

function renderAjam() {
  const links = Object.entries(TREATISE).map(([k, [label, url]]) => `<li${k === lang ? ' class="is-mine"' : ""}><a href="${url}" target="_blank" rel="noopener">${esc(label)}</a></li>`).join("");
  $("ajam-body").innerHTML = `<p>${esc(t().ajamLead)}</p>${AJAM.map(quote).join("")}
    ${lang !== "ar" ? `<p class="pl-tr"><span class="lbl">${esc(t().tr)}</span><span dir="ltr">${esc(AJAM_TR)}</span></p>` : ""}
    <p>${esc(t().ajamHelp)}</p><ul class="treatise">${links}</ul>`;
}

function render() {
  document.documentElement.lang = lang;
  document.documentElement.dir = RTL.includes(lang) ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const k = el.dataset.i18n;
    el.textContent = k.startsWith("nav") ? navWord(k) : (t()[k] ?? el.textContent);
  });
  document.title = `${t().title} · ${lang === "ar" ? "تثبّت" : "Tathabbut"}`;
  renderPillars();
  $("wudu-lead").textContent = t().wuduLead;
  renderSteps(WUDU, $("wudu-steps"), "wudu", $("wudu-player"), `<li class="step-note">${quote(WUDU_ONCE)}</li>`);
  $("salah-lead").textContent = t().salahLead;
  $("rakat").innerHTML = `<p class="lbl">${esc(t().rakatT)}</p><ul>${RAKAT.map((r) => [r[0], (r.names && r.names[lang]) || r[1], r[2]]).map(([ar, en, n]) => `<li><b>${esc(lang === "ar" ? ar : en)}</b><span>${num(n)}</span></li>`).join("")}</ul>${quote(RAKAT_Q)}`;
  renderSteps(SALAH, $("salah-steps"), "salah", $("salah-player"));
  renderAjam();
  $("sources").innerHTML = Object.values(SRC).map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener" lang="ar">${esc(s.title)}</a> · ${lang === "ar" ? "موقع سماحة الشيخ ابن باز" : "binbaz.org.sa"}</li>`).join("")
    + `<li>${lang === "ar" ? "الآيات من مصحف مجمع الملك فهد، ومعانيها من الترجمات المعتمدة (quranpedia.net)" : "Verses from the King Fahd Complex Mushaf; meanings from the approved translations (quranpedia.net)"}</li>`;
  $("review-note").textContent = t().review;
}

$("lang").value = lang;
$("lang").addEventListener("change", (e) => { lang = e.target.value; try { localStorage.setItem("tathabbut-lang", lang); } catch (x) { /* ignore */ } render(); });
render();
fetch("/api/pillars").then((r) => r.json()).then((v) => { VERSES = v; render(); }).catch(() => { /* the page works without the verses */ });
