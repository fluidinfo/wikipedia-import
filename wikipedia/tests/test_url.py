from json import load
import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from twisted.python.util import sibpath

from wikipedia.url import (
    WikipediaPage, WikipediaPageHandler, loadWikipediaTitles)


class SampleWikipedaPageHandler(object):
    """Dummy handler keeps tracks of method calls."""

    def __init__(self):
        self.pages = []
        self.closed = False

    def handle(self, page):
        """Handle a L{WikipediaPage} instance."""
        self.pages.append(page)

    def close(self):
        """Finalize handling."""
        self.closed = True


class LoadWikipediaTitlesTest(TestCase):

    def setUp(self):
        super(LoadWikipediaTitlesTest, self).setUp()
        self.pageHandler = SampleWikipedaPageHandler()

    def testLoadWikipediaTitles(self):
        """
        L{loadWikipediaTitles} yields a L{WikipediaPage} instance for each
        C{page} element in the specified XML file.
        """
        path = sibpath(__file__, 'basic.xml')
        loadWikipediaTitles(path, self.pageHandler)
        [page] = self.pageHandler.pages
        self.assertEqual('Anaconda', page.title)

    def testLoadWikipediaTitlesClosesPageHandler(self):
        """
        The C{close} method on the page handler will be called when
        L{loadWikipediaTitles} finishes parsing the XML document.
        """
        path = sibpath(__file__, 'basic.xml')
        loadWikipediaTitles(path, self.pageHandler)
        self.assertTrue(self.pageHandler.closed)


class WikipediaPageHandlerTest(TestCase):

    def setUp(self):
        super(WikipediaPageHandlerTest, self).setUp()
        self.outputPath = mkdtemp()
        self.handler = WikipediaPageHandler(self.outputPath)

    def tearDown(self):
        rmtree(self.outputPath)
        super(WikipediaPageHandlerTest, self).tearDown()

    def testCloseWithoutPages(self):
        """
        L{WikipediaPageHandler.close} is a no-op if no pages have been
        generated.
        """
        self.handler.close()
        self.assertEqual([], os.listdir(self.outputPath))

    def testCloseFlushesPages(self):
        """
        L{WikipediaPageHandler.close} flushes any pages that have not yet been
        written to disk.
        """
        self.handler.handle(WikipediaPage('Sample page'))
        self.handler.close()
        path = os.path.join(self.outputPath, 'wikipedia-titles-00001.json')
        with open(path, 'r') as file:
            data = load(file)
        self.assertEqual(
            {'objects': [{'about': 'sample page',
                          'values': {'wikipedia.org/title': 'Sample page'}}]},
            data)

    def testFlushBatches(self):
        """
        L{WikipediaPageHandler} automatically flushes cached data to disk,
        when the batch size is reached.
        """
        handler = WikipediaPageHandler(self.outputPath, batchSize=1)
        handler.handle(WikipediaPage('Sample page 1'))
        self.assertEqual(['wikipedia-titles-00001.json'],
                         os.listdir(self.outputPath))
        handler.handle(WikipediaPage('Sample page 2'))
        self.assertEqual(['wikipedia-titles-00001.json',
                          'wikipedia-titles-00002.json'],
                         sorted(os.listdir(self.outputPath)))
