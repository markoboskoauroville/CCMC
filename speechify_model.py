#!/usr/bin/env python3
"""speechify_model: the newest English Speechify model is FOUND by the app, USED only after Marko approves it by ear
(modules/latest-model-at-start.md, 13.11.2026: "I like the voice from my Mac").

The family pattern is simba-<version>; never a pinned name. Asks GET /v1/audio/models, keeps the live, non-deprecated,
numbered simba-X.Y models (never *multilingual*, never simba-english), best first. Cached with its date in
~/.voice/speechify_model.json; refreshed when older than a day; API unreachable: the cache, then BUILTIN.
    python3 speechify_model.py            prints: using simba-3.2; newer candidate simba-X.Y (not approved)
    python3 speechify_model.py approve simba-X.Y   after his A/B test only
"""
import json, os, re, sys, time, urllib.request

API = "https://api.sws.speechify.com/v1/audio/models"
CACHE = os.path.expanduser("~/.voice/speechify_model.json")
KEYFILE = os.path.expanduser("~/Downloads/API/speechify_api.txt")
APPROVED_DEFAULT = "simba-3.2"               # approved by Marko's ears; changes only by `approve`
MAXAGE = 24 * 3600
FAMILY = re.compile(r"^simba-(\d+(?:\.\d+)*)$")


def _keys():
    try: txt = open(KEYFILE).read()
    except OSError: return []
    return list(dict.fromkeys(re.findall(r"\bsk_[A-Za-z0-9_-]{40,}", txt)))


def rank(models):
    """the family ids, highest version first: simba-3.5 > simba-3.2 > simba-3.0 ; others dropped"""
    ok = [m for m in models if FAMILY.match(m) and "multilingual" not in m]
    return sorted(ok, key=lambda m: [int(x) for x in FAMILY.match(m).group(1).split(".")], reverse=True)


def _ask(key):
    req = urllib.request.Request(API, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    return rank([m["id"] for m in data.get("models", []) if not m.get("deprecated")
                 and (m.get("english_voices_only") or "en" in (m.get("languages") or []))])


def _cache():
    try: return json.load(open(CACHE))
    except (OSError, ValueError): return {}


def _save(c):
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True); json.dump(c, open(CACHE, "w"))
    except OSError: pass


def approved(): return _cache().get("approved") or APPROVED_DEFAULT


def detect(force=False):
    """the best live model of the family (the candidate), asked at most once a day; offline: the cached one"""
    c = _cache()
    if c.get("candidate") and not force and time.time() - c.get("checked", 0) < MAXAGE: return c["candidate"]
    for k in _keys():
        try: found = _ask(k)
        except Exception: continue
        if found:
            c.update(candidate=found[0], checked=time.time(), models=found); _save(c)
            return found[0]
    return c.get("candidate")


def models(force=False):
    """what the app USES: the approved model only. A newer one is a candidate, reported, never used."""
    detect(force); return [approved()]


def label():
    cand = detect(); c = _cache(); a = approved()
    t = time.strftime("%d.%m %H:%M", time.localtime(c["checked"])) if c.get("checked") else "never"
    new = cand and cand != a and rank([cand, a])[0] == cand
    return "model: %s (approved)%s (checked %s)" % (a, "; newer candidate %s, NOT used until approved by ear" % cand if new else "", t)


if __name__ == "__main__":
    if sys.argv[1:2] == ["approve"] and len(sys.argv) == 3 and FAMILY.match(sys.argv[2]):
        c = _cache(); c["approved"] = sys.argv[2]; _save(c)
    print(label())
