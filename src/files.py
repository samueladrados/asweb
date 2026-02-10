# -*- coding: utf-8 -*-
"""
Created on Fri May  5 03:10:32 2023

@author: Samuel
"""

import string
import re
import os
import numpy as np
from nltk import word_tokenize
from nltk.corpus import stopwords

from pathlib import Path

def upload_corpus(filepath):
    filepath=Path(filepath)
    text_file = open(filepath, "r")  
    corpus = text_file.read()
    text_file.close()
    return corpus
    
    
def preprocessing_glove(corpus):
    corpus=corpus.lower()
    corpus=corpus.translate(str.maketrans('', '', string.punctuation))  
    corpus=re.sub('[0-9]+', '', corpus)
    stop_words = stopwords.words('english')
    corpus=re.sub(r'\b\w+\b', lambda w: w.group() if w.group() not in stop_words else '', corpus)
            
    return corpus


def preprocessing_word2vec(corpus):
    corpus=corpus.lower()
    corpus=corpus.translate(str.maketrans('', '', string.punctuation)) 
    corpus=re.sub('[0-9]+', '', corpus)  
    corpus=word_tokenize(corpus)
    stop_words = stopwords.words('english')
    corpus=[w for w in corpus if not w in stop_words]
    aux=[]
    aux.append(corpus)
    return aux


def save_word_embeddings(filename, we):
    path=os.path.join(os.getcwd(), filename)
    f=open(path, "w", encoding="utf-8")
    for j, word in enumerate(we.keys()):
        f.write(word + " ")
        for i, w in enumerate(we[word]):
            if i<len(we[word])-1:
                f.write(str(w) + " ")
            else:
                if j<len(we)-1:
                    f.write(str(w) + "\n")
                else:
                    f.write(str(w))
                    

def upload_word_embeddings(path):
    path=Path(path)
    we={}
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            line=line.split("\n")[0].split(" ")
            we[line[0]]=np.array(line[1:], dtype=np.float32)
            we[line[0]]=we[line[0]]/np.linalg.norm(we[line[0]])
    return we
    