import os
import sys
import time
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import xml.etree.ElementTree as ET
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS, RDF, XSD, Namespace
#from owlrl import DeductiveClosure, OWLRL_Semantics

from re import sub
import unicodedata, re

# Define a function to convert a string to camel case
def camel_case(s):
    if not s:
        return s
    # quitar comillas dobles
    s = s.replace('"', '')
    # reemplazar guiones/underscores por espacios, capitalizar y eliminar espacios
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    if not s:
        return s
    s = s[0].lower() + s[1:]
    # normalizar y quitar diacríticos (á, ñ, etc.)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    # quitar cualquier caracter que no sea letra o número
    s = re.sub(r'[^A-Za-z0-9]', '', s)
    return s

BASE_URI = 'http://miuri/xd#'
BASE_URI_ACADEMICWORK = 'http://miuri/xd#AcademicWork'
BASE_URI_TFG = 'http://miuri/xd#TFG'
BASE_URI_TFM = 'http://miuri/xd#TFM'
BASE_URI_TESIS = 'http://miuri/xd#Tesis'
BASE_URI_PERSONA = 'http://miuri/xd#Persona'
BASE_URI_SUBJECT = 'http://miuri/xd#Subject'
BASE_URI_PUBLISHER = 'http://miuri/xd#Publisher'
rdf_path = './zaguan.ttl'
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
    title = []
    description = []
    subject = []
    contributor = []
    creator = []
    date = []
    identifier = ''
    language = []
    publisher = []
    relation = []
    rights = []

    

    solved = False
    for child in root:
        if child.tag == f'{{{dc_uri}}}type':
            if child.text: doc_type += child.text
        if child.tag == f'{{{dc_uri}}}description':
            if child.text: description.append(child.text)
            
        if child.tag == f'{{{dc_uri}}}title':
            if child.text: title.append(child.text)
        if child.tag == f'{{{dc_uri}}}subject':
            if child.text: 
                subject.append(child.text)
        if child.tag == f'{{{dc_uri}}}contributor':
            if child.text: contributor.append(child.text)
        if child.tag == f'{{{dc_uri}}}creator':
            if child.text: creator.append(child.text)
        if child.tag == f'{{{dc_uri}}}date':
            if child.text: date.append(child.text)
        if child.tag == f'{{{dc_uri}}}identifier':
            if child.text: identifier = child.text
        if child.tag == f'{{{dc_uri}}}language':
            if child.text: language.append(child.text)
        if child.tag == f'{{{dc_uri}}}publisher':
            if child.text: publisher.append(child.text)
        if child.tag == f'{{{dc_uri}}}relation':
            if child.text: relation.append(child.text)
        if child.tag == f'{{{dc_uri}}}rights':
            if child.text: rights.append(child.text)


    base_doc_uri = BASE_URI_TFG if doc_type == 'TAZ-TFG' else BASE_URI_TFM if doc_type == 'TAZ-TFM' else BASE_URI_TESIS if doc_type == 'TESIS' else BASE_URI_ACADEMICWORK
    clean_id = identifier.strip().replace("\n", "").replace("\r", "")
    doc_uri = URIRef(clean_id)
    model.add((doc_uri, RDF.type, URIRef(base_doc_uri)))
    model.add((doc_uri, RDF.type, URIRef(BASE_URI_ACADEMICWORK)))

    for c in creator:
        creator_uri = URIRef(BASE_URI_PERSONA+'/' + camel_case(c))
        model.add((creator_uri, RDF.type, URIRef(BASE_URI_PERSONA)))
        model.add((creator_uri, URIRef(BASE_URI + "namePersona"), Literal(c)))
        model.add((doc_uri, URIRef(BASE_URI + "hasAuthor"), creator_uri))
    for c in contributor:
        contributor_uri = URIRef(BASE_URI_PERSONA+'/' + camel_case(c))
        model.add((contributor_uri, RDF.type, URIRef(BASE_URI_PERSONA)))
        model.add((contributor_uri, URIRef(BASE_URI + "namePersona"), Literal(c)))
        model.add((doc_uri, URIRef(BASE_URI + "contributor"), contributor_uri))
    for p in publisher:
        publisher_uri = URIRef(BASE_URI_PUBLISHER + '/' + camel_case(p))
        model.add((publisher_uri, RDF.type, URIRef(BASE_URI_PUBLISHER)))
        model.add((publisher_uri, URIRef(BASE_URI + "namePublisher"), Literal(p)))
        model.add((doc_uri, URIRef(BASE_URI + "publisher"), publisher_uri))
    for subj in subject:
        subject_uri = URIRef(BASE_URI_SUBJECT + '/' + camel_case(subj))
        model.add((doc_uri, URIRef(BASE_URI + "subject"), subject_uri))

    
    
    for t in title:
        model.add((doc_uri, URIRef(BASE_URI + "title"), Literal(t)))
    for d in date:
        model.add((doc_uri, URIRef(BASE_URI + "year"), Literal(d, datatype=XSD.gYear)))
    for d in description:
        model.add((doc_uri, URIRef(BASE_URI + "description"), Literal(d)))
    for l in language:
        model.add((doc_uri, URIRef(BASE_URI + "language"), Literal(l, datatype=XSD.language)))
    for r in relation:
        clean_r = r.strip().replace("\n", "").replace("\r", "")
        model.add((doc_uri, URIRef(BASE_URI + "relation"), URIRef(clean_r)))
    for rt in rights:
        clean_rt = rt.strip().replace("\n", "").replace("\r", "")
        model.add((doc_uri, URIRef(BASE_URI + "license"), URIRef(clean_rt)))


    

model.serialize(destination="coleccion.ttl", format='turtle')
model2=Graph()
model2.parse("esquema.ttl", format='turtle')
model2 += model
# Aplica OWL-RL (modifica model2 añadiendo triples inferidos)
#DeductiveClosure(OWLRL_Semantics).expand(model2)
model2.serialize(destination=rdf_path, format='turtle')