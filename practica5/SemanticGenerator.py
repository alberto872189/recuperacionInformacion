import os
import sys
import time
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import xml.etree.ElementTree as ET
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS, RDF, XSD, Namespace

from re import sub

# Define a function to convert a string to camel case
def camel_case(s):
    # Use regular expression substitution to replace underscores and hyphens with spaces,
    # then title case the string (capitalize the first letter of each word), and remove spaces
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    
    # Join the string, ensuring the first letter is lowercase
    return ''.join([s[0].lower(), s[1:]])

# Configuración del servicio FUSEKI
FUSEKI_HOST = 'http://localhost:3030'
DATASET_NAME = 'datasetExample3'
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'
ENDPOINT = f'{FUSEKI_HOST}/{DATASET_NAME}/sparql'
BASE_URI = 'http://miuri/xd/'
BASE_URI_ACADEMICWORK = 'http://miuri/xd/AcademicWork'
BASE_URI_TFG = 'http://miuri/xd/TFG'
BASE_URI_TFM = 'http://miuri/xd/TFM'
BASE_URI_TESIS = 'http://miuri/xd/Tesis'
BASE_URI_PERSONA = 'http://miuri/xd/Persona'
BASE_URI_SUBJECT = 'http://miuri/xd/Subject'
BASE_URI_PUBLISHER = 'http://miuri/xd/Publisher'

rdf_path = './schema.ttl'
docs_path = '../recordsdc'

i = 1
while i < len(sys.argv):
    if sys.argv[i] == '-docs':
        docs_path = sys.argv[i + 1]
        i += 1
    elif sys.argv[i] == '-rdf':
        rdf_path = sys.argv[i + 1]
        i += 1
    i += 1

model = Graph()
model.bind("mi", Namespace(BASE_URI))

for doc in os.scandir(docs_path):
    file_path = doc.path
    tree = ET.parse(file_path)
    root = tree.getroot()
    raw_text = "".join(root.itertext())
    # break into lines and remove leading and trailing space on each
    text = ' '.join(line.strip() for line in raw_text.splitlines() if line)

    # Obtener el diccionario de namespaces
    namespaces = dict([
        node for _, node in ET.iterparse(file_path, events=['start-ns'])
    ])

    # Mostrar la URI asociada al prefijo 'dc'
    dc_uri = namespaces.get('dc')
    doc_type = ''
    title = ''
    description = ''
    subject = -1
    contributor = ''
    creator = ''
    date = ''
    identifier = ''
    language = ''
    publisher = ''
    relation = ''
    rights = ''

    solved = False
    for child in root:
        if child.tag == f'{{{dc_uri}}}type':
            if child.text: doc_type += child.text
        if child.tag == f'{{{dc_uri}}}description':
            if child.text: description += child.text
        if child.tag == f'{{{dc_uri}}}title':
            if child.text: title += child.text
        if child.tag == f'{{{dc_uri}}}subject':
            if child.text: subject += child.texts
        if child.tag == f'{{{dc_uri}}}contributor':
            if child.text: contributor += child.texts
        if child.tag == f'{{{dc_uri}}}creator':
            if child.text: creator += child.texts
        if child.tag == f'{{{dc_uri}}}date':
            if child.text: date += child.texts
        if child.tag == f'{{{dc_uri}}}identifier':
            if child.text: identifier += child.texts
        if child.tag == f'{{{dc_uri}}}language':
            if child.text: language += child.texts
        if child.tag == f'{{{dc_uri}}}publisher':
            if child.text: publisher += child.texts
        if child.tag == f'{{{dc_uri}}}relation':
            if child.text: relation += child.texts
        if child.tag == f'{{{dc_uri}}}rights':
            if child.text: rights += child.texts

    base_doc_uri = BASE_URI_TFG if doc_type == 'TAZ-TFG' else BASE_URI_TFM if doc_type == 'TAZ-TFM' else BASE_URI_TESIS if doc_type == 'TESIS' else BASE_URI_ACADEMICWORK
    doc_uri = URIRef(base_doc_uri + identifier) #TODO POSIBLEMENTE ESTO ESTA MAL

    creator_uri = URIRef(BASE_URI_PERSONA + camel_case(creator))
    model.add((creator_uri, RDF.type, BASE_URI_PERSONA))
    model.add((creator_uri, URIRef(BASE_URI + "namePersona"), Literal(creator)))
    
    contributor_uri = URIRef(BASE_URI_PERSONA + camel_case(contributor))
    model.add((contributor_uri, RDF.type, BASE_URI_PERSONA))
    model.add((contributor_uri, URIRef(BASE_URI + "namePersona"), Literal(contributor)))

    publisher_uri = URIRef(BASE_URI_PUBLISHER + camel_case(publisher))
    model.add((publisher_uri, RDF.type, BASE_URI_PUBLISHER))
    model.add((publisher_uri, URIRef(BASE_URI + "namePublisher"), Literal(publisher)))
    
    model.add((doc_uri, URIRef(BASE_URI + "title"), Literal(title)))
    model.add((doc_uri, URIRef(BASE_URI + "date"), XSD.gYear(date)))
    model.add((doc_uri, URIRef(BASE_URI + "description"), Literal(description)))
    model.add((doc_uri, URIRef(BASE_URI + "langauge"), XSD.language(language)))
    model.add((doc_uri, URIRef(BASE_URI + "relation"), XSD.anyURI(relation)))
    model.add((doc_uri, URIRef(BASE_URI + "license"), XSD.anyURI(rights)))
    model.add((doc_uri, URIRef(BASE_URI + "creator"), creator_uri))
    model.add((doc_uri, URIRef(BASE_URI + "contributor"), contributor_uri))
    model.add((doc_uri, URIRef(BASE_URI + "publisher"), publisher_uri))
    model.add((doc_uri, URIRef(BASE_URI + "subject"), Literal(subject))) #TODO cambiar
