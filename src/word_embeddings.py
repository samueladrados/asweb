# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 04:08:29 2023

@author: Samuel
"""

class WordEmbeddings():
    
    def __init__(self, corpus, vector_size=100, window_size=10, min_count=2):
        self.corpus=corpus
        self.vector_size=int(vector_size)
        self.window_size=int(window_size)
        self.min_count=int(min_count)
        self.we=None
        self.name=None
        