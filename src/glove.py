# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 16:12:52 2023

@author: Samuel

Based on the Source Code of Gauthier, J. (2019). glove.py [Software]. En hans/glove.py. https://github.com/hans/glove.py
"""
import itertools
from src import word_embeddings
import numpy as np

from scipy import sparse
from math import log
from random import shuffle
from collections import Counter


class Glove(word_embeddings.WordEmbeddings):

    
    def __init__(self, corpus, vector_size=100, window_size=10, min_count=2, iterations=25, learning_rate=0.05, alpha=0.75, x_max=100):
        super().__init__(corpus,vector_size,window_size,min_count)
        self.iterations=int(iterations)
        self.learning_rate=float(learning_rate)
        self.alpha=float(alpha)
        self.x_max=float(x_max)
        self.vocab=self.build_vocab()
        self.cooccur=list(self.build_cooccur())
        self.W=self.train_glove()
        self.W=self.merge_main_context()
        self.we={word: self.W[i] for i, word in enumerate(self.vocab)}
        
        
    def build_vocab(self):
        """
        Build a vocabulary with word frequencies for an entire corpus.
    
        Returns a dictionary `w -> (i, f)`, mapping word strings to pairs of
        word ID and word corpus frequency.
        """
    
        print("Building vocab from corpus")
    
        vocab = Counter()
        for line in self.corpus.splitlines():
            tokens = line.strip().split()
            vocab.update(tokens)
    
        vocab=dict(sorted(vocab.items()))
        vocab=dict(sorted(vocab.items(), key=lambda item: item[1], reverse=True))
    
        print("Done building vocab from corpus.")
    
        return {word: (i, freq) for i, (word, freq) in enumerate(vocab.items()) if self.min_count==None or freq >= self.min_count}
    
    def build_cooccur(self):
        """
        Build a word co-occurrence list for the given corpus.
        This function is a tuple generator, where each element (representing
        a cooccurrence pair) is of the form
            (i_main, i_context, cooccurrence)
        where `i_main` is the ID of the main word in the cooccurrence and
        `i_context` is the ID of the context word, and `cooccurrence` is the
        `X_{ij}` cooccurrence value as described in Pennington et al.
        (2014).
        """
    
        vocab_size = len(self.vocab)
    
        # Collect cooccurrences internally as a sparse matrix for passable
        # indexing speed; we'll convert into a list later
        cooccurrences = sparse.lil_matrix((vocab_size, vocab_size),
                                          dtype=np.float64)
    
        for i, line in enumerate(self.corpus.splitlines()):
            if i % 1000 == 0:
                print("Building cooccurrence matrix: on line %i", i)

            tokens = line.strip().split()
            token_ids = [self.vocab[word][0] for word in tokens if self.vocab.get(word)!=None]
            
            for center_i, center_id in enumerate(token_ids):
                # Collect all word IDs in left window of center word
                context_ids = token_ids[max(0, center_i - self.window_size) : center_i]
                contexts_len = len(context_ids)
    
                for left_i, left_id in enumerate(context_ids):
                    # Distance from center word
                    distance = contexts_len - left_i
    
                    # Weight by inverse of distance between words
                    increment = 1.0 / float(distance)
    
                    # Build co-occurrence matrix symmetrically (pretend we
                    # are calculating right contexts as well)
                    cooccurrences[center_id, left_id] += increment
                    cooccurrences[left_id, center_id] += increment
                    

        # Now yield our tuple sequence (dig into the LiL-matrix internals to
        # quickly iterate through all nonzero cells)
        for i, (row, data) in enumerate(zip(cooccurrences.rows,
                                                   cooccurrences.data)):
            for data_idx, j in enumerate(row):
                yield i, j, data[data_idx]
        
    
    def run_iter(self, biases, gradient_squared, gradient_squared_biases):
        """
        Run a single iteration of GloVe training using the given
        cooccurrence data and the previously computed weight vectors /
        biases and accompanying gradient histories.
        See the `train_glove` function for information on the shapes of `W`,
        `biases`, `gradient_squared`, `gradient_squared_biases` and how they
        should be initialized.
        The parameters `x_max`, `alpha` define our weighting function when
        computing the cost for two word pairs; see the GloVe paper for more
        details.
        Returns the cost associated with the given weight assignments and
        updates the weights by online AdaGrad in place.
        """
    
        global_cost = 0
        vocab_size = len(self.vocab)
        # We want to iterate over data randomly so as not to unintentionally
        # bias the word vector contents
        shuffle(self.cooccur)
    
        for i_main, i_context, cooccurrence in self.cooccur:
    
            weight = (cooccurrence / self.x_max) ** self.alpha if cooccurrence < self.x_max else 1
    
            # Compute inner component of cost function, which is used in
            # both overall cost calculation and in gradient calculation
            #
            #   $$ J' = w_i^Tw_j + b_i + b_j - log(X_{ij}) $$
            cost_inner = (self.W[i_main].dot(self.W[i_context + vocab_size])
                          + biases[i_main : i_main + 1][0] + biases[i_context + vocab_size : i_context + vocab_size + 1][0]
                          - log(cooccurrence))
    
            # Compute cost
            #
            #   $$ J = f(X_{ij}) (J')^2 $$
            cost = weight * (cost_inner ** 2)
    
            # Add weighted cost to the global cost tracker
            global_cost += 0.5 * cost
    
            # Compute gradients for word vector terms.
            #
            # NB: `main_word` is only a view into `W` (not a copy), so our
            # modifications here will affect the global weight matrix;
            # likewise for context_word, biases, etc.
            grad_main = weight * cost_inner * self.W[i_context + vocab_size]
            grad_context = weight * cost_inner * self.W[i_main]
    
            # Compute gradients for bias terms
            grad_bias_main = weight * cost_inner
            grad_bias_context = weight * cost_inner
    
            # Now perform adaptive updates
            self.W[i_main] -= (self.learning_rate * grad_main / np.sqrt(gradient_squared[i_main]))
            self.W[i_context + vocab_size] -= (self.learning_rate * grad_context / np.sqrt(gradient_squared[i_context + vocab_size]))
    
            biases[i_main : i_main + 1] -= (self.learning_rate * grad_bias_main / np.sqrt(gradient_squared_biases[i_main : i_main + 1]))
            biases[i_context + vocab_size : i_context + vocab_size + 1] -= (self.learning_rate * grad_bias_context / np.sqrt(
                    gradient_squared_biases[i_context + vocab_size : i_context + vocab_size + 1]))
    
            # Update squared gradient sums
            gradient_squared[i_main] += np.square(grad_main)
            gradient_squared[i_context + vocab_size] += np.square(grad_context)
            gradient_squared_biases[i_main : i_main + 1] += grad_bias_main ** 2
            gradient_squared_biases[i_context + vocab_size : i_context + vocab_size + 1] += grad_bias_context ** 2
    
        return global_cost
    
    
    def train_glove(self):
        """
        Train GloVe vectors on the given generator `cooccurrences`, where
        each element is of the form
            (word_i_id, word_j_id, x_ij)
        where `x_ij` is a cooccurrence value $X_{ij}$ as presented in the
        matrix defined by `build_cooccur` and the Pennington et al. (2014)
        paper itself.
        Returns the computed word vector matrix `W`.
        """
    
        vocab_size = len(self.vocab)
    
        # Word vector matrix. This matrix is (2V) * d, where N is the size
        # of the corpus vocabulary and d is the dimensionality of the word
        # vectors. All elements are initialized randomly in the range (-0.5,
        # 0.5]. We build two word vectors for each word: one for the word as
        # the main (center) word and one for the word as a context word.
        #
        # It is up to the client to decide what to do with the resulting two
        # vectors. Pennington et al. (2014) suggest adding or averaging the
        # two for each word, or discarding the context vectors.
        self.W = (np.random.rand(vocab_size * 2, self.vector_size) - 0.5) / float(self.vector_size)
    
        # Bias terms, each associated with a single vector. An array of size
        # $2V$, initialized randomly in the range (-0.5, 0.5].
        biases = (np.random.rand(vocab_size * 2) - 0.5) / float(self.vector_size)
    
        # Training is done via adaptive gradient descent (AdaGrad). To make
        # this work we need to store the sum of squares of all previous
        # gradients.
        #
        # Like `W`, this matrix is (2V) * d.
        #
        # Initialize all squared gradient sums to 1 so that our initial
        # adaptive learning rate is simply the global learning rate.
        gradient_squared = np.ones((vocab_size * 2, self.vector_size),
                                   dtype=np.float64)
    
        # Sum of squared gradients for the bias terms.
        gradient_squared_biases = np.ones(vocab_size * 2, dtype=np.float64)
    
        # Build a reusable list from the given cooccurrence generator,
        # pre-fetching all necessary data.
        #
        # NB: These are all views into the actual data matrices, so updates
        # to them will pass on to the real data structures
        #
        # (We even extract the single-element biases as slices so that we
        # can use them as views)
    
    
        for i in range(self.iterations):
            print("\tBeginning iteration %i..", i)
    
            cost = self.run_iter(biases, gradient_squared, gradient_squared_biases)
    
            print("\t\tDone (cost %f)", cost/len(self.W))
    
        return self.W
    
    
    def merge_main_context(self, merge_fun=lambda m, c: np.mean([m, c], axis=0),
                           normalize=True):
        """
        Merge the main-word and context-word vectors for a weight matrix
        using the provided merge function (which accepts a main-word and
        context-word vector and returns a merged version).
    
        By default, `merge_fun` returns the mean of the two vectors.
        """
    
        vocab_size = int(len(self.W) / 2)
        for i, row in enumerate(self.W[:vocab_size]):
            merged = merge_fun(row, self.W[i + vocab_size])
            if normalize:
                merged /= np.linalg.norm(merged)
            self.W[i, :] = merged
    
        return self.W[:vocab_size]
    
           
