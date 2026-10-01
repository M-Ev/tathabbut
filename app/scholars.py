"""Approved hadith scholars whose gradings تثبّت shows (the team's decision, 29 Sep 2026).

Two separate groups, each ordered by death year (AH), the scholars' usual convention.
Ranking scholars against each other is not the tool's job: every view is shown as it is.

`dorar_id` is the scholar's id in the Dorar hadith encyclopedia search filter (m[]).
Abd al-Qadir al-Arna'ut has no filter id on Dorar; his gradings are kept when they appear
in results, matched by name.
"""
import re
from dataclasses import dataclass

from .normalize import normalize_ar

IMAMS = "imams"      # أئمة الحديث
EDITORS = "editors"  # المحققون المعاصرون

GROUP_LABELS = {
    IMAMS: {"ar": "أحكام أئمة الحديث", "en": "Gradings by the classical imams of hadith"},
    EDITORS: {"ar": "أحكام المحققين المعاصرين", "en": "Gradings by modern hadith editors"},
}


@dataclass(frozen=True)
class Scholar:
    key: str
    name_ar: str
    name_en: str
    died_ah: int
    group: str
    dorar_id: str | None
    aliases: tuple = ()
    narrator_critic: bool = False  # mostly speaks about narrators, not hadith


SCHOLARS = (
    Scholar("malik", "الإمام مالك", "Imam Malik", 179, IMAMS, "179", ("مالك", "الامام مالك", "مالك بن انس")),
    Scholar("ibn_main", "يحيى بن معين", "Yahya ibn Ma'in", 233, IMAMS, "232", ("ابن معين", "يحيي بن معين"), True),
    Scholar("ibn_madini", "علي بن المديني", "Ali ibn al-Madini", 234, IMAMS, "234", ("ابن المديني",), True),
    Scholar("ahmad", "الإمام أحمد", "Imam Ahmad ibn Hanbal", 241, IMAMS, "241", ("احمد", "الامام احمد", "احمد بن حنبل")),
    Scholar("bukhari", "البخاري", "al-Bukhari", 256, IMAMS, "256"),
    Scholar("muslim", "مسلم", "Muslim", 261, IMAMS, "261"),
    Scholar("dhahabi", "الذهبي", "al-Dhahabi", 748, IMAMS, "748"),
    Scholar("ibn_hajar", "ابن حجر العسقلاني", "Ibn Hajar al-Asqalani", 852, IMAMS, "852", ("ابن حجر",)),
    Scholar("shakir", "أحمد شاكر", "Ahmad Shakir", 1377, EDITORS, "1377"),
    Scholar("muallimi", "المعلمي اليماني", "al-Mu'allimi al-Yamani", 1386, EDITORS, "1386", ("المعلمي",)),
    Scholar("albani", "الألباني", "al-Albani", 1420, EDITORS, "1420"),
    Scholar("aq_arnaut", "عبد القادر الأرناؤوط", "Abd al-Qadir al-Arna'ut", 1425, EDITORS, None,
            ("عبد القادر الارناووط", "عبدالقادر الارناووط", "عبد القادر الارناوط", "عبدالقادر الارناؤوط")),
    Scholar("shuaib", "شعيب الأرناؤوط", "Shu'ayb al-Arna'ut", 1438, EDITORS, "1438",
            ("شعيب الارناووط", "شعيب الارناوط")),
)

DORAR_IDS = [s.dorar_id for s in SCHOLARS if s.dorar_id]


def _key(name: str) -> str:
    return normalize_ar(name).replace(" ", "")


_BY_NAME = {}
for _s in SCHOLARS:
    for _n in (_s.name_ar, *_s.aliases):
        _BY_NAME[_key(_n)] = _s
_BY_ID = {s.dorar_id: s for s in SCHOLARS if s.dorar_id}


def find_scholar(name: str = "", dorar_id: str | None = None) -> Scholar | None:
    if dorar_id and dorar_id in _BY_ID:
        return _BY_ID[dorar_id]
    return _BY_NAME.get(_key(name or ""))


# Words that show a statement is about the hadith or its chain, not only about a narrator.
_HADITH_WORDS = re.compile("حديث|اسناد|هذا|متن|مرفوع|موقوف|مرسل|باطل|موضوع|لا اصل")
# Narrator descriptions that contain the word حديث but judge a person (منكر الحديث، ثقة في الحديث...).
_NARRATOR_PHRASES = re.compile(
    "(منكر|ضعيف|صالح|ثقه|متروك|صدوق|لين|مقارب|ذاهب|واهي|مضطرب|كثير الخطا في|ليس بالقوي في|ثبت في|ليس بشيء في) ?ال?حديث"
)


def is_hadith_level_grading(scholar: Scholar, grade: str) -> bool:
    """Ibn Ma'in and Ibn al-Madini mostly judge narrators; their words about a narrator must never
    be shown as a grading of the hadith. Keep their entry only when it speaks about the hadith itself."""
    if not scholar.narrator_critic:
        return True
    g = normalize_ar(grade)
    return bool(_HADITH_WORDS.search(_NARRATOR_PHRASES.sub(" ", g)))


GRADE_FLAGS = {
    "fabricated": re.compile("موضوع|لا اصل له|ليس له اصل|كذب|باطل|مكذوب"),
}


def grade_flags(grade: str) -> list[str]:
    g = normalize_ar(grade)
    return [k for k, rx in GRADE_FLAGS.items() if rx.search(g)]
