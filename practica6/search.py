# ------------------------------------------------------
# Consulta necesidades de información contra Solr (core nutch).
# Las consultas se leen del fichero de entrada tal cual (formato Solr query).
# ------------------------------------------------------

import xml.etree.ElementTree as ET
import sys
import re
import requests

# Configuración del servicio Solr
SOLR_BASE = 'http://localhost:8983/solr'
SOLR_CORE = 'nutch'
SOLR_SELECT = f"{SOLR_BASE}/{SOLR_CORE}/select"


def _normalize_zaguan_id(raw_id: str) -> str:
    """Convierte IDs locales (oai_zaguan..._12345.xml) a https://zaguan.unizar.es/record/12345.

    Si no se puede extraer el número, devuelve el id original.
    """
    if not raw_id:
        return raw_id
    # Si ya viene en el formato deseado, respétalo
    if raw_id.startswith("http://zaguan.unizar.es/record/") or raw_id.startswith("https://zaguan.unizar.es/record/"):
        return raw_id
    m = re.search(r"_(\d+)\.xml", raw_id)
    if m:
        rec_id = m.group(1)
        return f"http://zaguan.unizar.es/record/{rec_id}"
    return raw_id


def printResults(identifier, docs, output):
    """Imprime resultados devueltos por Solr.

    - identifier: id de la informationNeed
    - docs: lista de documentos devueltos en response.docs
    - output: descriptor de salida (stdout o fichero)
    """
    if not docs:
        print(f"{identifier}\t(no results)", file=output)
        return

    for doc in docs:
        doc_id = _normalize_zaguan_id(doc.get('id', ''))
        title = doc.get('title', '')
        if isinstance(title, list):
            title = title[0] if title else ''
        score = doc.get('score', '')
        parts = [str(doc_id)]
        if title:
            parts.append(str(title))
        if score != '':
            parts.append(f"score={score}")
        print(f"{identifier}\t" + "\t".join(parts), file=output)


def run_query(raw_query):
    """Ejecuta una consulta Solr.

    Si la cadena ya trae parámetros (contiene '=') se envía como querystring tal cual.
    En caso contrario se envía como parámetro q=raw_query con wt=json y rows=100.
    """
    q = raw_query.strip()
    try:
        if '=' in q:
            # Se asume que el usuario ha pasado la query completa (p.ej. q=foo&rows=50)
            url = f"{SOLR_SELECT}?{q}"
            resp = requests.get(url, timeout=10)
        else:
            params = {"q": q, "wt": "json", "rows": 100}
            resp = requests.get(SOLR_SELECT, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get('response', {}).get('docs', [])
    except Exception as exc:  # noqa: BLE001
        # En caso de error, devolver lista vacía y mostrar por stderr
        print(f"[ERROR] {exc}", file=sys.stderr)
        return []


# ------------------------------------------------------
# Función main
# ------------------------------------------------------
if __name__ == '__main__':
    input_file = None
    output_file = None
    output = sys.stdout
    data = []

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-infoNeeds':
            file_path = sys.argv[i + 1]
            tree = ET.parse(file_path)
            root = tree.getroot()
            raw_text = "".join(root.itertext())
            text = ' '.join(line.strip() for line in raw_text.splitlines() if line)
            for need in root.findall("informationNeed"):
                identifier = need.find("identifier").text
                qtext = need.find("text").text
                data.append({"identifier": identifier, "text": qtext})
            i += 1
        elif sys.argv[i] == '-output':
            output_file = sys.argv[i + 1]
            output = open(output_file, "w")
            i += 1
        i += 1

    for item in data:
        query = item["text"]
        identifier = item["identifier"]
        docs = run_query(query)
        printResults(identifier, docs, output)

    if output_file:
        output.close()