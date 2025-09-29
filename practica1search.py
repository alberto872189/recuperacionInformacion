"""
search.py
Author: Javier Nogueras Iso
Last update: 2024-09-07

Program to search a free text query on a previously created inverted index.
This program is based on the whoosh library. See https://pypi.org/project/Whoosh/ .
Usage: python search.py -index <index folder>
"""

import sys

from whoosh.qparser import QueryParser
from whoosh.qparser import OrGroup
from whoosh import scoring
import whoosh.index as index

class MySearcher:
    def __init__(self, index_folder, show_info, model_type = 'tfidf'):
        ix = index.open_dir(index_folder)
        self.show_info = show_info
        if model_type == 'tfidf':
            # Apply a vector retrieval model as default
            self.searcher = ix.searcher(weighting=scoring.TF_IDF())
        else:
            # Apply the probabilistic BM25F model, the default model in searcher method
            self.searcher = ix.searcher()
        self.parser = QueryParser("content", ix.schema, group = OrGroup)

    def search(self, query_text):
        query = self.parser.parse(query_text)
        results = self.searcher.search(query)
        print('Returned documents:')
        i = 1
        for result in results:
            print(f'{i} - File path: {result.get("path")}, Similarity score: {result.score}')
            if (self.show_info): print(f'Modified: {result.get("fecha_modificacion")}')
            i += 1

if __name__ == '__main__':
    index_folder = '../whooshindex'
    i = 1
    show_info = False
    while (i < len(sys.argv)):
        if sys.argv[i] == '-index':
            index_folder = sys.argv[i+1]
            i = i + 1
        elif sys.argv[i] == '-info':
            show_info = True
        i = i + 1

    searcher = MySearcher(index_folder, show_info)

    #query = 'System engineering'
    query = input('Introduce a query: ')
    while query != 'q':
        searcher.search(query)
        query = input('Introduce a query (\'q\' for exit): ')