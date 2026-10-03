from app.extract import extract

TEXT = (
    "يقول الله تعالى: ﴿يَا أَيُّهَا الَّذِينَ آمَنُوا إِنْ جَاءَكُمْ فَاسِقٌ بِنَبَإٍ فَتَبَيَّنُوا﴾ (الحجرات: 6). "
    "وقال رسول الله ﷺ: «إنما الأعمال بالنيات». وفي الحديث: «اطلبوا العلم ولو في الصين». "
    "ومن يتق الله يجعل له مخرجا ويرزقه من حيث لا يحتسب، فلا تيأسوا. وقال تعالى: {وأقيموا الصلاة وآتوا الزكاة} (البقرة: 110).\n"
    'The Prophet (ﷺ) said: "The best of you are those who learn the Quran and teach it." '
    'Allah says in the Quran: "Indeed, with hardship comes ease" (94:6).'
)


def test_extracts_all_citations_in_order():
    got = [(c.type, c.lang, c.marker != "unmarked") for c in extract(TEXT)]
    assert got == [
        ("quran", "ar", True), ("hadith", "ar", True), ("hadith", "ar", True), ("quran", "ar", False),
        ("quran", "ar", True), ("hadith", "en", True), ("quran", "en", True),
    ]


def test_reads_references():
    cands = extract(TEXT)
    assert (cands[0].ref_surah, cands[0].ref_ayah) == (49, 6)
    assert (cands[4].ref_surah, cands[4].ref_ayah) == (2, 110)
    assert (cands[6].ref_surah, cands[6].ref_ayah) == (94, 6)


def test_plain_text_has_no_citations():
    assert extract("هذا نص عادي عن أهمية القراءة والتعلم في حياتنا اليومية.") == []


def test_longer_hadith_markers_are_not_cut():
    # «الحديث الشريف» must not leave «الشريف:» inside the quote; «قول النبي ﷺ» is a marker too.
    assert [c.quote for c in extract("وفي الحديث الشريف: «تبسمك في وجه أخيك لك صدقة»")] == ["تبسمك في وجه أخيك لك صدقة"]
    assert [(c.type, c.quote) for c in extract("ومن ذلك قول النبي ﷺ: «الدين النصيحة»")] == [("hadith", "الدين النصيحة")]


def test_follow_on_hadith_after_a_hadith_is_extracted():
    # Preflight B2: posts list hadith with a bare «وقال:» after the first one.
    cs = extract("وقال ﷺ: «إنما الأعمال بالنيات». وقال: «اطلبوا العلم ولو بالصين». وقال أيضًا: «الدين النصيحة»")
    assert [(c.type, c.quote) for c in cs] == [
        ("hadith", "إنما الأعمال بالنيات"), ("hadith", "اطلبوا العلم ولو بالصين"), ("hadith", "الدين النصيحة")]


def test_bare_qala_is_not_a_hadith_without_a_hadith_before_it():
    assert extract("قال محمد: «مرحبا بكم جميعا»") == []
    cs = extract("قال رسول الله ﷺ: «الدين النصيحة».\n\nوقال: «كلام عادي من شخص»")
    assert [c.quote for c in cs] == ["الدين النصيحة"]  # a new paragraph does not continue the list


def test_reference_without_colon_ends_the_quote():
    # Preflight B3: «(البقرة 200)» was swallowed into the ayah, so a real ayah was called not in the Mushaf.
    (c,) = extract("وقال تعالى: إن الله مع الصابرين (البقرة 200).")
    assert c.quote == "إن الله مع الصابرين" and (c.ref_surah, c.ref_ayah) == (2, 200)
