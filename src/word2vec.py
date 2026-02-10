# -*- coding: utf-8 -*-
"""
Created on Sat May  6 19:01:40 2023

@author: Samuel
"""
import gensim
from src import word_embeddings

class Word2vec(word_embeddings.WordEmbeddings):
    
    def __init__(self, corpus, vector_size=100, window_size=10, min_count=2):
        super().__init__(corpus,vector_size,window_size,min_count)
        self.w2v_model=self.create_word2vec_model()
        self.w2v_model.init_sims(replace=True)
        self.we=self.create_word2vec_we()
        
    
    
    def create_word2vec_model(self):
        return gensim.models.Word2Vec(self.corpus,
                                        vector_size=self.vector_size,
                                        window=self.window_size,
                                        min_count=self.min_count)
        
        
    def create_word2vec_we(self):
        return {word: self.w2v_model.wv[word] for word in self.w2v_model.wv.index_to_key}
    
    