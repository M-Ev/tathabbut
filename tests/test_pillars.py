"""The pillars page quotes Shaykh Ibn Baz word for word: every quote, and every phrase given to say in the prayer,
must be in the texts fetched from his official site (data/pillars_sources.json)."""
import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "static" / "pillars.js").read_text(encoding="utf-8")
SOURCES = json.loads((ROOT / "data" / "pillars_sources.json").read_text(encoding="utf-8"))["fatwas"]
ALL = " ".join(f["text"] for f in SOURCES.values())


def test_every_quote_is_in_the_fatwa_it_names():
    quotes = re.findall(r'\{ src: "(\w+)", q: "([^"]+)" \}', JS)
    assert len(quotes) >= 25
    for src, q in quotes:
        assert src in SOURCES, src
        assert q in SOURCES[src]["text"], (src, q)


def test_every_phrase_to_say_is_in_the_shaykhs_words():
    consts = dict(re.findall(r'const (TASHAHHUD|IBRAHIMIYYA) = "([^"]+)";', JS))
    says = [s for s in re.findall(r'say: "([^"]+)"', JS) if s not in ("يقول:", "Say:")] + list(consts.values())
    assert len(says) >= 12
    for s in says:
        if s in ("بسم الله",):  # the basmala: «يسمي الله»
            continue
        for part in s.split("، "):
            assert part in ALL, part


def test_the_links_point_to_the_fetched_fatwas():
    for key, url in re.findall(r'(\w+): \{ url: "(https://binbaz\.org\.sa/fatwas/\d+)"', JS):
        assert SOURCES[key]["url"].startswith(url + "/"), key


def test_the_pillars_api_gives_the_verses_from_the_mushaf_with_their_meanings():
    from app.main import app

    r = TestClient(app).get("/api/pillars").json()
    assert set(r) == {"shahada", "salah", "zakah", "sawm", "hajj", "fatiha"}
    assert len(r["fatiha"]["ayat"]) == 7 and r["fatiha"]["surah_ar"] == "الفاتحة"
    assert "en" in r["sawm"]["translations"] and r["sawm"]["ayat"][0]["ayah"] == 183
