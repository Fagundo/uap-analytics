"""Page text prepared for topic modeling.

Two kinds of noise would otherwise become the topics:

* **Boilerplate**: classification stamps, routing slips, release stamps, redaction codes, form headers
  and the BAASS proprietary footer repeat on hundreds of pages. Global patterns remove the known
  ones. Within each document of 4+ pages, any word on more than half of its pages is dropped for
  that document (a letterhead or form field, not content).
* **Form pages**: control cover sheets (the CIA Top Secret signature record) are dropped whole.
* **OCR damage**: garbled tokens ('fthipple', 'tated') rarely repeat across *separate* documents. A
  token is kept when it appears in the clean reference texts (born-digital documents, passed in as
  ``reference_docs``) and in at least ``min_docs`` documents, or, outside the reference, when it is
  6+ letters long and appears in at least ``common_docs`` documents (old-file words like
  'theodolite'). Short unreferenced tokens ('tated', 'eee') are almost always OCR fragments.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from uap_analytics.replications.networks.corpus import PageText

# Markings, release and routing furniture, form vocabulary, redaction codes
_BOILERPLATE = re.compile(
    r"1843\s*\(\s*a\s*\)\s*\(\s*\d\s*\)(?:\s*\(\s*[a-z]\s*\))?|\(b\)\s*\(\s*\d\s*\)(?:\s*\(\s*[a-f]\s*\))?|"
    r"declassified|authority\s*:?\s*nn[a-z]?\s*\d+|approved for release|released in part|"
    r"this information is proprietary and confidential and cannot be disseminated or used without prior "
    r"written consent from the operating manager of baass|"
    r"\bnw\s*\d{4,}\b|docid\s*:?\s*\d+|page\s+\d+\s+of\s+\d+|"
    # the watermark The Black Vault stamps on documents it republishes
    r"(?:this document (?:was obtained|is) from )?the\s*black\s*vault(?:\.com)?[^\n]{0,160}|theblackvault\S*|"
    # the espionage-law notice stamped on 1950s forms: a marking, not content
    r"(?:this document contains )?information affecting the national (?:defen[cs]e|security).{0,400}?"
    r"(?:prohibited by law|unauthorized person)", re.I | re.S)

def strip_watermark(text: str) -> str:
    """The Black Vault prints its watermark vertically down republished pages, so OCR returns it as a
    run of one-word fragments ('TheBlackVaultist', 'helargestonlneFr', 'documentcl'). On a page that
    carries it, drop the lines that are a single token; content lines have spaces."""
    if "blackvault" not in text.replace(" ", "").lower():
        return text
    return "\n".join(line for line in text.splitlines() if len(line.split()) != 1)


# Whole pages that are control forms, not content (the CIA Top Secret cover sheet)
_FORM_PAGE = re.compile(r"signature\s+record\s+and\s+cover\s+sheet|notice\s+of\s+detachment", re.I)

STOPWORDS = frozenset("""
a about above after again against all also am an and any are as at be because been before being below
between both but by can could did do does doing down during each few for from further had has have
having he her here hers herself him himself his how i if in into is it its itself just me more most my
myself no nor not now of off on once only or other our ours ourselves out over own same she should so
some such than that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with would you your
yours yourself yourselves shall may might must upon within without also however therefore thus per via
one two three four five six seven eight nine ten first second third etc mr mrs dr gen col lt maj capt
sgt cpl pfc jr sr st no nos ref subject date dated memorandum memo letter enclosure incl inclosure
copy copies file files page pages form report reports reported item items para paragraph section
secret confidential unclassified restricted classified classification top downgraded regraded control
office officer said says say stated states made make also following attached re cc
january february march april may june july august september october november december
jan feb mar apr jun jul aug sep sept oct nov dec monday tuesday wednesday thursday friday saturday sunday
aap tho tbe thc ths tha aud aad ard wero lho ond aro ware tlie
dir exec int asst div ltr attn remarks suspense dispatched routing sheet action coord coordination
signature initials telephone tel ext extension inc incl encl
espionage revelation unauthorized prohibited
""".split())                                            # last line: OCR misreadings that repeat, and 'AAP Person' labels


# Three-letter words worth keeping; other short tokens are mostly OCR fragments ('bot', 'eee', 'ted')
SHORT_WORDS = frozenset("""
ufo uap jet mph gps cia fbi dod faa nsa dia sac adc afb sky sun red car dog saw sea air gun war hum
oak fog ice arm leg eye
""".split())


@dataclass(frozen=True)
class CleanPage:
    doc_id: str
    page: int
    tokens: tuple[str, ...]
    text: str                                  # original text, for showing typical passages
    group: str = ""                            # the collection (release) the page belongs to

    @property
    def id(self) -> tuple[str, int]:
        return self.doc_id, self.page


class PageCleaner:
    def __init__(self, min_docs: int = 2, common_docs: int = 5, min_tokens: int = 25,
                 doc_boilerplate_share: float = 0.5, min_len: int = 4, min_len_unreferenced: int = 6,
                 group_min_pages: int = 20, group_min_docs: int = 5):
        self.min_len_unreferenced = min_len_unreferenced
        self.group_min_pages, self.group_min_docs = group_min_pages, group_min_docs
        self.min_docs, self.common_docs, self.min_tokens = min_docs, common_docs, min_tokens
        self.doc_share, self.min_len = doc_boilerplate_share, min_len

    def _tokenize(self, text: str) -> list[str]:
        text = _BOILERPLATE.sub(" ", text)
        return [w for w in re.findall(r"[a-z]+", text.lower())
                if (len(w) >= self.min_len or w in SHORT_WORDS) and w not in STOPWORDS]

    def clean(self, pages: Iterable[PageText], reference_docs: set[str] | None = None,
              groups: dict[str, str] | None = None) -> list[CleanPage]:
        """``groups`` maps doc_id to its collection. A collection of many short documents (575 one-page FAA
        reports) has furniture too: words on more than half its pages are dropped, like a letterhead."""
        groups = groups or {}
        raw = [(p, self._tokenize(strip_watermark(p.text))) for p in pages if not _FORM_PAGE.search(p.text)]

        # OCR filter: in the clean reference texts and 2+ documents, or else in 5+ documents
        docs_of: dict[str, set[str]] = defaultdict(set)
        for p, toks in raw:
            for w in set(toks):
                docs_of[w].add(p.doc_id)
        reference = {w for p, toks in raw if reference_docs and p.doc_id in reference_docs for w in toks}
        vocab = {w for w, ds in docs_of.items()
                 if (w in reference and len(ds) >= self.min_docs)
                 or (len(ds) >= self.common_docs and len(w) >= self.min_len_unreferenced)}

        # per-document boilerplate: words on more than half the pages of a 4+ page document
        pages_in_doc: Counter = Counter(p.doc_id for p, _ in raw)
        word_pages: dict[str, Counter] = defaultdict(Counter)
        for p, toks in raw:
            word_pages[p.doc_id].update(set(toks))
        furniture = {d: {w for w, n in c.items() if pages_in_doc[d] >= 4 and n / pages_in_doc[d] > self.doc_share}
                     for d, c in word_pages.items()}

        # per-collection furniture, for collections of many documents
        group_pages: Counter = Counter(groups.get(p.doc_id, "") for p, _ in raw)
        group_docs: dict[str, set[str]] = defaultdict(set)
        group_words: dict[str, Counter] = defaultdict(Counter)
        for p, toks in raw:
            g = groups.get(p.doc_id, "")
            group_docs[g].add(p.doc_id)
            group_words[g].update(set(toks))
        group_furniture = {g: {w for w, n in c.items() if n / group_pages[g] > self.doc_share}
                           for g, c in group_words.items()
                           if g and group_pages[g] >= self.group_min_pages and len(group_docs[g]) >= self.group_min_docs}

        out = []
        for p, toks in raw:
            g = groups.get(p.doc_id, "")
            drop = furniture[p.doc_id] | group_furniture.get(g, set())
            kept = tuple(w for w in toks if w in vocab and w not in drop)
            if len(kept) >= self.min_tokens:
                out.append(CleanPage(p.doc_id, p.page, kept, p.text, g))
        return out
