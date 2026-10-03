"""Hand-typed quotes in common (imla'i) spelling, written for this test and not produced by app/spelling.py,
so the second Mushaf index is checked against spelling the converter did not make (plan items 1-3)."""
import pytest

from app.quran import get_quran

COMMON = [
    ("قل هو الله أحد", "112:1"),
    ("الله الصمد", "112:2"),
    ("والعصر", "103:1"),
    ("إن الإنسان لفي خسر", "103:2"),
    ("والشمس وضحاها", "91:1"),
    ("والليل إذا يغشى", "92:1"),
    ("وإذ قال إبراهيم لأبيه آزر", "6:74"),
    ("يا أيها الذين آمنوا كتب عليكم الصيام", "2:183"),
    ("يا بني إسرائيل اذكروا نعمتي التي أنعمت عليكم", "2:40"),
    ("إن الله على كل شيء قدير", None),
    ("ولا تقربوا الزنى إنه كان فاحشة وساء سبيلا", "17:32"),
    ("وقضى ربك ألا تعبدوا إلا إياه وبالوالدين إحسانا", "17:23"),
    ("الذين آمنوا وتطمئن قلوبهم بذكر الله ألا بذكر الله تطمئن القلوب", "13:28"),
    ("فإن مع العسر يسرا", "94:5"),
    ("إن مع العسر يسرا", "94:6"),
    ("وما خلقت الجن والإنس إلا ليعبدون", "51:56"),
    ("هل أتاك حديث ضيف إبراهيم المكرمين", "51:24"),
    ("إنما يخشى الله من عباده العلماء", "35:28"),
    ("والسماوات مطويات بيمينه", "39:67"),
    ("وأقيموا الصلاة وآتوا الزكاة", None),
    ("ومن يتق الله يجعل له مخرجا", "65:2"),
    ("يا أيها الناس إنا خلقناكم من ذكر وأنثى", "49:13"),
    ("الرحمن علم القرآن", "55:1-2"),
    ("مالك يوم الدين", "1:4"),
    ("لا يكلف الله نفسا إلا وسعها", "2:286"),
]


@pytest.mark.parametrize("quote,ref", COMMON)
def test_common_spelling_matches_the_mushaf(quote, ref):
    m = get_quran().match_arabic(quote, marked=True)
    assert m.status == "exact", (quote, m.status, m.diff)
    if ref:
        assert m.ref == ref


ALEF = [
    ("قال هو الله أحد", "قال"),  # ﴿قُلۡ﴾
    ("قال أعوذ برب الفلق", "قال"),
    ("باسم الله الرحمن الرحيم", "باسم"),  # ﴿بِسۡمِ﴾
]


@pytest.mark.parametrize("quote,word", ALEF)
def test_extra_alef_is_a_difference(quote, word):
    m = get_quran().match_arabic(quote, marked=True)
    assert m.status == "differs"
    assert [d["quoted"] for d in m.diff if d["op"] != "equal"] == [word]


@pytest.mark.parametrize("text", ["النظافة من الإيمان", "الجنة تحت أقدام الأمهات", "العمل عبادة", "حب الوطن من الإيمان"])
def test_sayings_are_not_tied_to_an_ayah(text):
    assert get_quran().match_arabic(text, marked=True).status == "not_found"


def test_one_word_is_too_short_to_check():
    assert get_quran().match_arabic("فتثبتوا", marked=True).status == "too_short"
