"""
index.py
Author: Javier Nogueras Iso
Editors: Alberto Latorre Cote, Francisco Moreno Domingo
Last update: 2025-10-06

Simple program to create an inverted index with the contents of text/xml files contained in a docs folder
This program is based on the whoosh library. See https://pypi.org/project/Whoosh/ .
Usage: python index.py -index <index folder> -docs <docs folder>
"""

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import LanguageAnalyzer
from nltk.stem.snowball import SnowballStemmer
from whoosh.analysis.filters import Filter
from whoosh.analysis.tokenizers import default_pattern

import os
import datetime

import xml.etree.ElementTree as ET

def create_folder(folder_name):
    if (not os.path.exists(folder_name)):
        os.mkdir(folder_name)

def apply_stemming(words):
    # the stemmer requires a language parameter
    snow_stemmer = SnowballStemmer(language="spanish")

    # stem's of each word
    stem_words = []
    for w in words:
        x = snow_stemmer.stem(w)
        stem_words.append(x)

    # print stemming results
    #for e1, e2 in zip(words, stem_words):
    #    print(e1 + ' ----> ' + e2)

    return stem_words

class MyStemmingFilter(Filter):
    """Uses unicode.lower() to lowercase token text.

    >>> rext = RegexTokenizer()
    >>> stream = rext("This is a TEST")
    >>> [token.text for token in LowercaseFilter(stream)]
    ["this", "is", "a", "test"]
    """

    def __call__(self, tokens):
        # the stemmer requires a language parameter
        snow_stemmer = SnowballStemmer(language="spanish")

        for w in tokens:
            w.text = snow_stemmer.stem(w.text)
            yield w    
          
def MyAnalyzer(lang, expression=default_pattern, gaps=False):
    from whoosh.lang import NoStemmer, NoStopWords
    from whoosh.analysis.tokenizers import RegexTokenizer
    from whoosh.analysis.filters import LowercaseFilter
    from whoosh.analysis.filters import StopFilter

    # Make the start of the chain
    chain = (RegexTokenizer(expression=expression, gaps=gaps)
             | LowercaseFilter())

    # Add a stop word filter
    try:
        chain = chain | StopFilter(lang=lang)
    except NoStopWords:
        pass

    # Add a stemming filter
    try:
        chain = chain | MyStemmingFilter()
    except NoStemmer:
        pass

    return chain

class MyIndex:
    def __init__(self,index_folder):
        langauge_analyzer = MyAnalyzer(lang="es", expression=r"\w+")
        schema = Schema(path=ID(stored=True),
                        title=TEXT(analyzer=langauge_analyzer),
                        description=TEXT(analyzer=langauge_analyzer),
                        autor=TEXT(analyzer=langauge_analyzer),
                        director=TEXT(analyzer=langauge_analyzer),
                        departamento=TEXT(analyzer=langauge_analyzer),
                        subject=TEXT(analyzer=langauge_analyzer),
                        fecha=TEXT(analyzer=langauge_analyzer))
        create_folder(index_folder)
        index = create_in(index_folder, schema)
        self.writer = index.writer()

    def index_docs(self,docs_folder):
        if (os.path.exists(docs_folder)):
            for file in sorted(os.listdir(docs_folder)):
                # print(file)
                if file.endswith('.xml'):
                    self.index_xml_doc(docs_folder, file)
        self.writer.commit()

    def index_xml_doc(self, foldername, filename):
        file_path = os.path.join(foldername, filename)
        # print(file_path)
        tree = ET.parse(file_path)
        root = tree.getroot()
        raw_text = "".join(root.itertext())
        # break into lines and remove leading and trailing space on each
        text = ' '.join(line.strip() for line in raw_text.splitlines() if line)
        # print(text)

        
        # Obtener el diccionario de namespaces
        namespaces = dict([
            node for _, node in ET.iterparse(file_path, events=['start-ns'])
        ])

        # Mostrar la URI asociada al prefijo 'dc'
        dc_uri = namespaces.get('dc')


        id = ""
        title = ""
        description = ""
        autor = ""
        director = ""
        fecha = ""
        subject = ""
        departamento = ""
        for child in root:
            if child.tag == f'{{{dc_uri}}}identifier':
                if child.text: id += child.text
            if child.tag == f'{{{dc_uri}}}title':    
                lang = child.attrib.get('{http://www.w3.org/XML/1998/namespace}lang')
                # Aceptar si el idioma no es inglés o si no se especifica
                if (lang is None or not lang.startswith('en')) and child.text:
                    title += child.text

            if child.tag == f'{{{dc_uri}}}description':
                if child.text: description += child.text
            if child.tag == f'{{{dc_uri}}}creator':
                if child.text: autor += child.text
            if child.tag == f'{{{dc_uri}}}contributor':
                if child.text: director += child.text
            if child.tag == f'{{{dc_uri}}}creator':
                if child.text: autor += child.text
            if child.tag == f'{{{dc_uri}}}date':
                if child.text: fecha += child.text
            if child.tag == f'{{{dc_uri}}}publisher':
                if child.text: departamento += child.text
            if child.tag == f'{{{dc_uri}}}subject':
                if child.text: subject += child.text
            

        self.writer.add_document(path=id,
                                 title=title,
                                 description=description,
                                 autor=autor,
                                 director=director,
                                 subject=subject,
                                 fecha=fecha,
                                 departamento=departamento,)

if __name__ == '__main__':

    index_folder = 'recordsdcindex'
    docs_folder = 'recordsdc'
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-index':
            index_folder = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-docs':
            docs_folder = sys.argv[i + 1]
            i = i + 1
        i = i + 1

    my_index = MyIndex(index_folder)
    my_index.index_docs(docs_folder)