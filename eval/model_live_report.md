# The language model on the live site: English hadith (plan item 23, first live run)

Run: 5 Oct 2026, through `POST /api/check` with `deep: true` on https://3rb-tathabbut.hf.space (commit `68f5d04`),
ALLaM-7B-Instruct-preview (Q4_K_M GGUF, llama.cpp) on the Space's free CPU (2 vCPU). The four English cases of
`eval/hadith_cases.jsonl`; the Arabic wording expected for each is recorded with the case (not written by the model).

| Case | Expected Arabic wording | ALLaM's search wording | Result shown | Seconds |
|---|---|---|---|---|
| hd-en-niyyat | إنما الأعمال بالنيات | الأعمال بالنيات، ولكل امرئ ما نوى. | right: Sahih al-Bukhari 1 found; «يحتاج مزيدًا من التحقق» because the match is the model's | 268 |
| hd-en-strong | ليس الشديد بالصرعة | الرجل القوي ليس الذي يغلب الناس بقوته، ولكن الرجل القوي هو الذي يملك نفسه عند الغضب. | missed, safely: a literal translation, no narration shares it, the pick was rejected and the quote referred | 285 |
| hd-en-tuhur | الطهور شطر الإيمان | النظافة من الإيمان | **wrong**: a hadith of Sahih Muslim was traced to a different, fabricated saying and shown with al-Albani's «موضوع»; the status stayed «يحتاج مزيدًا من التحقق» (not red) and the report says the Arabic wording came from the model | 256 |
| hd-en-china | اطلبوا العلم ولو بالصين | اطلب العلم ولو بالصين | right: al-Dhahabi's and al-Albani's gradings of that wording | 245 |

ALLaM traced 2 of 4, missed 1 safely and mistraced 1, at about 4.4 minutes per quote on the free CPU.

What follows from it:
- The English-to-Arabic jobs (search wording and picking the source) need a stronger model; extraction from
  Arabic text stays with ALLaM. `TATHABBUT_LLM_FALLBACK_FIRST=arabic,match` routes those two jobs to the fallback
  model first (ALLaM answers if it fails); every report names the model that answered.
- The guards held where they could: no model match is ever shown green or red, and the literal translation
  found nothing rather than a wrong source. They cannot catch a model that proposes a real but different saying
  (hd-en-tuhur); that is why the model's Arabic wording is always shown to the reader.
- Four cases are not an accuracy figure; `eval/run_model_eval.py` measures each job on a seeded set.

## Second and third runs: the stronger model, then the fast free one (5 Oct)

Same four cases, same site, with the English-to-Arabic jobs (and, in the third run, extraction too) sent to the
fallback model first (`TATHABBUT_LLM_FALLBACK_FIRST`). Each report's `model.answered_by` names who answered.

| Case | ALLaM (CPU) | Qwen3-235B (HF router), wording and pick | gpt-oss-120b (Groq free tier), all jobs |
|---|---|---|---|
| hd-en-niyyat | right, 268 s | (not rerun) | right: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى» → Bukhari 1, 6 s |
| hd-en-strong | missed safely, 285 s | right: «ليس الشديد بالصرعة...» → Bukhari 6114, Muslim 2609, 117 s (ALLaM extraction included) | missed safely: an empty wording, 1 s (fixed in `702685b`: asked again, then ALLaM) |
| hd-en-tuhur | **wrong** (fabricated saying), 256 s | referred: still «النظافة من الإيمان», no source picked | right: «الطُّهُورُ شَطْرُ الإِيْمَانِ» → Sahih Muslim 223, 6 s |
| hd-en-china | right, 245 s | (not rerun) | right: «اطلبوا العلم ولو في الصين» → al-Albani's grading, 5 s |

gpt-oss-120b on Groq traced 3 of 4 and missed 1 safely, in about 6 seconds a quote, at no per-token cost. It
became the first model for all three jobs; ALLaM stays on the site and answers whenever the fast model fails,
is rate-limited, or gives nothing usable.
