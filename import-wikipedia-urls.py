#!/usr/bin/python

from logging import basicConfig, INFO
import sys

from wikipedia.url import WikipediaPageHandler, loadWikipediaTitles


def main(inputFilename, outputPath):
    """Load Wikipedia page titles from an XML file and write out JSON files.

    @param inputFilename: The path to the Wikipedia XML file to load data from.
    @param outputPath: The path to write JSON files to.
    """
    basicConfig(format='%(asctime)s %(levelname)8s  %(message)s', level=INFO)
    pageHandler = WikipediaPageHandler(outputPath)
    loadWikipediaTitles(inputFilename, pageHandler)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: import-wikipedia-urls INPUT_FILENAME OUTPUT_PATH"
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
