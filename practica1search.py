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
from practica1index import MyStemmingFilter
import whoosh.index as index

class MySearcher:
    def __init__(self, index_folder, model_type = 'tfidf'):
        ix = index.open_dir(index_folder)
        if model_type == 'tfidf':
            # Apply a vector retrieval model as default
            self.searcher = ix.searcher(weighting=scoring.TF_IDF())
        else:
            # Apply the probabilistic BM25F model, the default model in searcher method
            self.searcher = ix.searcher()
        self.parser = QueryParser("content", ix.schema, group = OrGroup)

    def search(self, query_text):
        query = self.parser.parse(query_text)
        results = self.searcher.search(query, limit=100)
        if not output_file:
            print('Returned documents:')
        i = 1
        for result in results:
            if output_file:
                output.write(f'{i}\t{result.get("path")}\n')
            else:
                print(f'{i}\t{result.get("path")}')
            i += 1

if __name__ == '__main__':
    index_folder = './recordsdcindex'
    i = 1
    imput_file = False
    output_file = False
    while (i < len(sys.argv)):
        if sys.argv[i] == '-index':
            index_folder = sys.argv[i+1]
            i = i + 1
        elif sys.argv[i] == '-infoNeeds':
            imput_file = True
            sys.stdin = open(sys.argv[i+1], "r")
        elif sys.argv[i] == '-output':
            output_file = True
            output = open(sys.argv[i+1], "w")
        i = i + 1

    searcher = MySearcher(index_folder)

    #query = 'System engineering'
    if imput_file:
        query = sys.stdin.readline().strip()  
    else:
        query = input('Introduce a query: ')
    while query != 'q':
        searcher.search(query)
        if imput_file:
            query = sys.stdin.readline().strip()
            if query == '':
                break
        else:
            query = input('Introduce a query (\'q\' for exit): ')
    output.close() if output_file else None