# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 21:02:32 2023

@author: Samuel
"""
from sklearn.decomposition import PCA
import numpy as np
from src import measurements

'''
Code based on: Rathore, A., Dev, S., Phillips, J. M., Srikumar, V., Zheng, Y., Yeh, C.-C. M., … Wang, B. (2021). 
VERB: Visualizing and Interpreting Bias Mitigation Techniques for Word Representations. ArXiv [Cs.CL]. 
Retrieved from http://arxiv.org/abs/2104.02797

'''

def reduction_embeddings_to_2d(we, masc_words, fem_words, neutral_words, gender_direction=None):
    #Reduction of embeddings dim to 2 dim with PCA to visualize them
    X_all=[]
    for word in masc_words + fem_words + neutral_words:
        X_all.append(we[word]) 
        
    projector=PCA(n_components=2)
    projector.fit(X_all)
    
    X_masc=[]
    for word in masc_words:
        X_masc.append(we[word]) 
    X_masc=projector.transform(X_masc)
        
    X_fem=[]
    for word in fem_words:
        X_fem.append(we[word]) 
    X_fem=projector.transform(X_fem)
    
    X_neutral=[]
    for word in neutral_words:
        X_neutral.append(we[word]) 
    X_neutral=projector.transform(X_neutral)
    
    
    X_masc_aux=[]
    for x in X_masc:
        X_masc_aux.append([round(float(item),6) for item in x])
    X_masc=X_masc_aux
    
    X_fem_aux=[]
    for x in X_fem:
        X_fem_aux.append([round(float(item),6) for item in x])
    X_fem=X_fem_aux
    

    
    X_neutral_aux=[]
    for x in X_neutral:
        X_neutral_aux.append([round(float(item),6) for item in x])
    X_neutral=X_neutral_aux
    
    if gender_direction is not None:
        dim=gender_direction.shape[0]
        origin=np.zeros(dim)
        
        vector_gender_direction=projector.transform(np.vstack([origin, gender_direction]))
        vector_gender_direction=vector_gender_direction-vector_gender_direction[0]
    
        vector_gender_direction_aux=[]
        for x in vector_gender_direction:
            vector_gender_direction_aux.append([round(float(item),6) for item in x])
        vector_gender_direction=vector_gender_direction_aux

        return X_masc, X_fem, X_neutral, vector_gender_direction
    else:
        return X_masc, X_fem, X_neutral
    
   
def reduction_embeddings_to_2d_gender_direction_x(we, masc_words, fem_words, neutral_words, gender_direction):
    #Reduction of embeddings dim to 2 dim with PCA to visualize them being x axis as the gender bias 
    X_all=[]
    for word in masc_words + fem_words + neutral_words:
        X_all.append(we[word])
             
    #Remove gender direction and compute PCA
    projector=PCA(n_components=2)
    projector.fit(X_all - np.dot(X_all,gender_direction.reshape(-1,1))*gender_direction)
    
    
    
    X_masc=[]
    for word in masc_words:
        X_masc.append(we[word]) 
            
    #x axis as the similarity with gender_direction
    x_component=np.expand_dims(np.dot(X_masc,gender_direction),1)
    
    #Remove gender direction of masc words (same as PCA) and transform with PCA into 2d
    debiased_X_masc=X_masc - np.dot(X_masc,gender_direction.reshape(-1,1))*gender_direction
    y_component=np.expand_dims(projector.transform(debiased_X_masc)[:, 0], 1)   
    X_masc=np.hstack([x_component, y_component])
    
    
    
    X_fem=[]
    for word in fem_words:
        X_fem.append(we[word]) 
            
    #x axis as the similarity with gender_direction
    x_component=np.expand_dims(np.dot(X_fem,gender_direction),1)
    
    #Remove gender direction of fem words (same as PCA) and transform with PCA into 2d
    debiased_X_fem=X_fem - np.dot(X_fem,gender_direction.reshape(-1,1))*gender_direction
    y_component=np.expand_dims(projector.transform(debiased_X_fem)[:, 0], 1)
   
    X_fem=np.hstack([x_component, y_component])
    
    
    X_neutral=[]
    for word in neutral_words:
        X_neutral.append(we[word]) 
            
    #x axis as the similarity with gender_direction
    x_component=np.expand_dims(np.dot(X_neutral,gender_direction),1)
    
    #Remove gender direction of neutral words (same as PCA) and transform with PCA into 2d
    debiased_X_neutral=X_neutral - np.dot(X_neutral,gender_direction.reshape(-1,1))*gender_direction
    y_component=np.expand_dims(projector.transform(debiased_X_neutral)[:, 0], 1)
   
    X_neutral=np.hstack([x_component, y_component])
    
    
    
    dim=gender_direction.shape[0]
    origin=np.zeros(dim)
    vector_gender_direction=np.vstack([origin, gender_direction])
    
 
    #Similarity of gender direction with gender direction in x axis = 1 (max)
    x_component=np.expand_dims(np.dot(vector_gender_direction,gender_direction),1)
    
    
    #Remove gender direction of gender direction = vector of zeros
    debiased_vector_gender_direction=vector_gender_direction - np.dot(vector_gender_direction,gender_direction.reshape(-1,1))*gender_direction   
   
    #Transform gender direction into a y axis space with gender direction removed = 0
    y_component=np.expand_dims(projector.transform(debiased_vector_gender_direction)[:, 0], 1)
    
    vector_gender_direction=np.hstack([x_component, y_component])
    
    #origin point of gender vector 0,0 
    vector_gender_direction=vector_gender_direction-vector_gender_direction[0]
    
    X_masc_aux=[]
    for x in X_masc:
        X_masc_aux.append([round(float(item),6) for item in x])
    X_masc=X_masc_aux
    
    X_fem_aux=[]
    for x in X_fem:
        X_fem_aux.append([round(float(item),6) for item in x])
    X_fem=X_fem_aux
    
    vector_gender_direction_aux=[]
    for x in vector_gender_direction:
        vector_gender_direction_aux.append([round(float(item),6) for item in x])
    vector_gender_direction=vector_gender_direction_aux
    
    X_neutral_aux=[]
    for x in X_neutral:
        X_neutral_aux.append([round(float(item),6) for item in x])
    X_neutral=X_neutral_aux
    
    return X_masc, X_fem, X_neutral, vector_gender_direction
    