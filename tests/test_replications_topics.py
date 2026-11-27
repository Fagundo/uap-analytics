"""Topics replication: page cleaning, themes, prevalence tests (ported unchanged with the code)."""
import unittest

import numpy as np

from uap_analytics.replications.topics.text import PageCleaner, strip_watermark
from uap_analytics.replications.topics.themes import Theme, ThemeScorer
from uap_analytics.replications.topics.report import TopicLabeler
from uap_analytics.replications.topics.model import PrevalenceAnalyzer, Topic, benjamini_hochberg
from uap_analytics.replications.networks.corpus import PageText


def _page(doc, n, text):
    return PageText(doc, n, text)


FILLER = "radar operators tracked the target across the evening while pilots reported bright lights moving fast "


class PageCleanerTest(unittest.TestCase):
    def test_markings_forms_and_ocr_fragments_are_removed(self):
        stamp = ("WARNING This document contains information affecting the national security of the United States "
                 "within the meaning of the espionage laws ... to an unauthorized person ")
        pages = [_page(f"D{i}", 1, FILLER * 3 + ("1843(a)(2) tated eee" if i > 1 else "")) for i in range(6)]
        pages.append(_page("D9", 1, stamp + FILLER * 3))
        pages.append(_page("D9", 2, "SIGNATURE RECORD AND COVER SHEET Access to Top Secret matter " + FILLER * 3))
        clean = PageCleaner(min_tokens=5).clean(pages, reference_docs={"D0", "D1"})
        words = {w for p in clean for w in p.tokens}
        self.assertNotIn("espionage", words)
        self.assertNotIn("tated", words)                    # short, not in the clean reference
        self.assertNotIn("eee", words)
        self.assertIn("radar", words)
        self.assertNotIn(("D9", 2), [p.id for p in clean])  # the cover sheet page is dropped whole

    def test_words_on_most_pages_of_a_document_are_furniture(self):
        pool = FILLER.split()
        body = lambda n: " ".join(pool[n:] + pool[:n][:3])          # each page differs, shares letterhead
        pages = [_page("D1", n, f"letterhead acme bureau {' '.join(pool[(3 * n) % len(pool):][:6])}")
                 for n in range(1, 6)]
        pages += [_page(f"D{i}", 1, f"letterhead acme bureau {body(i)}") for i in range(2, 5)]
        clean = PageCleaner(min_tokens=3).clean(pages, reference_docs={"D2", "D3", "D4"})
        d1 = [p for p in clean if p.doc_id == "D1"]
        self.assertTrue(d1 and all("letterhead" not in p.tokens for p in d1))

    def test_words_on_most_pages_of_a_collection_are_furniture(self):
        pool = FILLER.split()
        pages = [_page(f"F{i}", 1, f"airspace facility {' '.join((pool * 2)[i % len(pool):][:5])}")
                 for i in range(25)]                                   # 25 one-page documents, one form
        groups = {f"F{i}": "faa" for i in range(25)}
        kw = dict(min_tokens=3, group_min_pages=20, group_min_docs=5)
        with_groups = PageCleaner(**kw).clean(pages, reference_docs=set(groups), groups=groups)
        without = PageCleaner(**kw).clean(pages, reference_docs=set(groups))
        self.assertTrue(all("airspace" in p.tokens for p in without))   # one-page documents: no per-doc furniture
        self.assertTrue(with_groups and all("airspace" not in p.tokens for p in with_groups))
        self.assertTrue(all(p.group == "faa" for p in with_groups))

    def test_watermark_fragments_are_dropped_only_on_watermarked_pages(self):
        marked = "The radar return was strong\nTheBlackVaultist\nhelargestonlneFr\nIt faded after ten minutes"
        self.assertEqual(strip_watermark(marked), "The radar return was strong\nIt faded after ten minutes")
        plain = "SECRET\nThe radar return was strong"
        self.assertEqual(strip_watermark(plain), plain)


class ThemeTest(unittest.TestCase):
    def test_prefix_and_exact_matching(self):
        th = Theme("press", ("newspaper",), frozenset({"press"}))
        self.assertTrue(th.matches("press") and th.matches("newspapers"))
        self.assertFalse(th.matches("pressure"))

    def test_score_is_share_of_words(self):
        from uap_analytics.replications.topics.text import CleanPage
        p = CleanPage("D", 1, ("radar", "film", "lights", "night"), "")
        m = ThemeScorer((Theme("instruments", ("radar", "film")),)).score([p])
        self.assertEqual(m.tolist(), [[0.5]])


class PrevalenceTest(unittest.TestCase):
    def test_group_difference_is_found_and_counted_per_document(self):
        pages, rows, eras = [], [], {}
        for d in range(12):
            doc = f"D{d}"
            eras[doc] = "1960s" if d < 4 else "1950s"
            for n in range(1 if d else 40):                  # D0 has 40 pages: still one document
                pages.append((doc, n + 1))
                rows.append([0.9, 0.1] if d < 4 else [0.2, 0.8])
        diffs = PrevalenceAnalyzer(permutations=500).differences(pages, np.array(rows), "era", eras)
        d = next(x for x in diffs if x.group == "1960s" and x.measure == 1)
        self.assertTrue(d.significant)
        self.assertEqual(d.docs, 4)
        self.assertAlmostEqual(d.group_share, 0.9)          # D0's 40 pages don't outvote the others

    def test_undated_documents_are_left_out_of_the_comparison(self):
        pages, rows, eras = [], [], {}
        for d in range(30):
            doc = f"D{d}"
            eras[doc] = "1960s" if d < 4 else "1950s" if d < 8 else "undated"
            pages.append((doc, 1))
            rows.append([0.9, 0.1] if d < 4 else [0.5, 0.5] if d < 8 else [0.0, 1.0])
        diffs = PrevalenceAnalyzer(permutations=200).differences(pages, np.array(rows), "era", eras)
        self.assertNotIn("undated", {x.group for x in diffs})
        d = next(x for x in diffs if x.group == "1960s" and x.measure == 1)
        self.assertEqual(d.docs, 4)
        self.assertAlmostEqual(d.group_share - d.rest_share, 0.4)    # against 1950s only, not the undated pile

    def test_benjamini_hochberg(self):
        self.assertEqual([round(q, 3) for q in benjamini_hochberg([0.01, 0.04, 0.03, 0.5])],
                         [0.04, 0.053, 0.053, 0.5])


class LabelerTest(unittest.TestCase):
    def test_label_applies_only_when_key_words_match(self):
        lab = TopicLabeler([{"label": "Space-vehicle fragments policy", "words": ["vehicles", "launched"]}])
        self.assertEqual(lab.label(Topic(1, ["vehicles", "dod", "launched"], [1, 1, 1])),
                         "Space-vehicle fragments policy")
        self.assertIsNone(lab.label(Topic(2, ["witness", "lights"], [1, 1])))


if __name__ == "__main__":
    unittest.main()
