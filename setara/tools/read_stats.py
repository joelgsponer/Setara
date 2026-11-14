#!/usr/bin/env python3
"""Summarise the anonymous counts copied from a device at a field visit.

  python3 tools/read_stats.py path/to/stats.json [more.json ...]

The file is on the card at setara/data/love/setara/data/stats.json. It holds
no names and nothing finer than the week (spec section 10).
"""
import json
import sys
from collections import defaultdict

for path in sys.argv[1:]:
    s = json.load(open(path, encoding="utf-8"))
    print(f"== device {s.get('device', '?')}  ({path})")

    print("\nMinutes of use per week")
    for week in sorted(s.get("weeks", {})):
        parts = ", ".join(f"{k} {v:.0f}" for k, v in sorted(s["weeks"][week].items()))
        print(f"  {week}: {parts}")

    print("\nLevels: plays, first-try success, stars per play")
    levels = defaultdict(lambda: [0, 0, 0, 0])
    for rid, r in s.get("rounds", {}).items():
        key = "-".join(rid.split("-")[:2])
        a = levels[key]
        a[0] += r.get("plays", 0)
        a[1] += r.get("attempts", 0)
        a[2] += r.get("correct", 0)
        a[3] += r.get("stars", 0)
    for key in sorted(levels):
        plays, attempts, correct, stars = levels[key]
        rate = f"{100 * correct / attempts:.0f}%" if attempts else "-"
        print(f"  {key:10} {plays:5} plays   {rate:>4} right   {stars / plays if plays else 0:.1f} stars")

    hard = sorted(
        ((r["correct"] / r["attempts"], rid) for rid, r in s.get("rounds", {}).items() if r.get("attempts", 0) >= 20),
    )[:10]
    if hard:
        print("\nHardest rounds (at least 20 answers)")
        for rate, rid in hard:
            print(f"  {rid:16} {100 * rate:.0f}% right")

    if s.get("checks"):
        print("\nQuick Check: right answers out of class size")
        for lesson in sorted(s["checks"]):
            c = s["checks"][lesson]
            share = 100 * c["right"] / c["size"] if c.get("size") else 0
            print(f"  {lesson:18} {c['right']}/{c['size']}  ({share:.0f}%)  taught {c['times']}x")

    t = s.get("teacher", {})
    if t:
        previews = sum(v for k, v in t.items() if k.startswith("preview_"))
        lessons = sum(v for k, v in t.items() if k.startswith("done_"))
        print(f"\nTeacher: {lessons} lessons finished, {previews} previews, course lesson reached {t.get('course_lesson', 0)}")

    if s.get("log"):
        print("\nProblems noted by the app")
        for e in s["log"]:
            print(f"  {e.get('week')}  v{e.get('v')}  {e.get('code')}")
    print()
