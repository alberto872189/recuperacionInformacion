# ------------------------------------------------------
# Este programa realiza consultas de texto en RDF. Muestra ejemplos de consultas no realizadas de forma correcta
# y como hacerlas correctamente.
# ------------------------------------------------------

from SPARQLWrapper import SPARQLWrapper, JSON
import xml.etree.ElementTree as ET
import sys

# Configuración del servicio FUSEKI
FUSEKI_HOST = 'http://localhost:3030'
DATASET_NAME = 'datasetZaguan'
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'
ENDPOINT = f'{FUSEKI_HOST}/{DATASET_NAME}/sparql'

# Método de impresión de resultados por pantalla, usado por varias consultas
def printResults(id, results, output):
    for result in results["results"]["bindings"]:
        print(f"{id}\t{result['work']['value']}", file=output)
    
# ------------------------------------------------------
# Función main que realiza diferentes tipos de consultas de texto
# ------------------------------------------------------
if __name__ == '__main__':
    sparql = SPARQLWrapper(ENDPOINT)
    
    index_folder = './recordsdcindex'
    input_file = None
    output_file = None
    output = sys.stdout
    data = []

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-infoNeeds':
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

    for item in data:
        query = item["text"]
        id = item["identifier"]
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        #print(results)
        printResults(id, results, output)
    if output:
        output.close()