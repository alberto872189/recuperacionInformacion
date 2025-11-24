from rdflib import Graph, Namespace, RDF

g = Graph()
g.parse('zaguan_config.ttl', format='turtle')
F = Namespace('http://jena.apache.org/configuration/fuseki#')
found = False
for s, p, o in g.triples((None, RDF.type, None)):
    print('TRIPLE:', s, 'a', o)
    if o == F.Service:
        found = True

print('FOUND fuseki:Service?', found)
