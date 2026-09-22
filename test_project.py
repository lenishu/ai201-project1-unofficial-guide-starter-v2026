"""Focused regression checks for chunk integrity and the relevance gate."""
import unittest
from unittest.mock import patch
import config
from ingest import Document, clean_text
from chunker import split_documents
from gate import check
from store import Result


class ChunkingTests(unittest.TestCase):
    def test_heading_and_topic_boundaries(self):
        chunks = split_documents([Document('dining.txt', 'Commons\n\nLunch takes twenty minutes.\n\nDinner closes at eight.')])
        self.assertEqual([c.text for c in chunks], ['Commons\n\nLunch takes twenty minutes.', 'Commons\n\nDinner closes at eight.'])
        self.assertEqual([c.label for c in chunks], ['dining.txt#0', 'dining.txt#1'])
        self.assertTrue(all(c.produced_by == 'chunker.py::split_documents' for c in chunks))

    def test_long_paragraph_splits_at_sentence_boundary(self):
        sentences = ['The first sentence has useful information.', 'The second sentence concerns a different detail.', 'The last sentence must survive.']
        with patch.object(config, 'CHUNK_SIZE', 65):
            chunks = split_documents([Document('long.txt', ' '.join(sentences))])
        self.assertEqual([c.text for c in chunks], sentences)
        self.assertEqual(' '.join(c.text for c in chunks), ' '.join(sentences))

    def test_overlong_sentence_is_not_cut_or_lost(self):
        sentence = 'An unusually long sentence ' + 'with information ' * 40 + 'ends here.'
        chunks = split_documents([Document('long.txt', sentence)])
        self.assertEqual([c.text for c in chunks], [sentence])

    def test_empty_and_title_only_documents(self):
        chunks = split_documents([Document('empty.txt', ' \n\n '), Document('title.txt', 'Only a title')])
        self.assertEqual([c.text for c in chunks], ['Only a title'])
        self.assertEqual(chunks[0].source, 'title.txt')

    def test_cleaning_preserves_paragraph_structure(self):
        self.assertEqual(clean_text('Title\r\n\r\n\r\nBody\t\ttext.  '), 'Title\n\nBody text.')

    def test_bad_size_is_rejected(self):
        with patch.object(config, 'CHUNK_SIZE', 0), self.assertRaises(ValueError):
            split_documents([Document('a.txt', 'Some text.')])


class GateTests(unittest.TestCase):
    def result(self, distance):
        return Result('Fact.', 'a.txt', 'a.txt#0', distance, 'chunker.py::split_documents')

    def test_threshold_is_strict_and_empty_results_refuse(self):
        self.assertFalse(check([], 0.6).passed)
        self.assertFalse(check([self.result(0.6)], 0.6).passed)
        self.assertTrue(check([self.result(0.59)], 0.6).passed)
        self.assertFalse(check([self.result(0.7)], 0.6).passed)


if __name__ == '__main__':
    unittest.main()
