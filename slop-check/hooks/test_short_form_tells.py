"""Both-directions test for the short-form tells. Upstream README requires it."""
import importlib.util, re, sys

spec = importlib.util.spec_from_file_location("s", "ai_slop.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
NEW = {"9", "27", "28", "CL"}

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
    "The part nobody talks about is the cost.",
    "Here's the kicker: it doubled.",
    "That number travelled. The one that didn't:",
    "I don't think that's a ceiling. I think it's an order.",
    "It's not a feature. It's a platform.",
    "You shouldn't hand it write access on day one.",
    "We've done it this way from day one.",
    "That's the part that broke.",
    "Here's the part that took me longest to see.",
    "Now the part where your background helps.",
    "That's the part that most marketers miss.",
    "That's the step most people skip.",
    "It's the thing most founders overlook.",
    "That's what most people miss.",
    "This is the detail so many teams forget.",
    "The scenario modeling is where it actually earns its keep.",
    "That one meeting earned its keep.",
    "The dashboard has been earning its keep since launch.",
    "These checks earn their keep on large PRs.",
    "Ten links from sites that do what your audience actually wants.",
    "Start with what customers actually want.",
    "What's actually happening is simpler.",
    "Here is what the data actually shows.",
    "Knowing which 92 is the part no tool supplies.",
    "Taste is the thing no model can replace.",
    "Judgment is the one piece no AI gives you.",
    "That context is the part that no agent can fake.",
    "That's the bit no language model will ever learn.",
    "Trust is the one thing not even the best model can generate.",
    "Relationships are the part no amount of automation replaces.",
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
    "Day one of the cohort is 28 September.",
    "On day one of the trial we saw the bug.",
    "The day one report is filed by the duty manager.",
    "She talks about the part of the process that fails.",
    "We replaced the part, which had rusted through.",
    "Two things broke: the sync and the webhook.",
    "The mistake many organizations make is waiting.",
    "Most people skip this.",
    "Most of the team missed the call.",
    "He asked what most customers pay.",
    "He earned his keep mucking out stables.",
    "She earned her place on the Olympic team.",
    "Every feature has to earn its place.",
    "You can keep what you earn.",
    "It actually feels very natural to sit back.",
    "What a year. We actually shipped it.",
    "What did the customer want?",
    "Actually, what matters is the price.",
    "Email is the one field no enrichment tool returned for this account.",
    "No tool supplies this data.",
    "The part of the pipeline that fails is the sync step.",
    "The man nobody knew.",
    "It was the only part number no supplier had in stock.",
    "The one thing no customer wants is a surprise invoice.",
    "This is the part no longer covered by the warranty.",
    "There is no tool for the part we need.",
    "It was the one piece no museum would lend.",
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
