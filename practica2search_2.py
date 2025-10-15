"""
search.py
Author: Javier Nogueras Iso
Editors: Alberto Latorre Cote, Francisco Moreno Domingo
Last update: 2025-10-06

Program to search a free text query on a previously created inverted index.
This program is based on the whoosh library. See https://pypi.org/project/Whoosh/ .
Usage: python search.py -index <index folder>
"""

import sys

from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser import OrGroup
from whoosh import scoring
from index import MyStemmingFilter
import whoosh.index as index
import xml.etree.ElementTree as ET
import spacy
import es_core_news_sm

class MySearcher:
    def __init__(self, index_folder, model_type = 'tfidf'):
        ix = index.open_dir(index_folder)
        if model_type == 'tfidf':
            # Apply a vector retrieval model as default
            self.searcher = ix.searcher(weighting=scoring.TF_IDF())
        else:
            # Apply the probabilistic BM25F model, the default model in searcher method
            self.searcher = ix.searcher()
        fields = ["autor", "director", "departamento", "title", "description", "subject", "fecha"]
        self.parser = MultifieldParser(fields, schema=ix.schema, group=OrGroup)

    def extract_keywords(text, nlp):
        doc = nlp(text)
        keywords = set()
        for ent in doc.ents:
            keywords.add(ent.text)
        for token in doc:
            if not token.is_stop and not token.is_punct and token.is_alpha:
                keywords.add(token.lemma_)
        return list(keywords)

    def search(self, query_text, i, output_file=None):
        nlp = es_core_news_sm.load()
        text = (query_text)
        doc = nlp(text)

        keywords = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN") and not token.is_stop]
        doc = nlp(text)

        keywords_string = ""
        
        for keyword in keywords:
            if any(subcadena in keyword for subcadena in ["trabaj", "grado", "estudi", "universidad", "curs", "curso", "master", "doctorad", "doctorado", "investig", "investigacion", "proyect", "proyecto"]):
                continue
            keywords_string += keyword + " "
        print(keywords_string)
        query = self.parser.parse(keywords_string)
        results = self.searcher.search(query, limit=100)
        if not output_file:
            print('Returned documents:')
        for result in results:
            if output_file:
                output.write(f'{i}\t{result.get("path")}\n')
            else:
                print(f'{i}\t{result.get("path")}')


if __name__ == '__main__':
    
    index_folder = './recordsdcindex'
    input_file = None
    output_file = None
    output = None
    data = []

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-index':
            index_folder = sys.argv[i + 1]
            i += 1
        elif sys.argv[i] == '-infoNeeds':
            input_file = True
            file_path = sys.argv[i + 1]
            # print(file_path)
            tree = ET.parse(file_path)
            root = tree.getroot()
            raw_text = "".join(root.itertext())
            # break into lines and remove leading and trailing space on each
            text = ' '.join(line.strip() for line in raw_text.splitlines() if line)
            # print(text)
            for need in root.findall("informationNeed"):
                identifier = need.find("identifier").text
                text = need.find("text").text
                data.append({"identifier": identifier, "text": text})
            i += 1
        elif sys.argv[i] == '-output':
            output_file = sys.argv[i + 1]
            output = open(output_file, "w")
            i += 1
        i += 1

    searcher = MySearcher(index_folder)

    if not input_file:
        query = input("Introduce a query: ")

    if not input_file:
        i = 1
        while query != 'q':
            searcher.search(query, i, output_file=output)
            query = input("Introduce a query ('q' for exit): ")
            i += 1
    else:
        for item in data:
            query = item["text"]
            id = item["identifier"]
            searcher.search(query, id, output_file=output)
    if output:
        output.close()





