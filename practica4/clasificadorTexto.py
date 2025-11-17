import os
import sys
import random
import pandas as pd, numpy as np, commonFunctions
from commonFunctions import to_categorical, cleanTexts, TextVectorization
from textClassifier__DataReader import dataReader
import xml.etree.ElementTree as ET
import textClassifier_Transformer_main as model
import textClassifier__TrainerTester as trainertester

SEED = 0

random.seed(SEED)
np.random.seed(SEED)

import tensorflow as tf
tf.random.set_seed(SEED)

os.environ["PYTHONHASHSEED"] = str(SEED)
os.environ["TF_DETERMINISTIC_OPS"] = "1"
os.environ["TF_CUDNN_DETERMINISTIC"] = "1"

categories = ['Ingeniería', 'Ciencias de la Salud', 'Artes y Humanidades', 'Ciencias', 'Ciencias sociales y jurídicas']
relations = {
    'Ingeniería': ['Arquitectura', 'Defensa y Seguridad', 'Agroalimentaria y del Medio Rural', 'Biomédica', 'Civil', 'Industrial', 'Telecomunicación', 'Eléctrica', 'Electrónica', 'Informática', 'Mecánica', 'Mecatrónica', 'Ingeniería Química', 'Eficiencia Energética'],
    'Ciencias de la Salud': ['Salud', 'Enfermería', 'Fisioterapia', 'Medicina', 'Nutrición', 'Odontología', 'Psicología', 'Terapia Ocupacional', 'Veterinaria', 'Nutricionales'],
    'Artes y Humanidades': ['Bellas Artes', 'Estudios Clásicos', 'Estudios Ingleses', 'Filología Hispánica', 'Filosofía', 'Historia', 'Lenguas Modernas'],
    'Ciencias': ['Biotecnología', 'Ciencia', 'Física', 'Geología', 'Matemáticas', 'Óptica', 'Química'],
    'Ciencias sociales y jurídicas': ['Administración', 'Deporte', 'Derecho', 'Economía', 'Empresa', 'Finanzas', 'Geografía', 'Gestión', 'Información', 'Educación', 'Marketing', 'Periodismo', 'Relaciones Laborales', 'Trabajo Social', 'Turismo', 'ADE', 'DERECHO', 'Auditoría']
}

def generate_datasets(input_dir):
    valid_documents = []
    #file_path = os.path.join(foldername, filename)
    # print(file_path)
    for doc in os.scandir(input_dir):
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
        solved = False
        for child in root:
            if child.tag == f'{{{dc_uri}}}type':
                if child.text: doc_type += child.text
            if child.tag == f'{{{dc_uri}}}description':
                if child.text: description += child.text
            if child.tag == f'{{{dc_uri}}}title':
                if child.text: title += child.text
            if child.tag == f'{{{dc_uri}}}subject':
                i = 0
                for clave in categories:
                    for valor in relations[clave]:
                        if valor in child.text and not solved:
                            subject = i
                            solved = True
                            break
                    i += 1
                    if solved: break
            

        if (doc_type != 'TAZ-TFG'):
            continue

        if not solved: print(file_path, ': ', doc_type, '\n')
        valid_documents.append((file_path, title, description, subject))
    training_set = random.sample(valid_documents, k=int(0.8*len(valid_documents)))
    test_set = list(set(valid_documents).difference(training_set))

    return training_set, test_set
    
        
input_dir = '../recordsdc'
output_dir = 'outputs'

i = 1
while i < len(sys.argv):
    if sys.argv[i] == '-dir':
        input_dir = sys.argv[i + 1]
        i += 1
    elif sys.argv[i] == '-output':
        output_dir = sys.argv[i + 1]
        i += 1
    i += 1

training_set, test_set = generate_datasets(input_dir)

def transform_list_to_pd(my_list):
    df = pd.DataFrame(my_list, columns=['File', 'Title', 'Description', 'Subject'])

    # Crear la columna 'Text' concatenando Title y Description
    df['Text'] = df['Title'] + '. ' + df['Description']

    cleanedTexts = cleanTexts((df['Text'].values))

    # Crear la columna 'Class Index' a partir de Subject
    df['Class Index'] = df['Subject']

    # Seleccionar solo las dos columnas que quieres
    df = df[['Class Index', 'Text']]
    return df

training_set = transform_list_to_pd(training_set)
test_set = transform_list_to_pd(test_set)

# Para el training set
X_train = training_set['Text']
y_train = training_set['Class Index']

# Para el test set
X_test = test_set['Text']
y_test = test_set['Class Index']

MAX_LEN = 200  # Debe coincidir con vectorizer.output_sequence_length
vectorizer = TextVectorization(max_tokens=None, output_mode='int', output_sequence_length=MAX_LEN)
vectorizer.adapt(X_train)

X_train = vectorizer(X_train)
X_test = vectorizer(X_test)

y_train = to_categorical(training_set['Class Index'].values)
y_test = to_categorical(test_set['Class Index'].values)

# voc_size = tamaño del vocabulario generado por vectorizer
voc_size = len(vectorizer.get_vocabulary())

my_model = model.createModel(voc_size, MAX_LEN)
trainertester.trainerTester(my_model, [X_train, y_train, X_test, y_test], 10, output_dir)