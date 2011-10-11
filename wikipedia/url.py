from json import dump
import os
from xml.sax import ContentHandler, parse


class WikipediaPage(object):
    """Metadata about a Wikipedia page.

    @param title: The title of the article.
    @param redirectTitle: Optionally, the title of the page to redirect to
        when this page is visited.
    """

    def __init__(self, title, redirectTitle=None):
        self.title = title
        self.redirectTitle = redirectTitle


def loadWikipediaTitles(path, pageHandler):
    """Generator loads and yields L{WikipediaPage} instances from a file.

    @param path: The path to a Wikipedia XML file.
    @param pageHandler: A handler class that will be called whenever a
        L{WikipediaPage} is generated.
    """
    contentHandler = WikipediaContentHandler(pageHandler)
    with open(path, 'r') as xmlFile:
        parse(xmlFile, contentHandler)


class WikipediaContentHandler(ContentHandler):
    """A SAX parsing handler for a Wikipedia XML document."""

    def __init__(self, pageHandler):
        self._currentElement = None
        self._currentPage = None
        self._pageHandler = pageHandler

    def startElement(self, name, attributes):
        """Handle a start element.

        @param name: The name of the element.
        @param attributes: The attributes defined for the element.
        """
        self._currentElement = name
        if name == 'page':
            self._currentPage = {'title': [], 'text': []}

    def characters(self, content):
        """Handle textual content.

        Note: This method may be called more than once for a single block of
            text.

        @param content: The textual content retrieved from the XML document.
        """
        if self._currentPage is not None:
            if self._currentElement == 'title':
                self._currentPage['title'].append(content)
            elif self._currentElement == 'text':
                self._currentPage['text'].append(content)

    def endElement(self, name):
        """Handle an end element.

        @param name: The name of the element.
        """
        if name == 'page':
            title = ''.join(self._currentPage['title']).strip()
            text = ''.join(self._currentPage['text'])
            redirectTitle = None
            if text.startswith('#REDIRECT'):
                start = text.find('[[') + 2
                end = text.find(']]')
                redirectTitle = text[start:end]
            self._pageHandler.handle(WikipediaPage(title, redirectTitle))
            self._currentPage = None

    def endDocument(self):
        """Handle the end of the XML document."""
        self._pageHandler.close()


class WikipediaPageHandler(object):
    """Handler converts L{WikipediaPage} instances into Fluidinfo objects.

    @param path: The directory to write JSON files to.
    @param batchSize: The maximum number of objects to write to a particular
        JSON file.  Default is 10000.
    """

    filenameTemplate = 'wikipedia-titles-%05d.json'

    def __init__(self, path, batchSize=None):
        self._path = path
        self._batchSize = batchSize or 10000
        self._currentBatch = 1
        self._pages = []

    def handle(self, page):
        """Convert a L{WikipediaPage} into a Fluidinfo object.

        @param page: The L{WikipediaPage} instance to process.
        """
        data = {'about': page.title.lower(),
                'values': {'wikipedia.com/title': page.title}}
        if page.redirectTitle is not None:
            data['values']['wikipedia.com/related'] = page.redirectTitle
        self._pages.append(data)
        if len(self._pages) == self._batchSize:
            self._flush()

    def close(self):
        """Finalize L{WikipediaPage} handling."""
        if self._pages:
            self._flush()

    def _flush(self):
        """Write stored objects to disk and flush the cache."""
        filename = self.filenameTemplate % self._currentBatch
        path = os.path.join(self._path, filename)
        with open(path, 'w') as file:
            dump({'objects': self._pages}, file)
        self._currentBatch += 1
        self._pages = []
