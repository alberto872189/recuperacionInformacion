import os
import sys
import time
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph

# Configuración del servicio FUSEKI
FUSEKI_HOST = 'http://localhost:3030'
DATASET_NAME = 'datasetExample3'
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'
ENDPOINT = f'{FUSEKI_HOST}/{DATASET_NAME}/sparql'


rdf_path = './schema.ttl'
conf_path = './conf.ttl'

i = 1
while i < len(sys.argv):
    if sys.argv[i] == '-conf':
        conf_path = sys.argv[i + 1]
        i += 1
    elif sys.argv[i] == '-rdf':
        rdf_path = sys.argv[i + 1]
        i += 1
    i += 1

def datasetCreation(config_file):
    with open(config_file, 'rb') as f:
        response = requests.post(
            f"{FUSEKI_HOST}/$/datasets",
            files={
                "config": (config_file, f, "text/turtle")
            },
            auth=(ADMIN_USER, ADMIN_PASS)
        )
    return response

# Carga un fichero RDF en el almacén que se ha creado. El rdf tiene una estructura con los índices ya creados.
def rdfLoad(dataset_name, rdf_file):
    with open(rdf_file, "rb") as f:
        response = requests.post(
            f"{FUSEKI_HOST}/{dataset_name}/data",
            data=f,
            headers={"Content-Type": "text/turtle"},
            auth=(ADMIN_USER, ADMIN_PASS)
        )
    return response

# Crea un almacén con el nombre y configuración indicada.
def fusekiConfiguration(dataset_name, config_file, rdf_file):
    response = datasetCreation(config_file)
    if response.status_code == 200:
        time.sleep(2) #Esperamos a que el servicio se actualice correctamente
        response = rdfLoad(dataset_name, rdf_file)
        if response.status_code == 200:
            print(f" Archivo '{rdf_file}' cargado")
        else:
            print(f' Error cargando archivo: {response.status_code} - {response.text}')
    else:
        print(f'Error creando dataset: {response.status_code} - {response.text}')


fusekiConfiguration('dataset epico', conf_path, rdf_path)

