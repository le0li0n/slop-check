"""Who we collect, and where their pre-2012 writing lives.

Every seed is a Wayback prefix query. More authors are listed than the target
needs, because roughly a third of any list like this fails to yield five clean
documents and it is cheaper to over-list than to come back.

Fields:
  slug     directory name
  name     author, as they published
  area     rough beat, for the manifest
  type     default document type (essay, blog post, article, ebook chapter, manifesto)
  seeds    Wayback prefix queries
  accept   optional regex a permalink must match (overrides the generic rules)
  reject   optional extra exclusion regex
  min_chars optional floor, for writers whose form is genuinely short
"""

AUTHORS = [
    # ---------------------------------------------------------------- startups & venture
    dict(slug="paul-graham", name="Paul Graham", area="Startups & venture", type="essay",
         seeds=["paulgraham.com/"],
         accept=r"^https?://(?:www\.)?paulgraham\.com/[a-z0-9]+\.html$",
         reject=r"/(index|articles|rss|bio|books|faq|lisp|arc|bel|antispam|raq|rp|say|"
                r"progbot|noop|lwba|start|jessica|founders|list|hp|kate|carl|equity)\.html"),
    dict(slug="fred-wilson", name="Fred Wilson", area="Startups & venture", type="blog post",
         seeds=["avc.com/a_vc/", "avc.blogs.com/a_vc/"]),
    dict(slug="brad-feld", name="Brad Feld", area="Startups & venture", type="blog post",
         seeds=["feld.com/wp/archives/", "feld.com/archives/"]),
    dict(slug="mark-suster", name="Mark Suster", area="Startups & venture", type="blog post",
         seeds=["bothsidesofthetable.com/"]),
    dict(slug="ben-horowitz", name="Ben Horowitz", area="Startups & venture", type="blog post",
         seeds=["bhorowitz.com/"]),
    dict(slug="steve-blank", name="Steve Blank", area="Startups & venture", type="blog post",
         seeds=["steveblank.com/"]),
    dict(slug="eric-ries", name="Eric Ries", area="Startups & venture", type="blog post",
         seeds=["startuplessonslearned.com/", "startuplessonslearned.blogspot.com/"]),
    dict(slug="marc-andreessen", name="Marc Andreessen", area="Startups & venture", type="blog post",
         seeds=["blog.pmarca.com/", "pmarca-archive.posterous.com/"]),
    dict(slug="chris-dixon", name="Chris Dixon", area="Startups & venture", type="blog post",
         seeds=["cdixon.org/", "cdixon.wordpress.com/"]),
    dict(slug="dharmesh-shah", name="Dharmesh Shah", area="Startups & venture", type="blog post",
         seeds=["onstartups.com/tabid/", "onstartups.com/"]),
    dict(slug="jason-cohen", name="Jason Cohen", area="Startups & venture", type="blog post",
         seeds=["blog.asmartbear.com/"]),
    dict(slug="david-skok", name="David Skok", area="Startups & venture", type="blog post",
         seeds=["forentrepreneurs.com/"]),
    dict(slug="bill-gurley", name="Bill Gurley", area="Startups & venture", type="blog post",
         seeds=["abovethecrowd.com/"]),
    dict(slug="naval-ravikant", name="Naval Ravikant", area="Startups & venture", type="blog post",
         seeds=["startupboy.com/"]),
    dict(slug="josh-kopelman", name="Josh Kopelman", area="Startups & venture", type="blog post",
         seeds=["redeye.firstround.com/"]),
    dict(slug="jeff-bussgang", name="Jeff Bussgang", area="Startups & venture", type="blog post",
         seeds=["bostonvcblog.typepad.com/"]),
    dict(slug="bijan-sabet", name="Bijan Sabet", area="Startups & venture", type="blog post",
         seeds=["bijansabet.com/"]),
    dict(slug="david-cohen", name="David Cohen", area="Startups & venture", type="blog post",
         seeds=["davidgcohen.com/", "colorado-startups.com/"]),
    dict(slug="guy-kawasaki", name="Guy Kawasaki", area="Startups & venture", type="blog post",
         seeds=["blog.guykawasaki.com/"]),
    dict(slug="steve-pavlina", name="Steve Pavlina", area="Startups & venture", type="blog post",
         seeds=["stevepavlina.com/blog/"]),

    # ---------------------------------------------------------------- software engineering
    dict(slug="joel-spolsky", name="Joel Spolsky", area="Software engineering", type="essay",
         seeds=["joelonsoftware.com/articles/", "joelonsoftware.com/items/"]),
    dict(slug="jeff-atwood", name="Jeff Atwood", area="Software engineering", type="blog post",
         seeds=["codinghorror.com/blog/"]),
    dict(slug="martin-fowler", name="Martin Fowler", area="Software engineering", type="essay",
         seeds=["martinfowler.com/bliki/", "martinfowler.com/articles/"]),
    dict(slug="steve-yegge", name="Steve Yegge", area="Software engineering", type="blog post",
         seeds=["steve-yegge.blogspot.com/", "steve.yegge.googlepages.com/"]),
    dict(slug="signal-v-noise", name="37signals (Signal v. Noise)", area="Software engineering",
         type="blog post", seeds=["37signals.com/svn/posts/", "signalvnoise.com/posts/",
                                  "37signals.com/svn/archives"]),
    dict(slug="robert-c-martin", name="Robert C. Martin", area="Software engineering", type="blog post",
         seeds=["blog.objectmentor.com/articles/", "butunclebob.com/ArticleS."]),
    dict(slug="eric-raymond", name="Eric S. Raymond", area="Software engineering", type="essay",
         seeds=["catb.org/~esr/writings/", "catb.org/esr/writings/"]),
    dict(slug="tim-bray", name="Tim Bray", area="Software engineering", type="blog post",
         seeds=["tbray.org/ongoing/When/"]),
    dict(slug="michael-lopp", name="Michael Lopp (Rands)", area="Software engineering", type="blog post",
         seeds=["randsinrepose.com/archives/"]),
    dict(slug="scott-hanselman", name="Scott Hanselman", area="Software engineering", type="blog post",
         seeds=["hanselman.com/blog/"]),
    dict(slug="raymond-chen", name="Raymond Chen", area="Software engineering", type="blog post",
         seeds=["blogs.msdn.com/b/oldnewthing/archive/", "blogs.msdn.com/oldnewthing/archive/"]),
    dict(slug="simon-willison", name="Simon Willison", area="Software engineering", type="blog post",
         seeds=["simonwillison.net/"]),
    dict(slug="john-gruber", name="John Gruber", area="Software engineering", type="blog post",
         seeds=["daringfireball.net/20", "daringfireball.net/"]),
    dict(slug="steve-souders", name="Steve Souders", area="Software engineering", type="blog post",
         seeds=["stevesouders.com/blog/"]),
    dict(slug="aaron-swartz", name="Aaron Swartz", area="Software engineering", type="blog post",
         seeds=["aaronsw.com/weblog/"]),
    dict(slug="paul-buchheit", name="Paul Buchheit", area="Software engineering", type="blog post",
         seeds=["paulbuchheit.blogspot.com/"]),
    dict(slug="karl-fogel", name="Karl Fogel", area="Software engineering", type="ebook chapter",
         seeds=["producingoss.com/en/"],
         accept=r"producingoss\.com/en/[a-z0-9-]+\.html$"),

    # ---------------------------------------------------------------- marketing, SEO & content
    dict(slug="seth-godin", name="Seth Godin", area="Marketing & content", type="blog post",
         seeds=["sethgodin.typepad.com/seths_blog/"], min_chars=450),
    dict(slug="brian-clark", name="Brian Clark (Copyblogger)", area="Marketing & content",
         type="blog post", seeds=["copyblogger.com/"]),
    dict(slug="rand-fishkin", name="Rand Fishkin (SEOmoz)", area="Marketing & content",
         type="blog post", seeds=["seomoz.org/blog/"]),
    dict(slug="avinash-kaushik", name="Avinash Kaushik", area="Marketing & content", type="blog post",
         seeds=["kaushik.net/avinash/"]),
    dict(slug="chris-brogan", name="Chris Brogan", area="Marketing & content", type="blog post",
         seeds=["chrisbrogan.com/"]),
    dict(slug="david-meerman-scott", name="David Meerman Scott", area="Marketing & content",
         type="blog post", seeds=["webinknow.com/"]),
    dict(slug="ann-handley", name="Ann Handley", area="Marketing & content", type="blog post",
         seeds=["annhandley.com/", "mpdailyfix.com/"]),
    dict(slug="danny-sullivan", name="Danny Sullivan", area="Marketing & content", type="article",
         seeds=["searchengineland.com/"]),
    dict(slug="aaron-wall", name="Aaron Wall", area="Marketing & content", type="blog post",
         seeds=["seobook.com/"]),
    dict(slug="joe-pulizzi", name="Joe Pulizzi", area="Marketing & content", type="blog post",
         seeds=["junta42.com/", "contentmarketinginstitute.com/"]),
    dict(slug="neil-patel", name="Neil Patel", area="Marketing & content", type="blog post",
         seeds=["quicksprout.com/", "pronetadvertising.com/"]),
    dict(slug="brian-solis", name="Brian Solis", area="Marketing & content", type="blog post",
         seeds=["briansolis.com/"]),
    dict(slug="jeremiah-owyang", name="Jeremiah Owyang", area="Marketing & content", type="blog post",
         seeds=["web-strategist.com/blog/"]),
    dict(slug="bryan-eisenberg", name="Bryan Eisenberg", area="Marketing & content", type="blog post",
         seeds=["bryaneisenberg.com/", "grokdotcom.com/"]),
    dict(slug="jay-baer", name="Jay Baer", area="Marketing & content", type="blog post",
         seeds=["convinceandconvert.com/"]),
    dict(slug="lee-odden", name="Lee Odden", area="Marketing & content", type="blog post",
         seeds=["toprankblog.com/"]),
    dict(slug="mack-collier", name="Mack Collier", area="Marketing & content", type="blog post",
         seeds=["mackcollier.com/", "moblogsmoproblems.blogspot.com/"]),

    # ---------------------------------------------------------------- management & strategy
    dict(slug="tom-peters", name="Tom Peters", area="Management & strategy", type="blog post",
         seeds=["tompeters.com/"]),
    dict(slug="bob-sutton", name="Bob Sutton", area="Management & strategy", type="blog post",
         seeds=["bobsutton.typepad.com/"]),
    dict(slug="daniel-pink", name="Daniel Pink", area="Management & strategy", type="blog post",
         seeds=["danpink.com/"]),
    dict(slug="penelope-trunk", name="Penelope Trunk", area="Management & strategy", type="blog post",
         seeds=["blog.penelopetrunk.com/"]),
    dict(slug="umair-haque", name="Umair Haque", area="Management & strategy", type="article",
         seeds=["blogs.hbr.org/haque/", "blogs.harvardbusiness.org/haque/"]),
    dict(slug="rosabeth-moss-kanter", name="Rosabeth Moss Kanter", area="Management & strategy",
         type="article", seeds=["blogs.hbr.org/kanter/", "blogs.harvardbusiness.org/kanter/"]),
    dict(slug="peter-bregman", name="Peter Bregman", area="Management & strategy", type="article",
         seeds=["blogs.hbr.org/bregman/", "blogs.harvardbusiness.org/bregman/"]),
    dict(slug="john-hagel", name="John Hagel", area="Management & strategy", type="blog post",
         seeds=["edgeperspectives.typepad.com/"]),
    dict(slug="jim-collins", name="Jim Collins", area="Management & strategy", type="article",
         seeds=["jimcollins.com/article_topics/", "jimcollins.com/lib/"]),
    dict(slug="charles-green", name="Charles H. Green", area="Management & strategy", type="blog post",
         seeds=["trustedadvisor.com/trustmatters/", "trustmatters.trustedadvisor.com/"]),

    # ---------------------------------------------------------------- design, UX & product
    dict(slug="jakob-nielsen", name="Jakob Nielsen", area="Design, UX & product", type="article",
         seeds=["useit.com/alertbox/"]),
    dict(slug="don-norman", name="Don Norman", area="Design, UX & product", type="essay",
         seeds=["jnd.org/dn.mss/"]),
    dict(slug="luke-wroblewski", name="Luke Wroblewski", area="Design, UX & product", type="blog post",
         seeds=["lukew.com/ff/entry.asp"],
         accept=r"lukew\.com/ff/entry\.asp\?\d+$"),
    dict(slug="jared-spool", name="Jared Spool", area="Design, UX & product", type="article",
         seeds=["uie.com/articles/", "uie.com/brainsparks/"]),
    dict(slug="marty-cagan", name="Marty Cagan", area="Design, UX & product", type="essay",
         seeds=["svpg.com/articles/", "svpg.com/blog/"]),
    dict(slug="kathy-sierra", name="Kathy Sierra", area="Design, UX & product", type="blog post",
         seeds=["headrush.typepad.com/creating_passionate_users/"]),
    dict(slug="khoi-vinh", name="Khoi Vinh", area="Design, UX & product", type="blog post",
         seeds=["subtraction.com/"]),
    dict(slug="joshua-porter", name="Joshua Porter", area="Design, UX & product", type="blog post",
         seeds=["bokardo.com/"]),
    dict(slug="jeffrey-zeldman", name="Jeffrey Zeldman", area="Design, UX & product", type="blog post",
         seeds=["zeldman.com/"]),
    dict(slug="37signals-getting-real", name="37signals", area="Design, UX & product",
         type="ebook chapter", seeds=["gettingreal.37signals.com/ch"],
         accept=r"gettingreal\.37signals\.com/ch\d+_[A-Za-z_]+\.php$"),

    # ---------------------------------------------------------------- technology & media analysis
    dict(slug="john-battelle", name="John Battelle", area="Technology & media", type="blog post",
         seeds=["battellemedia.com/"]),
    dict(slug="nicholas-carr", name="Nicholas Carr", area="Technology & media", type="blog post",
         seeds=["roughtype.com/"]),
    dict(slug="clay-shirky", name="Clay Shirky", area="Technology & media", type="essay",
         seeds=["shirky.com/writings/", "shirky.com/herecomeseverybody/"]),
    dict(slug="doc-searls", name="Doc Searls", area="Technology & media", type="blog post",
         seeds=["doc.searls.com/", "blogs.law.harvard.edu/doc/"]),
    dict(slug="danah-boyd", name="danah boyd", area="Technology & media", type="essay",
         seeds=["zephoria.org/thoughts/", "danah.org/papers/"]),
    dict(slug="tim-oreilly", name="Tim O'Reilly", area="Technology & media", type="essay",
         seeds=["radar.oreilly.com/tim/", "radar.oreilly.com/archives/"]),
    dict(slug="anil-dash", name="Anil Dash", area="Technology & media", type="blog post",
         seeds=["dashes.com/anil/"]),
    dict(slug="dave-winer", name="Dave Winer", area="Technology & media", type="blog post",
         seeds=["scripting.com/stories/", "scripting.com/davenet/"]),
    dict(slug="horace-dediu", name="Horace Dediu", area="Technology & media", type="blog post",
         seeds=["asymco.com/"]),
    dict(slug="jeff-jarvis", name="Jeff Jarvis", area="Technology & media", type="blog post",
         seeds=["buzzmachine.com/"]),
    dict(slug="robert-scoble", name="Robert Scoble", area="Technology & media", type="blog post",
         seeds=["scobleizer.com/"]),
    dict(slug="cluetrain", name="Levine, Locke, Searls & Weinberger", area="Technology & media",
         type="manifesto", seeds=["cluetrain.com/"],
         accept=r"cluetrain\.com/(book/)?[a-z0-9-]+\.html$"),

    # ---------------------------------------------------------------- sales & business development
    dict(slug="jill-konrath", name="Jill Konrath", area="Sales & business development",
         type="blog post", seeds=["jillkonrath.com/sales-blog/", "sellingtobigcompanies.blogspot.com/"]),
    dict(slug="anthony-iannarino", name="Anthony Iannarino", area="Sales & business development",
         type="blog post", seeds=["thesalesblog.com/"]),
    dict(slug="brian-carroll", name="Brian Carroll", area="Sales & business development",
         type="blog post", seeds=["blog.startwithalead.com/"]),
    dict(slug="jonathan-farrington", name="Jonathan Farrington", area="Sales & business development",
         type="blog post", seeds=["jonathanfarrington.com/", "thejfblogit.co.uk/"]),
    dict(slug="dave-brock", name="Dave Brock", area="Sales & business development", type="blog post",
         seeds=["partnersinexcellenceblog.com/"]),
    dict(slug="michael-webb", name="Michael Webb", area="Sales & business development",
         type="article", seeds=["salesperformance.com/"]),

    # ---------------------------------------------------------------- second wave
    # Chosen because their sites are still standing at their original permalinks,
    # which is what actually determines whether a pre-2012 post can be collected.
    dict(slug="seth-levine", name="Seth Levine", area="Startups & venture", type="blog post",
         seeds=["sethlevine.com/"]),
    dict(slug="mark-cuban", name="Mark Cuban", area="Management & strategy", type="blog post",
         seeds=["blogmaverick.com/"]),
    dict(slug="jason-calacanis", name="Jason Calacanis", area="Startups & venture",
         type="blog post", seeds=["calacanis.com/"]),
    dict(slug="rob-walling", name="Rob Walling", area="Startups & venture", type="blog post",
         seeds=["softwarebyrob.com/"]),
    dict(slug="patrick-mckenzie", name="Patrick McKenzie", area="Startups & venture",
         type="essay", seeds=["kalzumeus.com/", "bingocardcreator.com/"]),
    dict(slug="derek-sivers", name="Derek Sivers", area="Management & strategy", type="blog post",
         seeds=["sivers.org/"], min_chars=500),
    dict(slug="scott-berkun", name="Scott Berkun", area="Management & strategy", type="essay",
         seeds=["scottberkun.com/"]),
    dict(slug="matt-cutts", name="Matt Cutts", area="Marketing & content", type="blog post",
         seeds=["mattcutts.com/blog/"]),
    dict(slug="bill-slawski", name="Bill Slawski", area="Marketing & content", type="blog post",
         seeds=["seobythesea.com/"]),
    dict(slug="barry-schwartz", name="Barry Schwartz", area="Marketing & content",
         type="blog post", seeds=["seroundtable.com/"]),
    dict(slug="john-jantsch", name="John Jantsch", area="Marketing & content", type="blog post",
         seeds=["ducttapemarketing.com/blog/"]),
    dict(slug="garr-reynolds", name="Garr Reynolds", area="Design, UX & product",
         type="blog post", seeds=["presentationzen.com/presentationzen/"]),
    dict(slug="peter-merholz", name="Peter Merholz", area="Design, UX & product",
         type="blog post", seeds=["peterme.com/"]),
    dict(slug="christina-wodtke", name="Christina Wodtke", area="Design, UX & product",
         type="blog post", seeds=["eleganthack.com/"]),
    dict(slug="barry-ritholtz", name="Barry Ritholtz", area="Technology & media",
         type="blog post", seeds=["ritholtz.com/blog/", "ritholtz.com/"]),
    dict(slug="paul-kedrosky", name="Paul Kedrosky", area="Technology & media",
         type="blog post", seeds=["paul.kedrosky.com/"]),
    dict(slug="michael-hyatt", name="Michael Hyatt", area="Management & strategy",
         type="blog post", seeds=["michaelhyatt.com/"]),
    dict(slug="beth-kanter", name="Beth Kanter", area="Marketing & content", type="blog post",
         seeds=["bethkanter.org/", "beth.typepad.com/beths_blog/"]),
    dict(slug="gerry-mcgovern", name="Gerry McGovern", area="Marketing & content",
         type="article", seeds=["gerrymcgovern.com/"]),
    dict(slug="dave-mcclure", name="Dave McClure", area="Startups & venture", type="blog post",
         seeds=["500hats.typepad.com/", "500hats.com/"]),
    dict(slug="tim-ferriss", name="Tim Ferriss", area="Management & strategy", type="blog post",
         seeds=["fourhourworkweek.com/blog/"]),
    dict(slug="ian-lurie", name="Ian Lurie", area="Marketing & content", type="blog post",
         seeds=["portent.com/blog/", "conversationmarketing.com/"]),
]

# A permalink looks like one of these, unless the author entry says otherwise.
GENERIC_ACCEPT = [
    r"/(?:19|20)\d\d/\d\d/\d\d/[^/]+/?$",          # /2009/05/14/post-title/
    r"/(?:19|20)\d\d/\d\d/[^/]+\.html$",           # Typepad, Blogspot
    r"/(?:19|20)\d\d/\d\d/[^/]{4,}/?$",            # WordPress month permalinks
    r"/archives?/(?:19|20)\d\d/\d\d/[^/]+",
    r"/archives?/\d{3,}[^/]*$",
    r"/(?:19|20)\d\d/[a-z0-9][a-z0-9-]{6,}\.html$",
    r"/blog/[a-z0-9][a-z0-9-]{8,}\.aspx$",
    r"/When/\d\dx?x/(?:19|20)\d\d/\d\d/\d\d/[^/]+$",   # tbray.org/ongoing
]

# Index pages, feeds, and the furniture of a blog.
GENERIC_REJECT = (
    r"(?:/page/\d+|/feed|/rss|\.xml$|\.json$|/comments?/|/trackback|"
    r"/category/|/categories/|/tag/|/tags/|/author/|/archives?/?$|/search|"
    r"[?&]replytocom=|[?&]share=|/print/|/amp/?$|/wp-content/|/wp-admin/|"
    r"/comment-page-|%[0-9A-Fa-f]{2}|"
    r"\.(?:jpg|jpeg|png|gif|css|js|pdf|zip|mp3|mov|swf)$|"
    r"/index\.html?$|%20|\s|#)"
)

# A WordPress-style slug: three or more hyphenated words, which is what a post
# title becomes and what /about/ or /contact/ never does.
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+){2,}/?$"

# Sites whose permalinks carry no date, so the generic date-shaped rules above
# miss them entirely. These documents get dated from the page or the capture.
PERMALINK_SHAPES = {
    "martin-fowler":   r"martinfowler\.com/(?:bliki|articles)/[A-Za-z][A-Za-z0-9]{3,}\.html$",
    "jakob-nielsen":   r"useit\.com/alertbox/(?:\d{8}|[a-z0-9_]{4,})\.html$",
    "rand-fishkin":    r"seomoz\.org/blog/" + SLUG,
    "dharmesh-shah":   r"onstartups\.com/tabid/\d+/bid/\d+/[A-Za-z0-9-]{6,}\.aspx$",
    "david-skok":      r"forentrepreneurs\.com/" + SLUG,
    "brian-clark":     r"copyblogger\.com/" + SLUG,
    "chris-brogan":    r"chrisbrogan\.com/" + SLUG,
    "jay-baer":        r"convinceandconvert\.com/[a-z0-9-]*/?" + SLUG,
    "jill-konrath":    r"jillkonrath\.com/sales-blog/" + SLUG,
    "dave-brock":      r"partnersinexcellenceblog\.com/" + SLUG,
    "charles-green":   r"trustmatters\.trustedadvisor\.com/[a-z0-9-]*/?" + SLUG,
    "marty-cagan":     r"svpg\.com/" + SLUG,
    "simon-willison":  r"simonwillison\.net/(?:19|20)\d\d/[A-Z][a-z]{2}/\d{1,2}/[a-z0-9-]+/?$",
    "aaron-swartz":    r"aaronsw\.com/weblog/\d{6}\.html$",
    "eric-raymond":    r"catb\.org/(?:~|%7E)?esr/writings/[a-z0-9-]{4,}\.html$",
    "don-norman":      r"jnd\.org/dn\.mss/[a-z0-9_]{6,}\.html$",
    "danny-sullivan":  r"searchengineland\.com/[a-z0-9][a-z0-9-]{10,}-\d{4,6}/?$",
    "bijan-sabet":     r"bijansabet\.com/post/\d+",
    "jim-collins":     r"jimcollins\.com/(?:article_topics|lib)/[a-zA-Z0-9._-]{4,}\.html$",
}

for _a in AUTHORS:
    if _a["slug"] in PERMALINK_SHAPES:
        _a["accept"] = PERMALINK_SHAPES[_a["slug"]]
