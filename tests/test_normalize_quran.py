from app.normalize import normalize_ar, skeleton_ar
from app.quran import get_quran

Q = get_quran()


def test_uthmani_and_common_spelling_meet():
    assert skeleton_ar("ٱلسَّمَٰوَٰتِ") == skeleton_ar("السماوات")
    assert skeleton_ar("ٱلصَّلَوٰةَ") == skeleton_ar("الصلاة")
    assert normalize_ar("إِنَّ") == "ان"


def test_data_is_complete():
    assert len(Q.ayat) == 6236 and len(Q.surahs) == 114


def test_exact_quote_spanning_two_ayat():
    m = Q.match_arabic("ومن يتق الله يجعل له مخرجا ويرزقه من حيث لا يحتسب")
    assert m.status == "exact" and m.ref == "65:2-3"


def test_misquoted_ayah_shows_word_differences():
    m = Q.match_arabic("يا أيها الذين آمنوا إذا جاءكم فاسق بخبر فتبينوا")
    assert m.status == "differs" and m.surah == 49 and m.ayah_from == 6
    changed = [d for d in m.diff if d["op"] != "equal"]
    assert [d["quoted"] for d in changed] == ["إذا", "بخبر"]  # the user's own spelling


def test_hadith_is_not_taken_for_quran():
    for text in ["إنما الأعمال بالنيات وإنما لكل امرئ ما نوى", "الدين النصيحة لله ولرسوله", "طلب العلم فريضة على كل مسلم"]:
        assert Q.match_arabic(text).status == "not_found", text


def test_repeated_ayah_counts_occurrences():
    assert Q.match_arabic("فبأي آلاء ربكما تكذبان").occurrences == 31


def test_english_translation_match():
    m = Q.match_english("O you who have believed, if there comes to you a disobedient one with information, investigate")
    assert m.status == "exact" and m.ref == "49:6" and m.matched_translation == "saheeh"
    # Whatever the quote followed, the reader is shown the King Fahd Complex translation and quranpedia.net links.
    assert m.translation_en.startswith("6. O you who believe! If a Fâsiq")
    assert m.url == "https://quranpedia.net/ayahs/49/6"
    assert m.translation_url == "https://quranpedia.net/surah/1/49/book/1948"


def test_king_fahd_complex_translation_quote_match():
    m = Q.match_english("If a Fasiq comes to you with any news, verify it, lest you should harm people in ignorance")
    assert m.status == "exact" and m.ref == "49:6" and m.matched_translation == "hilali"


def test_surah_names():
    assert Q.surah_number("البقرة") == 2
    assert Q.surah_number("سورة الحجرات") == 49
    assert Q.surah_number("Al-Baqarah") == 2


def test_repeated_phrase_prefers_cited_place():
    m = Q.match_arabic("وأقيموا الصلاة وآتوا الزكاة", prefer=(2, 110))
    assert m.ref == "2:110" and m.occurrences > 1


def test_cited_place_accepted_for_near_identical_ayat():
    assert Q.match_english("Indeed, with hardship comes ease", prefer=(94, 5)).ref == "94:5"


def test_wrong_reference_reports_what_is_really_there():
    m = Q.match_arabic("يا أيها الذين آمنوا إن جاءكم فاسق بنبإ فتبينوا")
    Q.check_reference(m, 2, 6, "(البقرة: 6)")
    assert m.reference_ok is False
    assert m.cited["surah_name_ar"] == "البقرة" and m.cited["exists"] and skeleton_ar(m.cited["text"]).startswith(skeleton_ar("إن الذين كفروا"))
    m2 = Q.match_arabic("يا أيها الذين آمنوا إن جاءكم فاسق بنبإ فتبينوا")
    Q.check_reference(m2, 112, 9, "(الإخلاص: 9)")
    assert m2.cited["exists"] is False and m2.cited["surah_ayat"] == 4
