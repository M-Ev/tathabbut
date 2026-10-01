import json

from app.dorar import parse_api_json, parse_site_html
from app.pipeline import check_text
from app.scholars import find_scholar, is_hadith_level_grading

from .conftest import FIX, run


def test_parse_site_and_api():
    site = parse_site_html((FIX / "dorar_site.html").read_text(encoding="utf-8"))
    assert [h.mohdith for h in site] == ["البخاري", "الألباني", "مسلم", "يحيى بن معين"]
    assert site[0].mohdith_id == "256" and site[0].hadith_id == "abc123" and site[0].grade == "[صحيح]"
    api = parse_api_json((FIX / "dorar_api.json").read_text(encoding="utf-8"))
    assert [h.mohdith for h in api] == ["النووي", "الألباني"]
    assert api[1].grade == "صحيح" and api[1].book == "غاية المرام"


def test_narrator_statement_is_never_shown_as_hadith_grading():
    ibn_main = find_scholar("يحيى بن معين")
    assert not is_hadith_level_grading(ibn_main, "منكر الحديث")
    assert is_hadith_level_grading(ibn_main, "هذا حديث باطل")


def test_hadith_gradings_grouped_and_ordered(fake_dorar):
    fake_dorar({"إنما": "dorar_site.html"})
    r = run(check_text("قال رسول الله ﷺ: «إنما الأعمال بالنيات»"))
    c = r["citations"][0]
    assert c["status"] == "graded"
    groups = c["hadith"]["groups"]
    assert [g["group"] for g in groups] == ["imams", "editors"]
    assert [i["scholar_key"] for i in groups[0]["items"]] == ["bukhari", "muslim"]  # by death year
    assert groups[1]["items"][0]["scholar_key"] == "albani"
    assert c["hadith"]["hidden_narrator_statements"] == 1
    assert groups[0]["items"][0]["grade"] == "[صحيح]"  # verbatim


def test_fabricated_grading_is_flagged_with_who_said_it(fake_dorar):
    fake_dorar({"اطلبوا": "dorar_site_fabricated.html"})
    r = run(check_text("وفي الحديث: «اطلبوا العلم ولو في الصين»"))
    c = r["citations"][0]
    assert c["hadith"]["fabricated_by"] == ["الألباني"]
    assert r["summary"]["fabricated_flag"] == 1


def test_not_found_refers_to_specialist(fake_dorar):
    fake_dorar({})
    r = run(check_text("قال رسول الله ﷺ: «من قرأ هذا النص المخترع دخل الجنة بلا حساب»"))
    c = r["citations"][0]
    assert c["status"] == "not_found" and "مختص" in c["referral"]["ar"]


def test_wrong_quran_reference_is_flagged(fake_dorar):
    fake_dorar({})
    r = run(check_text("قال تعالى: ﴿وَأَقِيمُوا الصَّلَاةَ وَآتُوا الزَّكَاةَ﴾ (آل عمران: 5)"))
    c = r["citations"][0]
    assert c["quran"]["surah"] == 2 and "wrong_reference" in c["notes"]


def test_text_claimed_as_quran_but_not_in_mushaf(fake_dorar):
    fake_dorar({})
    r = run(check_text("قال الله تعالى: «النظافة من الإيمان والعمل عبادة»"))
    assert r["citations"][0]["status"] == "not_in_mushaf"


def test_english_hadith_without_model_is_referred(fake_dorar):
    fake_dorar({})
    r = run(check_text('The Prophet (pbuh) said: "Actions are judged by intentions."'))
    assert r["citations"][0]["status"] == "needs_model"


def test_english_hadith_with_model(fake_dorar, fake_llm):
    fake_dorar({"إنما": "dorar_site.html"})
    b = fake_llm([json.dumps({"arabic": "إنما الأعمال بالنيات"}), json.dumps({"match": 1})])
    r = run(check_text('The Prophet (pbuh) said: "Actions are judged by intentions."'))
    c = r["citations"][0]
    assert c["status"] == "graded" and "match_by_model" in c["notes"]
    assert len(b.calls) == 2


def test_model_citations_must_exist_in_text(fake_dorar, fake_llm):
    fake_dorar({})
    fake_llm([json.dumps([
        {"type": "hadith", "quote": "حديث مخترع لم يرد في النص أصلا"},
        {"type": "quran", "quote": "إن مع العسر يسرا"},
    ], ensure_ascii=False)])
    r = run(check_text("تذكّر أن إن مع العسر يسرا في كل حال.", deep=True))
    assert r["model"]["dropped_unverifiable"] == 1
    assert [c["quote"] for c in r["citations"]] == ["إن مع العسر يسرا"]
    assert r["citations"][0]["status"] == "verified"


def test_personal_fatwa_question_is_referred(fake_dorar):
    fake_dorar({})
    r = run(check_text("أنا في دولة أوروبية، هل يجوز لي أن أفعل كذا في زواجي؟"))
    assert r["level_d"]["detected"] and "alifta" in r["level_d"]["body"]["url"]


def test_every_citation_gets_one_evidence_tier(fake_dorar):
    fake_dorar({"إنما": "dorar_site.html"})
    r = run(check_text(
        "قال رسول الله ﷺ: «إنما الأعمال بالنيات». قال تعالى: ﴿يا أيها الذين آمنوا إذا جاءكم فاسق بخبر فتبينوا﴾. "
        "قال الله تعالى: «النظافة من الإيمان والعمل عبادة»"
    ))
    assert [c["tier"] for c in r["citations"]] == ["documented", "verify", "refer"]
    assert (r["summary"]["documented"], r["summary"]["verify"], r["summary"]["refer"]) == (1, 1, 1)
