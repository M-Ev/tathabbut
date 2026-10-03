# سجل الأخطاء · Errata

Every fault the team found in its own results during the build days (4 to 6 October 2026): what a user saw, how it was found, the commit that fixed it, and the measure before and after. A fault found later is added here, not edited away. Details per change are in `CHANGELOG.md`.

| # | What a user saw | Found by | Fixed in | Before → after |
|---|---|---|---|---|
| 1 | A hadith al-Albani graded fabricated showed «حالة الدليل: موثّق المصدر» beside a red verdict | preflight review, 3 Oct | 59e0d67 | evidence status now from `data/display_rules.json`; `documented` only for an ayah matching the Mushaf |
| 2 | A second hadith introduced with a bare «وقال:» was skipped silently | preflight B2 | 59e0d67 | extracted and checked |
| 3 | «إن الله مع الصابرين (البقرة 200)» was called "not in the Mushaf" | preflight B3 | 59e0d67 | found (2:153), the wrong number pointed out |
| 4 | A Dorar hit at 70% similarity, with its grading, under an ayah missing from the Mushaf | preflight B4 | 59e0d67 | only a strong match (85+) is shown there |
| 5 | Correct Quran text typed in common spelling (شيئا، إبراهيم، الليل...) reported as a misquote | synthetic set, seed 2026 | 828d839 | 52/276 (18.8%) → 0/276; census 949/6216 → 1/6216 |
| 6 | An added or dropped alef («قال» for ﴿قُلۡ﴾) passed as the exact ayah | plan review, 2 Oct | 828d839 | alef cases 0 measured → 60/60 caught |
| 7 | One-word quotes said "not found" instead of "too short to check" | synthetic set | 828d839 | referred to a Quran specialist with that reason |
| 8 | Fatwa questions: «القرآن» never met «القران»; 6 of 12 questions showed nothing; a fatwa on removing body hair shown for a new Muslim's question about his Christian wife | live fatwa run, 4 Oct | 7a12f1b | 3 of 12 show nothing; the unrelated fatwa gone; hit rate awaits the reviewer |
| 9 | «من غشنا فليس منا» (Sahih Muslim) shown red, «لا تؤيده المصادر المعتمدة», because of Ibn Hajar's «موضوع» on an 897-word sermon containing it; the same for «كن في الدنيا كأنك غريب» (al-Bukhari) | live hadith run through the site, 4 Oct | a6556e3 | both «تؤيده المصادر»; the longer narration shown with a note, not counted |
| 10 | «الدين المعاملة» shown beside al-Albani's «صحيح» on «إن الدين النصيحة» | same run | a6556e3 | a similar wording, with the missing word named |
| 11 | Sayings with one word changed («أدومها وإن كثر» for «وإن قل») took the hadith's grading | trap set, 4 Oct | cadce51 | 13/20 → 2/20 (one is al-Albani's grading of the saying itself) |
| 12 | A written «رواه البخاري» after a fabricated saying passed unremarked | plan item 19 | e7f269b | «لم نجده في صحيح البخاري ضمن نتائج البحث» |
| 13 | Behind the hosting proxy all visitors shared one request limit | plan item 16 (inferred, not observed) | 12060d7 | per visitor |
| 14 | More than 12 citations were cut with no word | plan item 18 | 12060d7 | «فُحص أول ١٢ استشهادًا من ١٥» |
| 15 | «هل علي بن أبي طالب أول من أسلم؟» treated as a fatwa question; «أنا طلقت زوجتي وهي حائض» missed | plan item 32 | 2398948 | both right |
| 16 | The published `eval/report.md` showed the four hadith cases as "source error" | preflight | 17dab76 | report now runs on the live site (`--via-space`) and says where it ran |

Known and open:
- Three hadith whose narration Dorar shows abbreviated or worded differently («من حسن إسلام المرء...», «تبسمك في وجه أخيك...», «تفكر ساعة...») now read as a similar wording (cost of fault 11's fix).
- `/api/health` reports the model ready whenever an OpenAI-compatible endpoint is configured, even if it is scaled to zero.
- The coverage values (10 words, 80%) were tuned on the same cases they are reported on; the Sharia reviewer's set is the real test.
