"""Content checker for the Learn app. Run from anywhere:

    python tools/check.py            # check every deck listed in content/index.json
    python tools/check.py ubiquiti   # check only some decks

Exit code 0 = no problems. Checks structure, rules from CONTENT-GUIDE.md and a privacy scan.
"""
import json, re, os, sys

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content")
problems = 0


def p(msg):
    global problems
    problems += 1
    print("  !", msg)


# words that must never appear in the public app (extend freely)
PRIVACY = re.compile(
    r"€|\$[1-9]|\b\d+ ?(eur|dkk|usd|nok|sek)\b|\bonninen\b|\bkesko\b|\bgigantti\b|\bverkkokauppa\b|"
    r"\bmultitronic\b|\bvalmet\b|s-ryhm|\btobias\b|pricefile|our own sales|local sales|"
    r"deal reg form", re.I)

idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
groups = idx.get("groups", {})
for gk, gv in groups.items():
    if isinstance(gv, dict) and not str(gv.get("color", "#")).startswith("#"):
        print("  ! group %s has a bad color" % gk)
listed = [d["id"] for d in idx["decks"]]
only = sys.argv[1:]
ids = {}

for m in idx["decks"]:
    name = m["id"]
    if only and name not in only:
        continue
    print(name)
    if m.get("group") not in groups:
        p("group '%s' not defined in index.json groups" % m.get("group"))
    if m.get("focus") not in (0, 1, 2, 3, 4, 5):
        p("focus must be 0..5")
    f = os.path.join(D, name + ".json")
    if not os.path.exists(f):
        p("deck file missing")
        continue
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        p("INVALID JSON: %s" % e)
        continue
    for k in ("title", "desc", "lessons"):
        if k not in d:
            p("missing " + k)
    if not d.get("src"):
        p("no deck src")
    for r in d.get("related", []):
        if r not in listed:
            p("related id '%s' is not a deck in index.json" % r)
    lv = {}
    for l in d.get("lessons", []):
        lid = l.get("id")
        if lid in ids:
            p("duplicate id %s (also in %s)" % (lid, ids[lid]))
        ids[lid] = name
        lv[l.get("lvl")] = lv.get(l.get("lvl"), 0) + 1
        if not l.get("src"):
            p("%s: no lesson src" % lid)
        else:
            for s in l["src"]:
                if not str(s.get("u", "")).startswith("http"):
                    p("%s: bad src url" % lid)
        pg = l.get("pages", [])
        if len(pg) != 3:
            p("%s: %d pages" % (lid, len(pg)))
        for i, x in enumerate(pg):
            txt = re.sub(r"<[^>]+>", " ", x.get("t", ""))
            n = len(txt.split())
            if n < 20 or n > 75:
                p("%s page %d: %d words" % (lid, i + 1, n))
            if re.search(r"<(?!/?(b|i|br|ul|li)\b)[a-z]", x.get("t", "")):
                p("%s page %d: disallowed html" % (lid, i + 1))
        qs = l.get("quiz", [])
        if not 3 <= len(qs) <= 4:
            p("%s: %d questions" % (lid, len(qs)))
        pos = []
        for j, q in enumerate(qs):
            o = q.get("o", [])
            if not 3 <= len(o) <= 4:
                p("%s q%d: %d options" % (lid, j + 1, len(o)))
            if not isinstance(q.get("a"), int) or not 0 <= q["a"] < len(o):
                p("%s q%d: bad a" % (lid, j + 1))
            else:
                pos.append(q["a"])
            if not q.get("w"):
                p("%s q%d: no explanation" % (lid, j + 1))
        if len(pos) >= 3 and len(set(pos)) == 1:
            p("%s: all correct answers at index %s" % (lid, pos[0]))
    blob = json.dumps(d, ensure_ascii=False)
    if "—" in blob or "–" in blob:
        p("em or en dash found")
    for mt in PRIVACY.finditer(blob):
        p("PRIVACY: '%s' found" % mt.group(0))
    print("  lessons=%d levels=%s" % (len(d.get("lessons", [])), dict(sorted(lv.items()))))

for fn in os.listdir(D):
    if fn.endswith(".json") and fn != "index.json" and fn[:-5] not in listed:
        print("note: %s exists but is not listed in index.json (hidden from the app)" % fn)
print("problems:", problems)
sys.exit(1 if problems else 0)
