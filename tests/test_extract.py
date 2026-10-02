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
