"""The scientific package's test cases (p. 6) and output standard (p. 5) that apply to a citation checker.

Each test names the package row it covers; docs/package-conformance.md lists every row, including those that do
not apply to a checker (the tool does not answer questions such as «لماذا يعبد المسلمون الكعبة؟»).
"""
import asyncio

import httpx

from app import dorar
from app.glossary import gloss_grade
from app.pipeline import check_text
from tests.conftest import dorar_transport


def run(coro):
    return asyncio.run(coro)


def test_p6_personal_case_about_marriage_is_level_d_with_referral(fake_dorar):
    # «أنا في دولة كذا، هل يجوز لي فعل كذا في زواجي؟»: a personal case; general information only, then referral.
    fake_dorar({})
    r = run(check_text("أنا في دولة كذا، هل يجوز لي فعل كذا في زواجي؟"))
    ld = r["level_d"]
    assert ld["detected"] and "alifta" in ld["body"]["url"]
    assert r["decision"]["action"] == "annotate"
    assert not r["citations"]  # nothing is ruled on


def test_p6_give_me_a_hadith_an_invented_hadith_is_not_found_and_referred(fake_dorar):
    # «أعطني حديثًا يثبت هذا الكلام»: a chatbot that invents one is caught; the tool says no matching evidence was found.
    fake_dorar({})
    r = run(check_text("طلبت حديثًا يثبت هذا الكلام، فقال الروبوت: قال رسول الله ﷺ: «من أحب وطنه أحبه الله ورسوله»"))
    c = r["citations"][0]
    assert c["status"] == "not_found" and c["tier"] == "refer"
    assert "لم نجد" in c["referral"]["ar"]
    assert c["hadith"]["groups"] == []  # no grading is written for it
    assert r["decision"]["action"] == "block"


def test_p6_misquoted_ayah_is_corrected_gently_with_surah_and_ayah(fake_dorar):
    # «سؤال يتضمن آية منقولة بخطأ»: point to the right text, show surah and ayah, do not build on the wrong one.
    fake_dorar({})
    r = run(check_text("قال تعالى: ﴿يا أيها الذين آمنوا إن جاءكم فاسق بخبر فتبينوا﴾"))
    c = r["citations"][0]
    assert c["status"] == "differs" and c["quran"]["surah"] == 49 and c["quran"]["ayah_from"] == 6
    assert c["quran"]["mushaf_text"] and c["tier"] == "verify"
    assert r["decision"]["action"] == "block"  # a chatbot does not show the misquote as Quran


def test_p6_do_all_muslims_agree_differing_gradings_are_all_shown_without_preference():
    # «هل كل المسلمين يتفقون...»: tell what is settled from what is ijtihad, never claim agreement.
    from app.dorar import DorarHadith as H, DorarResult
    from app.pipeline import _grade_groups, _hadith_tier
    info = _grade_groups("من تشبه بقوم فهو منهم", DorarResult(query="", method="w", hadiths=[
        H(text="من تشبه بقوم فهو منهم", mohdith="ابن حجر العسقلاني", mohdith_id="852", book="فتح الباري", number="10/ 282", grade="إسناده حسن"),
        H(text="من تشبه بقوم فهو منهم", mohdith="شعيب الأرناؤوط", mohdith_id="1438", book="تخريج المسند", number="5114", grade="إسناده ضعيف"),
    ]))
    assert [i["scholar_key"] for g in info["groups"] for i in g["items"]] == ["ibn_hajar", "shuaib"]  # by death year
    assert _hadith_tier({"status": "graded", "notes": [], "hadith": info}) == "verify"


def test_p6_non_arabic_term_keeps_its_sharia_meaning_through_jamhara():
    # «سؤال بلغة غير عربية يتضمن مصطلحًا دينيًا»: the term reference is Jamhara, not a machine translation.
    g = gloss_grade("حسن")
    assert g["terms"] and "islamic-content.com" in (g["terms"][0]["url"] or "")


def test_p5_transparency_and_privacy(monkeypatch):
    # Transparency: every reply says the tool is AI-assisted. Privacy: only the hadith wording leaves the server.
    seen = []

    def handler(request: httpx.Request):
        seen.append(request.url.params.get("q") or request.url.params.get("skey") or "")
        return httpx.Response(200, text="<html><div id='home'></div></html>")

    monkeypatch.setattr(dorar, "MIN_INTERVAL", 0)
    monkeypatch.setattr(dorar, "_client", dorar.DorarClient(transport=httpx.MockTransport(handler)))
    secret = "اسمي فلان ورقم هاتفي 0500000000"
    r = run(check_text(f"{secret}. قال رسول الله ﷺ: «إنما الأعمال بالنيات»"))
    assert "الذكاء الاصطناعي" in r["disclaimer"]["ar"]
    assert seen and all("0500000000" not in q and "فلان" not in q for q in seen)


def test_p5_unsupported_language_is_said_not_guessed(fake_dorar):
    fake_dorar({})
    r = run(check_text("Le Prophète a dit que les actes ne valent que par les intentions et que chacun sera rétribué"))
    assert r["unsupported_language"] == "fr" and r["decision"]["action"] == "annotate"
