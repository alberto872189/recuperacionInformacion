"""
index.py
Author: Javier Nogueras Iso
Last update: 2024-09-07

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
                        fecha_modificacion=STORED,
                        title=TEXT,
                        description=TEXT,
                        autor=TEXT,
                        director=TEXT,
                        departamento=TEXT,
                        fecha=TEXT,
                        content=TEXT(analyzer=langauge_analyzer))
        create_folder(index_folder)
        index = create_in(index_folder, schema)
        self.writer = index.writer()

    def index_docs(self,docs_folder):
        if (os.path.exists(docs_folder)):
            for file in sorted(os.listdir(docs_folder)):
                # print(file)
                if file.endswith('.xml'):
                    self.index_xml_doc(docs_folder, file)
                elif file.endswith('.txt'):
                    self.index_txt_doc(docs_folder, file)
        self.writer.commit()

    def index_txt_doc(self, foldername,filename):
        file_path = os.path.join(foldername, filename)
        # print(file_path)
        with open(file_path) as fp:
            text = ' '.join(line for line in fp if line)
        # print(text)
        self.writer.add_document(path=filename,
                                 fecha_modificacion=datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                                 content=text)

    def index_xml_doc(self, foldername, filename):
        file_path = os.path.join(foldername, filename)
        # print(file_path)
        tree = ET.parse(file_path)
        root = tree.getroot()
        raw_text = "".join(root.itertext())
        # break into lines and remove leading and trailing space on each
        text = ' '.join(line.strip() for line in raw_text.splitlines() if line)
        # print(text)

        title = ""
        description = ""
        autor = ""
        director = ""
        fecha = ""
        departamento = ""
        for child in root:
            if child.tag == '{http://www.openarchives.org/OAI/2.0/oai_dc/}title':
                if child.text: title += child.text
            if child.tag == '{http://www.openarchives.org/OAI/2.0/oai_dc/}description':
                if child.text: description += child.text
            if child.tag == '{http://www.openarchives.org/OAI/2.0/oai_dc/}creator':
                if child.text: autor += child.text
            if child.tag == '{http://www.openarchives.org/OAI/2.0/oai_dc/}contributor':
                if child.text: director += child.text
            if child.tag == '{http://www.openarchives.org/OAI/2.0/oai_dc/}creator':
                if child.text: autor += child.text
            if child.tag == '{http://www.openarchives.org/OAI/2.0/oai_dc/}date':
                if child.text: fecha += child.text
            if child.tag == '{http://www.openarchives.org/OAI/2.0/oai_dc/}publisher':
                if child.text: departamento += child.text
            

        self.writer.add_document(path=filename,
                                 fecha_modificacion=datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                                 title=title,
                                 description=description,
                                 autor=autor,
                                 director=director,
                                 fecha=fecha,
                                 departamento=departamento,
                                 content=text)

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