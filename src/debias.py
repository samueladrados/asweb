# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 20:14:12 2023

@author: Samuel
"""

import numpy as np
from src import measurements
import torch
import time
import random 
import scipy
from src import gender_direction_search
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


""" 
hard_debiasing and soft_debiasing:
    Bolukbasi, T., Chang, K. W., Zou, J. Y., Saligrama, V., & Kalai, A. T. (2016). Man
    is to computer programmer as woman is to homemaker? debiasing word embeddings.
    Advances in neural information processing systems, 29, 4349-4357.
"""

def hard_debiasing(we, gender_specific_words, gender_neutral_words, gender_direction):
    #neutralize
    we_copy=we.copy()
    for word in gender_neutral_words:
        aux=we_copy[word] - measurements.vector_projection(we_copy[word], gender_direction)
        we_copy[word]=aux/np.linalg.norm(aux)
    
    #equalize
    for set_words in gender_specific_words:
        mu=sum([we_copy[word] for word in set_words])/len(set_words)
        mub=measurements.vector_projection(mu, gender_direction)
        v=mu-mub
        for word in set_words:
            proj_word_bias=measurements.vector_projection(we_copy[word], gender_direction)
            aux=proj_word_bias-mub
            we_copy[word]=v+(np.sqrt(1 - np.linalg.norm(v)**2)*(aux/np.linalg.norm(aux)))
    
    return we_copy

def soft_debiasing(we, gender_specific_words, gender_direction, landa=0.2, epochs=100, lr=0.001, momentum=0.0):

    #Code based on "Manzini, T., Lim, Y. C., Tsvetkov, Y., & Black, A. W. (2019). Black is to Criminal as Caucasian is to Police: Detecting and Removing Multiclass Bias in Word Embeddings. ArXiv Preprint ArXiv:1904. 04047."

    W=[]
    neutrals=[]
    we_copy=we.copy()
    
    for key in we_copy.keys():
        W.append(we_copy[key])
        if key not in gender_specific_words:
            neutrals.append(we_copy[key])
            
    W=torch.tensor(W).T
    neutrals=torch.tensor(neutrals).T
    
    u, s, _ = torch.svd(W)
    s = torch.diag(s)
    t1 = s.mm(u.t())
    t2 = u.mm(s)

    
    embedding_dim=u.shape[0]
    transform = torch.randn(embedding_dim, embedding_dim)
    biasSpace = torch.tensor(gender_direction).view(embedding_dim, -1).float()
    
    neutrals.requires_grad = False
    W.requires_grad = False
    biasSpace.requires_grad = False
    transform.requires_grad = True
    
    optimizer = torch.optim.SGD([transform], lr, momentum)
    
    for i in range(0, epochs):
        TtT = torch.mm(transform.t(), transform)
        norm1 = (t1.mm(TtT - torch.eye(embedding_dim)).mm(t2)).norm(p=2)
        norm2 = (neutrals.t().mm(TtT).mm(biasSpace)).norm(p=2)
        
        loss = norm1 + landa * norm2

        norm1 = None
        norm2 = None
        
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        
        print("Loss @ Epoch #" + str(i) + ":", loss)
    
    
    print("Optimization Completed, normalizing vector transform")
        

    for key in we_copy.keys():
        transformedVec = torch.mm(transform, torch.tensor(we_copy[key]).view(-1, 1))
        we_copy[key] = ( transformedVec / transformedVec.norm(p=2) ).detach().numpy().flatten()

    return we_copy
    
    




'''
attract_repel:
    Mrkšić, N., Vulić, I., Ó Séaghdha, D., Leviant, I., Reichart, R., Gašić, M., … Young, S. (2017). 
    Semantic Specialization of Distributional Word Vector Spaces using Monolingual and Cross-Lingual Constraints.
    Transactions of the Association for Computational Linguistics, 5, 309–324. doi:10.1162/tacl_a_00063

'''

def initialise_model(numpy_embedding):
    """
    Initialises the TensorFlow Attract-Repel model.
    """
    attract_examples = tf.placeholder(tf.int32, [None, 2])  # each element is the position of word vector.
    repel_examples = tf.placeholder(tf.int32, [None, 2])  # each element is again the position of word vector.

    negative_examples_attract = tf.placeholder(tf.int32, [None, 2])
    negative_examples_repel = tf.placeholder(tf.int32, [None, 2])

    attract_margin = tf.placeholder("float")
    repel_margin = tf.placeholder("float")
    regularisation_constant = tf.placeholder("float")

    # Initial (distributional) vectors. Needed for L2 regularisation.
    W_init = tf.constant(numpy_embedding, name="W_init")

    # Variable storing the updated word vectors.
    W_dynamic = tf.Variable(numpy_embedding, name="W_dynamic")

    # Attract Cost Function:

    # placeholders for example pairs...
    attract_examples_left = tf.nn.l2_normalize(tf.nn.embedding_lookup(W_dynamic, attract_examples[:, 0]),
                                               1)
    attract_examples_right = tf.nn.l2_normalize(tf.nn.embedding_lookup(W_dynamic, attract_examples[:, 1]),
                                                1)
    
    # and their respective negative examples:
    negative_examples_attract_left = tf.nn.l2_normalize(
        tf.nn.embedding_lookup(W_dynamic, negative_examples_attract[:, 0]), 1)
    negative_examples_attract_right = tf.nn.l2_normalize(
        tf.nn.embedding_lookup(W_dynamic, negative_examples_attract[:, 1]), 1)

    # dot product between the example pairs.
    attract_similarity_between_examples = tf.reduce_sum(tf.multiply(attract_examples_left, attract_examples_right),
                                                        1)

    # dot product of each word in the example with its negative example.
    attract_similarity_to_negatives_left = tf.reduce_sum(
        tf.multiply(attract_examples_left, negative_examples_attract_left), 1)
    attract_similarity_to_negatives_right = tf.reduce_sum(
        tf.multiply(attract_examples_right, negative_examples_attract_right), 1)

    # and the final Attract Cost Function (sans regularisation):
    attract_cost = tf.nn.relu(
        attract_margin + attract_similarity_to_negatives_left - attract_similarity_between_examples) + \
            tf.nn.relu(attract_margin + attract_similarity_to_negatives_right - attract_similarity_between_examples)

    # Repel Cost Function:

    # placeholders for example pairs...
    repel_examples_left = tf.nn.l2_normalize(tf.nn.embedding_lookup(W_dynamic, repel_examples[:, 0]),
                                             1)  # becomes batch_size X vector_dimension
    repel_examples_right = tf.nn.l2_normalize(tf.nn.embedding_lookup(W_dynamic, repel_examples[:, 1]), 1)

    # and their respective negative examples:
    negative_examples_repel_left = tf.nn.l2_normalize(
        tf.nn.embedding_lookup(W_dynamic, negative_examples_repel[:, 0]), 1)
    negative_examples_repel_right = tf.nn.l2_normalize(
        tf.nn.embedding_lookup(W_dynamic, negative_examples_repel[:, 1]), 1)

    # dot product between the example pairs.
    repel_similarity_between_examples = tf.reduce_sum(tf.multiply(repel_examples_left, repel_examples_right),
                                                      1)  # becomes batch_size again, might need tf.squeeze

    # dot product of each word in the example with its negative example.
    repel_similarity_to_negatives_left = tf.reduce_sum(
        tf.multiply(repel_examples_left, negative_examples_repel_left), 1)
    repel_similarity_to_negatives_right = tf.reduce_sum(
        tf.multiply(repel_examples_right, negative_examples_repel_right), 1)

    # and the final Repel Cost Function (sans regularisation):
    repel_cost = tf.nn.relu(
        repel_margin - repel_similarity_to_negatives_left + repel_similarity_between_examples) + \
            tf.nn.relu(repel_margin - repel_similarity_to_negatives_right + repel_similarity_between_examples)

    # The Regularisation Cost (separate for the two terms, depending on which one is called):

    # load the original distributional vectors for the example pairs:
    original_attract_examples_left = tf.nn.embedding_lookup(W_init, attract_examples[:, 0])
    original_attract_examples_right = tf.nn.embedding_lookup(W_init, attract_examples[:, 1])

    original_repel_examples_left = tf.nn.embedding_lookup(W_init, repel_examples[:, 0])
    original_repel_examples_right = tf.nn.embedding_lookup(W_init, repel_examples[:, 1])

    # and then define the respective regularisation costs:
    regularisation_cost_attract = regularisation_constant * (
                tf.nn.l2_loss(original_attract_examples_left - attract_examples_left) + tf.nn.l2_loss(
            original_attract_examples_right - attract_examples_right))
    attract_cost += regularisation_cost_attract

    regularisation_cost_repel = regularisation_constant * (
                tf.nn.l2_loss(original_repel_examples_left - repel_examples_left) + tf.nn.l2_loss(
            original_repel_examples_right - repel_examples_right))
    repel_cost += regularisation_cost_repel

    # Finally, we define the training step functions for both steps.

    tvars = tf.trainable_variables()

    attract_grads = [tf.clip_by_value(grad, -2., 2.) for grad in tf.gradients(attract_cost, tvars)]
    repel_grads = [tf.clip_by_value(grad, -2., 2.) for grad in tf.gradients(repel_cost, tvars)]

    attract_optimiser = tf.train.AdagradOptimizer(0.05)
    repel_optimiser = tf.train.AdagradOptimizer(0.05)

    attract_cost_step = attract_optimiser.apply_gradients(list(zip(attract_grads, tvars)))
    repel_cost_step = repel_optimiser.apply_gradients(list(zip(repel_grads, tvars)))

    # return the handles for loading vectors from the TensorFlow embeddings:
    return W_dynamic, negative_examples_repel, repel_examples, repel_cost_step, repel_margin, attract_margin, regularisation_constant, negative_examples_attract, attract_examples, attract_cost_step, attract_examples_left, attract_examples_right, repel_examples_left, repel_examples_right




def extract_negative_examples(list_minibatch, sess, embedding_attract_left, embedding_attract_right, attract_examples, attract_batch=True):
        """
        For each example in the minibatch, this method returns the closest vector which is not
        in each words example pair.
        """

        list_of_representations = []
        list_of_indices = []

        representations = sess.run([embedding_attract_left, embedding_attract_right],
                                        feed_dict={attract_examples: list_minibatch})

        for idx, (example_left, example_right) in enumerate(list_minibatch):
            list_of_representations.append(representations[0][idx])
            list_of_representations.append(representations[1][idx])

            list_of_indices.append(example_left)
            list_of_indices.append(example_right)

        condensed_distance_list = pdist(list_of_representations, 'cosine')
        square_distance_list = squareform(condensed_distance_list)

        if attract_batch:
            default_value = 2.0  # value to set for given attract/repel pair, so that it can not be found as closest or furthest away.
        else:
            default_value = 0.0  # for antonyms, we want the opposite value from the synonym one. Cosine Distance is [0,2].

        for i in range(len(square_distance_list)):

            square_distance_list[i, i] = default_value

            if i % 2 == 0:
                square_distance_list[i, i + 1] = default_value
            else:
                square_distance_list[i, i - 1] = default_value

        if attract_batch:
            negative_example_indices = np.argmin(square_distance_list,
                                                    axis=1)  # for each of the 100 elements, finds the index which has the minimal cosine distance (i.e. most similar).
        else:
            negative_example_indices = np.argmax(square_distance_list,
                                                    axis=1)  # for antonyms, find the least similar one.

        negative_examples = []

        for idx in range(len(list_minibatch)):
            negative_example_left = list_of_indices[negative_example_indices[2 * idx]]
            negative_example_right = list_of_indices[negative_example_indices[2 * idx + 1]]

            negative_examples.append((negative_example_left, negative_example_right))

        negative_examples = mix_sampling(list_minibatch, negative_examples)

        return negative_examples



def attract_repel(we, synonyms, antonyms, iterations=5, batch_size=10, attr_margin = 0.6, rep_margin = 0.0, l2_reg_constant = 0.000000001):
       
    tf.reset_default_graph()
       
    vocab_index = {}
    inverted_index = {}
    
    for idx, word in enumerate(we.keys()):
        we[word]=np.float32(we[word])
        vocab_index[word] = idx
        inverted_index[idx] = word
        
        
    constraints = set()
    skipped = 0    
        
    for word_pair in synonyms:
        for i, word in enumerate(word_pair):
            if word not in we.keys():
                word_pair[i] = word.lower()
            if word_pair[0] in we.keys() and word_pair[1] in we.keys() and word_pair[0] != word_pair[1]:
                constraints |= {(vocab_index[word_pair[0]], vocab_index[word_pair[1]])}
            else:
                skipped += 1
    print("{} constraints skipped ({:.2f}% of total)".format(skipped, skipped/i*100))
    synonyms = list(constraints)
    print('HERE are the synonyms:', synonyms)
    
    constraints = set()
    skipped = 0
    for word_pair in antonyms:
        for i, word in enumerate(word_pair):
            if word not in we.keys():
                word_pair[i] = word.lower()
            if word_pair[0] in we.keys() and word_pair[1] in we.keys() and word_pair[0] != word_pair[1]:
                constraints |= {(vocab_index[word_pair[0]], vocab_index[word_pair[1]])}
            else:
                skipped += 1
    print("{} constraints skipped ({:.2f}% of total)".format(skipped, skipped/i*100))
    antonyms = list(constraints)
    print('HERE are the antonyms:', antonyms)
    
    W_dynamic, negative_examples_repel, repel_examples, repel_cost_step, repel_margin, attract_margin, regularisation_constant, negative_examples_attract, attract_examples, attract_cost_step, embedding_attract_left, embedding_attract_right, embedding_repel_left, embedding_repel_right = initialise_model(np.array(list(we.values())))
    we_copy=we.copy()

    init = tf.global_variables_initializer()

    sess = tf.Session()
    sess.run(init)
    
    
    current_iteration = 0
    
    syn_count=len(synonyms)
    ant_count=len(antonyms)
    
    syn_batches = int(syn_count / batch_size)
    ant_batches = int(ant_count / batch_size)
    batches_per_epoch = syn_batches + ant_batches
    
    last_time = time.time()
    
    while current_iteration < iterations:
        antonym_counter = 0
        synonym_counter = 0
        
        order_of_synonyms = list(range(0, syn_count))
        order_of_antonyms = list(range(0, ant_count))
        
        random.shuffle(order_of_synonyms)
        random.shuffle(order_of_antonyms)
        
        list_of_batch_types = [0] * batches_per_epoch
        list_of_batch_types[syn_batches:] = [1] * ant_batches  # all antonym batches to 1
        random.shuffle(list_of_batch_types)

        if current_iteration == 0:
            print("\nStarting epoch:", current_iteration + 1, "\n")
        else:
            print("\nStarting epoch:", current_iteration + 1, "Last epoch took:", round(time.time() - last_time,
                                                                                            1), "seconds. \n")
            last_time = time.time()
            
        for batch_index in range(0, batches_per_epoch):
            
            syn_or_ant_batch = list_of_batch_types[batch_index]
            
            if syn_or_ant_batch == 0:

                synonymy_examples = [synonyms[order_of_synonyms[x]] for x in
                                    range(synonym_counter * batch_size,
                                          (synonym_counter + 1) * batch_size)]
                current_negatives = extract_negative_examples(synonymy_examples, sess, embedding_attract_left, embedding_attract_right, attract_examples, attract_batch=True)

                sess.run([attract_cost_step], feed_dict={attract_examples: synonymy_examples,
                                                                    negative_examples_attract: current_negatives, \
                                                                    attract_margin: attr_margin,
                                                                    regularisation_constant: l2_reg_constant})
                synonym_counter += 1

            else:

                antonymy_examples = [antonyms[order_of_antonyms[x]] for x in
                                     range(antonym_counter * batch_size,
                                           (antonym_counter + 1) * batch_size)]
                current_negatives = extract_negative_examples(antonymy_examples, sess, embedding_attract_left, embedding_attract_right, attract_examples, attract_batch=False)

                sess.run([repel_cost_step], feed_dict={repel_examples: antonymy_examples,
                                                                negative_examples_repel: current_negatives, \
                                                                repel_margin: rep_margin,
                                                                regularisation_constant: l2_reg_constant})

                antonym_counter += 1

        current_iteration += 1
                
        [current_vectors] = sess.run([W_dynamic])
        for idx, word in enumerate(we_copy):
            we_copy[word] = current_vectors[idx, :] / np.linalg.norm(current_vectors[idx, :])
    
    return we_copy
        
    
def random_different_from(top_range, number_to_not_repeat):
    result = random.randint(0, top_range - 1)
    while result == number_to_not_repeat:
        result = random.randint(0, top_range - 1)

    return result

        
def mix_sampling(list_of_examples, negative_examples):

    #Converts half of the negative examples to random words from the batch (that are not in the given example pair).

    mixed_negative_examples = []
    batch_size = len(list_of_examples)

    for idx, (left_idx, right_idx) in enumerate(negative_examples):

        new_left = left_idx
        new_right = right_idx

        if random.random() >= 0.5:
            new_left = list_of_examples[random_different_from(batch_size, idx)][random.randint(0, 1)]

        if random.random() >= 0.5:
            new_right = list_of_examples[random_different_from(batch_size, idx)][random.randint(0, 1)]

        mixed_negative_examples.append((new_left, new_right))

    return mixed_negative_examples



"""
Linear projection:
    Dev, S., & Phillips, J. M. (2019). Attenuating Bias in Word Vectors. CoRR, abs/1901.07656. 
    Retrieved from http://arxiv.org/abs/1901.07656
"""
def linear_projection(we, gender_direction):
    we_copy=we.copy()
    for key in we_copy.keys():
        we_copy[key]=we_copy[key]-measurements.vector_projection(we_copy[key], gender_direction)
    return we_copy



"""
Double Hard Debiased: 
    Wang, T., Lin, X. V., Rajani, N. F., McCann, B., Ordonez, V., & Xiong, C. (2020, July). Double-Hard Debias: 
    Tailoring Word Embeddings for Gender Bias Mitigation. Association for Computational Linguistics (ACL)
"""
def double_hard_debiasing(we, female_words, male_words, gender_pairs=None, female_words_direction=None, male_words_direction=None):
    X=[]
    X_words=[]
    Y=[]
    we_copy=we.copy()
    vector_dim=len(we_copy[female_words[0]])

    for word in male_words+female_words:
        X.append(we_copy[word])
        X_words.append(word)
        if word in male_words:
            Y.append(1)
        else:
            Y.append(0)
    if gender_pairs==None:
        for word in female_words_direction:
            if word not in female_words:
                X.append(we_copy[word])
                X_words.append(word)
                Y.append(0)
        for word in male_words_direction:
            if word not in male_words:
                X.insert(0, we_copy[word])
                X_words.insert(0, word)
                Y.insert(0, 1)
    else:
        for pair in gender_pairs:
            if pair[0] not in female_words:
                X.append(we_copy[pair[0]])
                X_words.append(pair[0])
                Y.append(0)
            
            if pair[1] not in male_words:
                X.insert(0, we_copy[pair[1]])
                X_words.insert(0, pair[1])
                Y.insert(0, 1)

    aux=[]
    for value in we_copy.values():
        aux.append(value)
        
    we_mean=np.mean(np.array(np.mean(aux, axis=0)), axis=0)
    we_hat=np.zeros((len(we_copy), vector_dim)).astype(float)
    for i, word in enumerate(we_copy.keys()):
        we_hat[i, :]=we_copy[word]-we_mean
        
    main_pca=PCA()
    main_pca.fit(we_hat)
    
    metrics=[]
    
    for component_id in range(min(len(female_words + male_words), 20)):

        #get rid of frequency features
        we_f={}
        
        for i, x in enumerate(X):
            u=x
            sub=np.zeros(u.shape).astype(float)
            sub += np.dot(np.dot(np.transpose(main_pca.components_[component_id]), u), main_pca.components_[component_id])
            we_f[X_words[i]]=x - sub - we_mean
            
        
        #hard debias
        if gender_pairs==None:
            gender_direction=gender_direction_search.two_means(we_f, female_words_direction, male_words_direction)
        else:
            gender_direction=gender_direction_search.PCA_pairs(we_f, gender_pairs)

        we_debiased=hard_debiasing(we_f, [], X_words, gender_direction)
        X_debiased=[we_debiased[key] for key in we_debiased.keys()]

        #KMeans
        kmeans = KMeans(n_clusters=2, random_state=1).fit(X_debiased)
        y_pred = kmeans.predict(X_debiased)
        correct = [1 if item1 == item2 else 0 for (item1,item2) in zip(Y, y_pred)]
        precision = max(sum(correct)/float(len(correct)), 1 - sum(correct)/float(len(correct)))
        metrics.append(precision)
    
    #get min metric, get rid of frequency features and apply hard debiasing
    k=metrics.index(min(metrics))
    we_f={}
    for i, x in enumerate(we_copy.keys()):
        u=we_copy[x]
        sub=np.zeros(u.shape).astype(float)
        sub += np.dot(np.dot(np.transpose(main_pca.components_[k]), u), main_pca.components_[k])
        aux=we_copy[x] - sub - we_mean
        we_copy[x]=aux
        we_f[x]=aux
        
    if gender_pairs==None:
        gender_direction=gender_direction_search.two_means(we_copy, female_words_direction, male_words_direction)
    else:
        gender_direction=gender_direction_search.PCA_pairs(we_copy, gender_pairs)

    we_copy=hard_debiasing(we_copy, [], list(we_copy.keys()), gender_direction)

    return we_copy, main_pca.components_[k], we_f, gender_direction

"""
Iterative Nullspace Projection:
    Ravfogel, S., Elazar, Y., Gonen, H., Twiton, M., & Goldberg, Y. (2020). Null It Out: Guarding Protected 
    Attributes by Iterative Nullspace Projection. ACL.
"""

def get_rowspace_projection(W):

    if np.allclose(W, 0):
        w_basis = np.zeros_like(W.T)
    else:
        w_basis = scipy.linalg.orth(W.T) # orthogonal basis

    P_W = w_basis.dot(w_basis.T) # orthogonal projection on W's rowspace

    return P_W


def get_projection_to_intersection_of_nullspaces(rowspace_projection_matrices, vector_dim):
       
    I = np.eye(vector_dim)
    Q = np.sum(rowspace_projection_matrices, axis = 0)
    P = I - get_rowspace_projection(Q)

    return P


def INLP(we, female_words, male_words, neutral_words, num_iter=35):
    we_copy=we.copy()
    vector_dim=len(we_copy[female_words[0]])
    X_train_words=[]
    X_train=[]
    Y_train=[]

    for word in random.sample(female_words + male_words, len(female_words + male_words)):
        if word in female_words:
            Y_train.append(0)
        else:
            Y_train.append(1)
        X_train_words.append(word)
        X_train.append(we_copy[word])
        
        
    neutral_words_debiased=[]
    for word in neutral_words:
        neutral_words_debiased.append(we_copy[word])
    
    X_train=np.array(X_train)
    Y_train=np.array(Y_train)
    neutral_words_debiased=np.array(neutral_words_debiased)
    rowspace_projections=[]
    Ws=[]
    
    for i in range(num_iter):
        

        W = gender_direction_search.classification(X_train, Y_train)
        if len(W.shape) == 1:
                W = np.expand_dims(W, 0)
        Ws.append(W)

        P_rowspace_wi = get_rowspace_projection(W)

        rowspace_projections.append(P_rowspace_wi)

        P = get_projection_to_intersection_of_nullspaces(rowspace_projections, vector_dim)

        X_train = (P.dot(X_train.T)).T
        neutral_words_debiased=(P.dot(neutral_words_debiased.T)).T
    
    
    for i, word in enumerate(X_train_words):
        we_copy[word]=X_train[i]
    for i, word in enumerate(neutral_words):
        we_copy[word]=neutral_words_debiased[i]
    return we_copy
