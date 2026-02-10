# -*- coding: utf-8 -*-
"""
Created on Thu May 18 04:47:07 2023

@author: Samuel
"""
import numpy as np
from sympy.utilities.iterables import multiset_permutations
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

""" 
indirect and direct bias from:
    Bolukbasi, T., Chang, K. W., Zou, J. Y., Saligrama, V., & Kalai, A. T. (2016). Man
    is to computer programmer as woman is to homemaker? debiasing word embeddings.
    Advances in neural information processing systems, 29, 4349-4357.
"""

def vector_projection(u, v):
    #project u on v
    return (np.dot(u, v) / np.linalg.norm(v)**2 ) * v


def indirect_bias(w, v, gender_direction):
    w_proj_out=w-vector_projection(w, gender_direction)
    v_proj_out=v-vector_projection(v, gender_direction)
    return (np.dot(w,v) - np.dot(w_proj_out, v_proj_out)/(np.linalg.norm(w_proj_out) * np.linalg.norm(v_proj_out)))/np.dot(w,v)


def direct_bias(gender_neutral_words, gender_direction, c=1):
    cos_similarity=[]
    for word in gender_neutral_words:
        if abs(np.dot(word, gender_direction)/(np.linalg.norm(word)*np.linalg.norm(gender_direction))) == 0 and c == 0:
            cos_similarity.append(0)       
        else:
            cos_similarity.append(pow(abs(np.dot(word, gender_direction)/(np.linalg.norm(word)*np.linalg.norm(gender_direction))),c))
    
    return sum(cos_similarity)/len(gender_neutral_words)

""" 
WEAT from:
    Caliskan, A., Bryson, J.J., & Narayanan, A. (2017). Semantics derived automatically 
    from language corpora contain human-like biases. Science, 356, 183 - 186,
"""

#Based on "jsedoc, ConceptorDebias, (Jan 31, 2022), GitHub repository, https://github.com/jsedoc/ConceptorDebias"
def swAB(W, A, B):
    return (np.mean(cosine_similarity(W,A), axis = 1) - np.mean(cosine_similarity(W,B), axis = 1))

def sXYAB(X, Y, A, B):
    return sum(swAB(X, A, B)) - sum(swAB(Y, A, B))

def effect_size(X, Y, A, B):
    XuY=np.concatenate((X, Y), axis=0)
    return (np.mean(swAB(X,A,B)) - np.mean(swAB(Y,A,B))) / np.std(swAB(XuY, A, B))

def p_value(X, Y, A, B):

    XuY=np.concatenate((X, Y), axis=0)
    
    idx = np.zeros(len(XuY))
    idx[:len(XuY) // 2] = 1
    
    test_stats_over_permutation = []

    for i in multiset_permutations(idx):
        i = np.array(i, dtype=np.int32)

        Ximat = XuY[i]
        Yimat = XuY[1-i]
        test_stats_over_permutation.append(sXYAB(Ximat, Yimat, A, B))

    sXYAB_overall = sXYAB(X, Y, A, B)
    sXYAB_comparasion = np.array([stat > sXYAB_overall for stat in test_stats_over_permutation])
    return sXYAB_comparasion.sum() / sXYAB_comparasion.size


def WEAT(X, Y, A, B):
    return sXYAB(X, Y, A, B), effect_size(X, Y, A, B), p_value(X, Y, A, B)


"""
neighborhood metric from:
    Gonen, H., & Goldberg, Y. (2019). Lipstick on a Pig: Debiasing Methods Cover up Systematic Gender Biases in Word Embeddings But do not Remove Them. 
    Proceedings of NAACL-HLT.
    
    and
    
    Wang, T., Lin, X. V., Rajani, N. F., McCann, B., Ordonez, V., & Xiong, C. (2020, July). Double-Hard Debias: 
    Tailoring Word Embeddings for Gender Bias Mitigation. Association for Computational Linguistics (ACL)
"""


def neighborhood_metric(X, Y, random_state=1, num=2):
    #metric=0.5 indicates perfecly unbiased, metric closer to 1.0 indicates stronger bias.
    
    kmeans = KMeans(n_clusters=num, random_state=random_state).fit(X)
    y_pred = kmeans.predict(X)
    correct = [1 if item1 == item2 else 0 for (item1,item2) in zip(Y, y_pred) ]
    metric = max(sum(correct)/float(len(correct)), 1 - sum(correct)/float(len(correct)))
    print('metric', metric)
    
    return metric