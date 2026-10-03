#!/usr/bin/env sh
# Every measurement in one run (plan item 34). Offline parts always run; parts that need the live sources run
# through the deployed site (Dorar refuses some clouds directly), at about 2 Dorar searches per case.
#   scripts/eval_all.sh                      offline only
#   scripts/eval_all.sh https://3rb-tathabbut.hf.space
set -e
cd "$(dirname "$0")/.."
SPACE="$1"
echo "== unit tests"; python3 -m pytest -q
echo "== Quran synthetic set and census (eval/synth_report.md)"; python3 eval/synth_quran.py
echo "== trap cases, re-scored from recorded live results (eval/trap_report.md)"; python3 eval/run_trap_eval.py
if [ -n "$SPACE" ]; then
  echo "== evaluation set on the live site (eval/report.md)"; python3 eval/run_eval.py --via-space "$SPACE"
  echo "== hadith set on the live site (eval/hadith_cases.md)"; python3 eval/verify_hadith_cases.py --via-space "$SPACE"
  echo "== fatwa matching, live (eval/fatwa_report.md)"; python3 eval/run_fatwa_eval.py
else
  echo "== evaluation set, local pipeline (eval/report.md; hadith cases need the live site)"; python3 eval/run_eval.py
fi
