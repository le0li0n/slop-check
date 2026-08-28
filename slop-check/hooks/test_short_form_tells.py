"""Both-directions test for the short-form tells. Upstream README requires it."""
import importlib.util, re, sys

spec = importlib.util.spec_from_file_location("s", "ai_slop.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
NEW = {"9", "27", "28"}

SHOULD_FLAG = [
    "Two things to sit with. One, the first.",
    "Something to sit with this week.",
    "Three things to consider before you buy.",
    "These are top of mind for the team.",
    "Here are three key takeaways from the call.",
    "Some surprising news landed today.",
    "You might find this fascinating.",
    "What's worth noting here is the price.",
    "But here's the thing nobody says.",
    "What nobody tells you is that it breaks.",
    "The part nobody talks about is the cost.",
    "Here's the kicker: it doubled.",
    "That number travelled. The one that didn't:",
    "I don't think that's a ceiling. I think it's an order.",
    "It's not a feature. It's a platform.",
]

SHOULD_NOT_FLAG = [
    "I sat with the data for an hour before writing.",
    "We sat with the customer and watched them use it.",
    "There are three things the API returns.",
    "Consider the alternative before you commit.",
    "The kicker pedal is on the left.",
    "He was the one that didn't renew, and he told us why.",   # guard: needs the reveal shape
    "I don't think we should ship on Friday.",
    "It's not ready.",
    "Here are the three keys to the building.",
    "The news was surprising to everyone in the room.",
    "She talks about the part of the process that fails.",
    "Two things broke: the sync and the webhook.",
    "Top of mind share rose four points.",
]

def hits(t):
    return [(s, re.search(p, t, re.I).group(0))
            for s, w, p, f in m.LINE_PATTERNS
            if s in NEW and re.search(p, t, re.I)]

fails = 0
print("SHOULD FLAG")
for t in SHOULD_FLAG:
    h = hits(t)
    ok = bool(h)
    fails += not ok
    print(f"  {'ok  ' if ok else 'MISS'} {t[:52]!r:56} {[f'§{s}' for s,_ in h]}")

print("\nSHOULD NOT FLAG")
for t in SHOULD_NOT_FLAG:
    h = hits(t)
    ok = not h
    fails += not ok
    print(f"  {'ok  ' if ok else 'FALSE POSITIVE'} {t[:52]!r:56} {[(f'§{s}', x) for s,x in h]}")

print(f"\nfailures: {fails}")
sys.exit(1 if fails else 0)
