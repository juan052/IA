import numpy as np
import nltk
# nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()


def tokenize(sentence):
    """
    Divide una oración en un arreglo de palabras/tokens.
    Un token puede ser una palabra, carácter de puntuación o número.
    """
    return nltk.word_tokenize(sentence)


def stem(word):
    """
    Aplicar stemming para encontrar la forma raíz de una palabra.
    Ejemplos:
    palabras = ["organize", "organizes", "organizing"]
    palabras = [stem(w) for w in palabras]
    -> ["organ", "organ", "organ"]
    """
    return stemmer.stem(word.lower())


def bag_of_words(tokenized_sentence, words):
    """
    Retorna un arreglo 'bag of words':
    1 para cada palabra conocida que exista en la oración, 0 en caso contrario.
    Ejemplo:
    oración = ["hola", "cómo", "estás", "tú"]
    palabras = ["hola", "cómo", "yo", "tú", "adiós", "gracias", "genial"]
    bog = [  1 ,    1 ,   0 ,   1 ,    0 ,     0   ,     0  ]
    """
    # Stemming para cada palabra
    sentence_words = [stem(word) for word in tokenized_sentence]
    # Inicializar 'bag' con 0 para cada palabra
    bag = np.zeros(len(words), dtype=np.float32)
    
    # Usar un conjunto para verificar si la palabra ya se procesó
    sentence_words_set = set(sentence_words)
    
    for idx, w in enumerate(words):
        if w in sentence_words_set: 
            bag[idx] = 1

    return bag