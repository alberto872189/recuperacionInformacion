"""
search.py
Author: Javier Nogueras Iso
Last update: 2024-09-07

Program to search a free text query on a previously created inverted index.
This program is based on the whoosh library. See https://pypi.org/project/Whoosh/ .
Usage: python search.py -index <index folder>
"""

import sys

from whoosh.qparser import QueryParser, MultifieldParser
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
        fields = ["autor", "director", "departamento", "title", "descripcion", "subject", "fecha"]
        self.parser = MultifieldParser(fields, schema=ix.schema, group=OrGroup)

    def search(self, query_text, output_file=None):
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
    input_file = None
    output_file = None
    output = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-index':
            index_folder = sys.argv[i + 1]
            i += 1
        elif sys.argv[i] == '-infoNeeds':
            input_file = sys.argv[i + 1]
            sys.stdin = open(input_file, "r")
            i += 1
        elif sys.argv[i] == '-output':
            output_file = sys.argv[i + 1]
            output = open(output_file, "w")
            i += 1
        i += 1

    searcher = MySearcher(index_folder)

    if input_file:
        query = sys.stdin.readline().strip()
    else:
        query = input("Introduce a query: ")

    while query != 'q':
        searcher.search(query, output_file=output)
        if input_file:
            query = sys.stdin.readline().strip()
            if query == '':
                break
        else:
            query = input("Introduce a query ('q' for exit): ")

    if output:
        output.close()
