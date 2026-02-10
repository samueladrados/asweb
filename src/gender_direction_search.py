# -*- coding: utf-8 -*-
"""
Created on Mon May 15 19:10:59 2023

@author: Samuel
"""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import SGDClassifier

""" 
PCA_pairs:
    Bolukbasi, T., Chang, K. W., Zou, J. Y., Saligrama, V., & Kalai, A. T. (2016). Man
    is to computer programmer as woman is to homemaker? debiasing word embeddings.
    Advances in neural information processing systems, 29, 4349-4357.
"""

def PCA_pairs(we, pairs, num_components = 10):
    matrix = []

    for a, b in pairs:
        center = (we[a] + we[b])/2
        matrix.append(we[a] - center)
        matrix.append(we[b] - center)
    matrix = np.array(matrix)
    
    pca = PCA(n_components = min(matrix.shape[0], matrix.shape[1], num_components))

    pca.fit(matrix)

    return np.array(pca.components_[0])


"""
two_means:
    Dev, S., & Phillips, J. M. (2019). Attenuating Bias in Word Vectors. CoRR, abs/1901.07656. 
    Retrieved from http://arxiv.org/abs/1901.07656
"""
def two_means(we, female_words, male_words):
    female_words_vectors=[]
    for word in female_words:
        female_words_vectors.append(we[word])
    
    male_words_vectors=[]
    for word in male_words:
        male_words_vectors.append(we[word])
    
    female_mean = np.mean(female_words_vectors, axis=0)
    male_mean = np.mean(male_words_vectors, axis=0)
    gender_direction = (female_mean - male_mean)/np.linalg.norm(female_mean - male_mean)
    return gender_direction/np.linalg.norm(gender_direction)


"""
classification:
    Ravfogel, S., Elazar, Y., Gonen, H., Twiton, M., & Goldberg, Y. (2020). Null It Out: 
    Guarding Protected Attributes by Iterative Nullspace Projection. ACL.
"""

def classification(X_train, Y_train):
    clf = SGDClassifier()
    clf.fit(X_train, Y_train)
    acc = clf.score(X_train, Y_train)
    print("accuracy: " + str(acc))
    
    return clf.coef_