"""«الأذكار الموثّقة»: nothing is shown that the sources do not support, where and how often they support it."""
import json
import re
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_adhkar as B  # noqa: E402

DATA = json.loads((ROOT / "data" / "adhkar.json").read_text(encoding="utf-8"))


def words(t):
    return set(re.findall(r"[ء-ي]+", B._plain(t)))


missing = B.missing_words


def test_every_shown_dhikr_is_in_an_authentic_narration_that_names_its_occasion_and_count():
    shown = 0
    for x in DATA["hadith"]:
        for p in x.get("shown", []):
            shown += 1
            src = p["source"]
            assert src["authentic"], x["id"]
            assert not missing(x["text"], src["text"]), (x["id"], missing(x["text"], src["text"]))
            pat = B.CONTEXT.get(p["category"])
            if pat:
                assert re.search(B._plain(pat), B._plain(src["text"])), (x["id"], p["category"])
            if p["count"]:
                assert re.search(B._plain(B.COUNT_WORDS[p["count"]]), B._plain(src["text"])), (x["id"], p["count"])
        assert not (x.get("shown") and x["check"].get("fabricated_by")), x["id"]
    assert shown >= 20


def test_a_verse_is_placed_under_an_occasion_only_on_a_verified_hadith():
    by_id = {x["id"]: x for x in DATA["hadith"]}
    for q in DATA["quran"]:
        for p in q["shown"]:
            if B.CONTEXT.get(p["category"]) or p["category"] == "ruqya_quran":
                ev = p["evidence"]
                assert ev and any(s["category"] == p["category"] for s in by_id[ev["id"]]["shown"]), (q["id"], p["category"])


def test_the_place_rule_keeps_a_dhikr_out_of_an_occasion_its_authentic_narration_does_not_name():
    item = {"categories": ["morning"], "count": 3, "text": "رضيت بالله ربا",
            "check": {"fabricated_by": [], "narrations": [
                {"text": "من قال حين يسمع المؤذن رضيت بالله ربا", "authentic": True, "in_sahihayn": False, "died_ah": 1420},
                {"text": "من قال حين يصبح ثلاث مرات رضيت بالله ربا", "authentic": False, "in_sahihayn": False, "died_ah": 1420}]}}
    assert B.place(item) == []
    item["check"]["narrations"][1]["authentic"] = True
    (p,) = B.place(item)
    assert p["category"] == "morning" and p["count"] == 3


def test_each_name_of_allah_is_in_the_verse_given_for_it():
    from app.normalize import skeleton_ar
    from app.quran import get_quran

    q = get_quran()
    names = json.loads((ROOT / "data" / "asma.json").read_text(encoding="utf-8"))["names"]
    for x in names:
        ay = q.ayat[q.index[(x["surah"], x["ayah"])]]
        w = x.get("mushaf_spelling") or (x["name"][2:] if x["name"].startswith("ال") and x["name"] != "الله" else x["name"])
        assert skeleton_ar(w) in skeleton_ar(ay.text), x["name"]


def test_the_section_endpoints():
    from app.main import app

    c = TestClient(app)
    d = c.get("/api/adhkar?lang=fr").json()
    assert d["categories"] and d["hadith"]
    assert all(x["ayat"] and x.get("meaning") for x in d["quran"])
    assert len(c.get("/api/mushaf").json()["surahs"]) == 114
    one = c.get("/api/mushaf/2?lang=ur&ayah=255").json()
    assert one["ayat"][0]["ayah"] == 255 and one["ayat"][0]["meaning"]
    assert c.get("/api/asma").json()["names"][0]["verse"]["ayat"]
