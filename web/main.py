# -*- coding: utf-8 -*-
"""
Created on Tue May  9 05:48:42 2023

@author: Samuel
"""
import sys
import os
import random
import string
from flask import Flask, render_template, request, jsonify
from src import glove
from src import word2vec
from src import debias
from src import files
from src import gender_direction_search
from src import measurements
from src import word_embeddings
from src import visualization







wordEmbeddings=[]

 
app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def index():
    return render_template('index.html')
    
@app.route("/upload_we", methods=['POST'])
def upload_we():
    if not os.path.exists(request.json['path']):
        return
    word_embedding=word_embeddings.WordEmbeddings("")
    filename=os.path.splitext(os.path.basename(request.json['path']))
    
    #check if name already exists and if so add a random char
    names=[]
    filename=filename[0]
    for we in wordEmbeddings:
        names.append(we.name)
    while(filename in names):
        filename = filename+random.choice(string.ascii_letters)
    
    word_embedding.name=filename
    word_embedding.we=files.upload_word_embeddings(request.json['path'])
    word_embedding.vector_size=len(next(iter(word_embedding.we.values())))
    wordEmbeddings.append(word_embedding)
    return jsonify({'name': word_embedding.name, 'vector_size': word_embedding.vector_size, 'num_words': len(word_embedding.we)})


@app.route("/compute_glove", methods=['POST'])
def compute_glove():
    if not os.path.exists(request.json['path']):
        return
    corpus=files.upload_corpus(request.json['path'])
    corpus=files.preprocessing_glove(corpus)
    word_embedding=glove.Glove(corpus=corpus, vector_size=request.json['vector_size'], window_size=request.json['window_size'], min_count=request.json['min_count'], iterations=request.json['iterations'], learning_rate=request.json['lr'], alpha=request.json['alpha'], x_max=request.json['x_max'])
    filename=os.path.splitext(os.path.basename(request.json['path']))
    
    #check if name already exists and if so add a random char
    names=[]
    filename=filename[0]
    for we in wordEmbeddings:
        names.append(we.name)
    while(filename in names):
        filename = filename+random.choice(string.ascii_letters)
    
    word_embedding.name=filename
    wordEmbeddings.append(word_embedding)
    return jsonify({'name': word_embedding.name, 'vector_size': word_embedding.vector_size, 'num_words': len(word_embedding.we)})


@app.route("/compute_w2v", methods=['POST'])
def compute_w2v():
    if not os.path.exists(request.json['path']):
        return
    corpus=files.upload_corpus(request.json['path'])
    corpus=files.preprocessing_word2vec(corpus)
    word_embedding=word2vec.Word2vec(corpus=corpus, vector_size=request.json['vector_size'], window_size=request.json['window_size'], min_count=request.json['min_count'])
    filename=os.path.splitext(os.path.basename(request.json['path']))
    
    #check if name already exists and if so add a random char
    names=[]
    filename=filename[0]
    for we in wordEmbeddings:
        names.append(we.name)
    while(filename in names):
        filename = filename+random.choice(string.ascii_letters)
    
    word_embedding.name=filename
    wordEmbeddings.append(word_embedding)
    return jsonify({'name': word_embedding.name, 'vector_size': word_embedding.vector_size, 'num_words': len(word_embedding.we)})


@app.route("/save_we", methods=['GET','POST'])
def save_we():
    for word_embedding in wordEmbeddings:
        if word_embedding.name==request.json['name']:
            files.save_word_embeddings(word_embedding.name + ".txt", word_embedding.we)
            break
    print("Saved file: " + request.json['name'] + ".txt")
    return jsonify({})


@app.route("/delete_we", methods=['GET','POST'])
def delete_we():
    aux=0
    for i, word_embedding in enumerate(wordEmbeddings):
        if word_embedding.name==request.json['name']:
            aux=i
            break
    del wordEmbeddings[aux]
    print(wordEmbeddings)
    return jsonify({})


@app.route("/hard", methods=['GET','POST'])
def hard():
    for word_embedding in wordEmbeddings:
        if word_embedding.name==request.json['name']:
            break
    gender_specific_words=request.json['gender_specific_words']
    gender_specific_words=gender_specific_words.replace(" ", "").split(";")
    aux=[]
    for pair in gender_specific_words:
        aux2=pair.split(',')
        if aux2[0] in word_embedding.we.keys() and aux2[1] in word_embedding.we.keys():
            aux.append([aux2[0], aux2[1]])
    gender_specific_words=aux
    if not gender_specific_words:
        print("Error: No gender specific words found")
        return jsonify({"error": "No gender specific words found"}), 400
    
    female_words=[item[1] for item in gender_specific_words]
    male_words=[item[0] for item in gender_specific_words]
    
    gender_neutral_words=request.json['gender_neutral_words']
    gender_neutral_words=gender_neutral_words.replace(" ", "").split(",")
    aux=[]
    for word in gender_neutral_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    gender_neutral_words=aux
    if not gender_neutral_words:
        print("Error: No gender neutral words found")
        return jsonify({"error": "No gender neutral words found"}), 400
    
    if request.json['gender_direction'] == 'pca':
        pairs=request.json['pairs']
        pairs=pairs.replace(" ", "").split(";")
        aux=[]
        for pair in pairs:
            aux2=pair.split(',')
            if aux2[0] in word_embedding.we.keys() and aux2[1] in word_embedding.we.keys():
                aux.append([aux2[0], aux2[1]])
        pairs=aux
        if not pairs:
            print("Error: No gender pairs found")
            return jsonify({"error": "No gender pairs found"}), 400
        
        gender_direction=gender_direction_search.PCA_pairs(word_embedding.we, pairs)
             
        female_words_direction=[item[0] for item in pairs]
        male_words_direction=[item[1] for item in pairs]
        
        
    elif request.json['gender_direction'] == 'two_means':
        female_words_direction=request.json['female_words_direction']
        female_words_direction=female_words_direction.replace(" ", "").split(",")
        male_words_direction=request.json['male_words_direction']
        male_words_direction=male_words_direction.replace(" ", "").split(",")
        
        aux_female=[]
        aux_male=[]
        for i, word in enumerate(female_words_direction):
            if female_words_direction[i] in word_embedding.we.keys() and male_words_direction[i] in word_embedding.we.keys():
                aux_female.append(female_words_direction[i])
                aux_male.append(male_words_direction[i])
        female_words_direction=aux_female
        male_words_direction=aux_male
        if not female_words_direction and not male_words_direction:
            return
        
        gender_direction=gender_direction_search.two_means(word_embedding.we, female_words_direction, male_words_direction)
 
        
    else:
        return

    female_words_all=list(dict.fromkeys(female_words+female_words_direction))
    male_words_all=list(dict.fromkeys(male_words+male_words_direction))
    masc_words0, fem_words0, neutral_words0, vector_gender_direction0=visualization.reduction_embeddings_to_2d(word_embedding.we, male_words_all, female_words_all, gender_neutral_words, gender_direction)
    masc_words1, fem_words1, neutral_words1, vector_gender_direction1=visualization.reduction_embeddings_to_2d_gender_direction_x(word_embedding.we, male_words_all, female_words_all, gender_neutral_words, gender_direction)
    
    debiased_embedding=debias.hard_debiasing(word_embedding.we, gender_specific_words, gender_neutral_words, gender_direction)
    
    masc_words2, fem_words2, neutral_words2, vector_gender_direction2=visualization.reduction_embeddings_to_2d_gender_direction_x(debiased_embedding, male_words_all, female_words_all, gender_neutral_words, gender_direction)
    masc_words3, fem_words3, neutral_words3, vector_gender_direction3=visualization.reduction_embeddings_to_2d(debiased_embedding, male_words_all, female_words_all, gender_neutral_words, gender_direction-gender_direction+1e-8)
    
    
    return_var=[]
    dictionary0={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary1={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary2={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary3={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}

    
    for i, word in enumerate(female_words_all):
        dictionary0['fem'][i]={'label':word, 'x':fem_words0[i][0], 'y':fem_words0[i][1]}
        dictionary1['fem'][i]={'label':word, 'x':fem_words1[i][0], 'y':fem_words1[i][1]}
        dictionary2['fem'][i]={'label':word, 'x':fem_words2[i][0], 'y':fem_words2[i][1]}
        dictionary3['fem'][i]={'label':word, 'x':fem_words3[i][0], 'y':fem_words3[i][1]}
        
    for i, word in enumerate(male_words_all):
        dictionary0['masc'][i]={'label':word, 'x':masc_words0[i][0], 'y':masc_words0[i][1]}
        dictionary1['masc'][i]={'label':word, 'x':masc_words1[i][0], 'y':masc_words1[i][1]}
        dictionary2['masc'][i]={'label':word, 'x':masc_words2[i][0], 'y':masc_words2[i][1]}
        dictionary3['masc'][i]={'label':word, 'x':masc_words3[i][0], 'y':masc_words3[i][1]}
       
    for i, word in enumerate(gender_neutral_words):
        dictionary0['neutral'][i]={'label':word, 'x':neutral_words0[i][0], 'y':neutral_words0[i][1]}
        dictionary1['neutral'][i]={'label':word, 'x':neutral_words1[i][0], 'y':neutral_words1[i][1]}
        dictionary2['neutral'][i]={'label':word, 'x':neutral_words2[i][0], 'y':neutral_words2[i][1]}
        dictionary3['neutral'][i]={'label':word, 'x':neutral_words3[i][0], 'y':neutral_words3[i][1]}

    for i in range(len(vector_gender_direction0)):
        dictionary0['gender_direction'][i]={'x':vector_gender_direction0[i][0], 'y':vector_gender_direction0[i][1]}
        dictionary1['gender_direction'][i]={'x':vector_gender_direction1[i][0], 'y':vector_gender_direction1[i][1]}
        dictionary2['gender_direction'][i]={'x':vector_gender_direction2[i][0], 'y':vector_gender_direction2[i][1]}
        dictionary3['gender_direction'][i]={'x':vector_gender_direction3[i][0], 'y':vector_gender_direction3[i][1]}
        
          
    word_embedding=word_embeddings.WordEmbeddings("", vector_size=len(next(iter(debiased_embedding.values()))))
    word_embedding.we=debiased_embedding
    name=request.json['name']+"_hard_debiased"
    names=[]
    for we in wordEmbeddings:
        names.append(we.name)
    while(name in names):
        name = name+random.choice(string.ascii_letters)
    
    word_embedding.name=name
    wordEmbeddings.append(word_embedding)
    
    return_var.append({'name': word_embedding.name, 'vector_size': word_embedding.vector_size, 'num_words': len(word_embedding.we)})
    return_var.append(dictionary0)
    return_var.append(dictionary1)
    return_var.append(dictionary2)
    return_var.append(dictionary3)
    return jsonify(return_var)




@app.route("/soft", methods=['GET','POST'])
def soft():
    for word_embedding in wordEmbeddings:
        if word_embedding.name==request.json['name']:
            break
   
    female_words=request.json['female_words']
    female_words=female_words.replace(" ", "").split(",")
    aux=[]
    for word in female_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    female_words=aux
    if not female_words:
        return

    male_words=request.json['male_words']
    male_words=male_words.replace(" ", "").split(",")
    aux=[]
    for word in male_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    male_words=aux
    if not male_words:
        return
    
    gender_neutral_words=request.json['gender_neutral_words']
    gender_neutral_words=gender_neutral_words.replace(" ", "").split(",")
    aux=[]
    for word in gender_neutral_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    gender_neutral_words=aux
    if not gender_neutral_words:
        return

    gender_specific_words=[]
    for word in female_words+male_words:
        gender_specific_words.append(word)

    landa=float(request.json['landa'])
    epochs=int(request.json['epochs'])
    lr=float(request.json['lr'])
    momentum=float(request.json['momentum'])


    if request.json['gender_direction'] == 'pca':
        pairs=request.json['pairs']
        pairs=pairs.replace(" ", "").split(";")
        aux=[]
        for pair in pairs:
            aux2=pair.split(',')
            if aux2[0] in word_embedding.we.keys() and aux2[1] in word_embedding.we.keys():
                aux.append([aux2[0], aux2[1]])
        pairs=aux
        if not pairs:
            return
        
        gender_direction=gender_direction_search.PCA_pairs(word_embedding.we, pairs)
        
        female_words_direction=[item[0] for item in pairs]
        male_words_direction=[item[1] for item in pairs]
        
        
    elif request.json['gender_direction'] == 'two_means':
        female_words_direction=request.json['female_words_direction']
        female_words_direction=female_words_direction.replace(" ", "").split(",")
        male_words_direction=request.json['male_words_direction']
        male_words_direction=male_words_direction.replace(" ", "").split(",")
        
        aux_female=[]
        aux_male=[]
        for i, word in enumerate(female_words_direction):
            if female_words_direction[i] in word_embedding.we.keys() and male_words_direction[i] in word_embedding.we.keys():
                aux_female.append(female_words_direction[i])
                aux_male.append(male_words_direction[i])
        female_words_direction=aux_female
        male_words_direction=aux_male
        if not female_words_direction and not male_words_direction:
            return
        
        gender_direction=gender_direction_search.two_means(word_embedding.we, female_words_direction, male_words_direction)


    else:
        return

    female_words_all=list(dict.fromkeys(female_words+female_words_direction))
    male_words_all=list(dict.fromkeys(male_words+male_words_direction))
    masc_words0, fem_words0, neutral_words0, vector_gender_direction0=visualization.reduction_embeddings_to_2d(word_embedding.we, male_words_all, female_words_all, gender_neutral_words, gender_direction)
    masc_words1, fem_words1, neutral_words1, vector_gender_direction1=visualization.reduction_embeddings_to_2d_gender_direction_x(word_embedding.we, male_words_all, female_words_all, gender_neutral_words, gender_direction)
    
    debiased_embedding=debias.soft_debiasing(word_embedding.we, gender_specific_words, gender_direction, landa, epochs, lr, momentum)
    
    masc_words2, fem_words2, neutral_words2, vector_gender_direction2=visualization.reduction_embeddings_to_2d_gender_direction_x(debiased_embedding, male_words_all, female_words_all, gender_neutral_words, gender_direction)
    masc_words3, fem_words3, neutral_words3, vector_gender_direction3=visualization.reduction_embeddings_to_2d(debiased_embedding, male_words_all, female_words_all, gender_neutral_words, gender_direction-gender_direction+1e-8)
    
    
    return_var=[]
    dictionary0={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary1={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary2={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary3={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}

    
    for i, word in enumerate(female_words_all):
        dictionary0['fem'][i]={'label':word, 'x':fem_words0[i][0], 'y':fem_words0[i][1]}
        dictionary1['fem'][i]={'label':word, 'x':fem_words1[i][0], 'y':fem_words1[i][1]}
        dictionary2['fem'][i]={'label':word, 'x':fem_words2[i][0], 'y':fem_words2[i][1]}
        dictionary3['fem'][i]={'label':word, 'x':fem_words3[i][0], 'y':fem_words3[i][1]}
        
    for i, word in enumerate(male_words_all):
        dictionary0['masc'][i]={'label':word, 'x':masc_words0[i][0], 'y':masc_words0[i][1]}
        dictionary1['masc'][i]={'label':word, 'x':masc_words1[i][0], 'y':masc_words1[i][1]}
        dictionary2['masc'][i]={'label':word, 'x':masc_words2[i][0], 'y':masc_words2[i][1]}
        dictionary3['masc'][i]={'label':word, 'x':masc_words3[i][0], 'y':masc_words3[i][1]}
       
    for i, word in enumerate(gender_neutral_words):
        dictionary0['neutral'][i]={'label':word, 'x':neutral_words0[i][0], 'y':neutral_words0[i][1]}
        dictionary1['neutral'][i]={'label':word, 'x':neutral_words1[i][0], 'y':neutral_words1[i][1]}
        dictionary2['neutral'][i]={'label':word, 'x':neutral_words2[i][0], 'y':neutral_words2[i][1]}
        dictionary3['neutral'][i]={'label':word, 'x':neutral_words3[i][0], 'y':neutral_words3[i][1]}

    for i in range(len(vector_gender_direction0)):
        dictionary0['gender_direction'][i]={'x':vector_gender_direction0[i][0], 'y':vector_gender_direction0[i][1]}
        dictionary1['gender_direction'][i]={'x':vector_gender_direction1[i][0], 'y':vector_gender_direction1[i][1]}
        dictionary2['gender_direction'][i]={'x':vector_gender_direction2[i][0], 'y':vector_gender_direction2[i][1]}
        dictionary3['gender_direction'][i]={'x':vector_gender_direction3[i][0], 'y':vector_gender_direction3[i][1]}
 
    
    word_embedding=word_embeddings.WordEmbeddings("", vector_size=len(next(iter(debiased_embedding.values()))))
    word_embedding.we=debiased_embedding
    name=request.json['name']+"_soft_debiased"
    names=[]
    for we in wordEmbeddings:
        names.append(we.name)
    while(name in names):
        name = name+random.choice(string.ascii_letters)
    
    word_embedding.name=name
    wordEmbeddings.append(word_embedding)

    return_var.append({'name': word_embedding.name, 'vector_size': word_embedding.vector_size, 'num_words': len(word_embedding.we)})
    return_var.append(dictionary0)
    return_var.append(dictionary1)
    return_var.append(dictionary2)
    return_var.append(dictionary3)
    return jsonify(return_var)



@app.route("/attract", methods=['GET','POST'])
def attract():
    for word_embedding in wordEmbeddings:
        if word_embedding.name==request.json['name']:
            break
    female_words=request.json['female_words']
    female_words=female_words.replace(" ", "").split(",")
    aux=[]
    for word in female_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    female_words=aux
    if not female_words:
        return

    male_words=request.json['male_words']
    male_words=male_words.replace(" ", "").split(",")
    aux=[]
    for word in male_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    male_words=aux
    if not male_words:
        return

    
    stereotypically_female_words=request.json['stereotypically_female_words']
    stereotypically_female_words=stereotypically_female_words.replace(" ", "").split(",")
    aux=[]
    for word in stereotypically_female_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    stereotypically_female_words=aux
    if not stereotypically_female_words:
        return

    stereotypically_male_words=request.json['stereotypically_male_words']
    stereotypically_male_words=stereotypically_male_words.replace(" ", "").split(",")
    aux=[]
    for word in stereotypically_male_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    stereotypically_male_words=aux
    if not stereotypically_male_words:
        return

    antonyms=[]
    synonyms=[]
    for word in female_words:
        for word2 in stereotypically_female_words:
            antonyms.append([word,word2])
        for word2 in stereotypically_male_words:
            synonyms.append([word,word2])

    for word in male_words:
        for word2 in stereotypically_female_words:
            synonyms.append([word,word2])
        for word2 in stereotypically_male_words:
            antonyms.append([word,word2])


    iterations=int(request.json['iterations'])
    batch_size=int(request.json['batch_size'])
    attr_margin=float(request.json['attr_margin'])
    rep_margin=float(request.json['rep_margin'])
    l2_reg_constant=float(request.json['l2_reg_constant'])

    gender_neutral_words=list(dict.fromkeys(stereotypically_female_words+stereotypically_male_words))
    
    masc_words0, fem_words0, neutral_words0=visualization.reduction_embeddings_to_2d(word_embedding.we, male_words, female_words, gender_neutral_words)

    debiased_embedding=debias.attract_repel(word_embedding.we, synonyms, antonyms, iterations, batch_size, attr_margin, rep_margin, l2_reg_constant)
    
    masc_words1, fem_words1, neutral_words1=visualization.reduction_embeddings_to_2d(debiased_embedding, male_words, female_words, gender_neutral_words)

    return_var=[]
    dictionary0={'fem':{}, 'masc':{}, 'neutral':{}}
    dictionary1={'fem':{}, 'masc':{}, 'neutral':{}}
    
    for i, word in enumerate(female_words):
        dictionary0['fem'][i]={'label':word, 'x':fem_words0[i][0], 'y':fem_words0[i][1]}
        dictionary1['fem'][i]={'label':word, 'x':fem_words1[i][0], 'y':fem_words1[i][1]}
     
    for i, word in enumerate(male_words):
        dictionary0['masc'][i]={'label':word, 'x':masc_words0[i][0], 'y':masc_words0[i][1]}
        dictionary1['masc'][i]={'label':word, 'x':masc_words1[i][0], 'y':masc_words1[i][1]}
    
    for i, word in enumerate(gender_neutral_words):
        dictionary0['neutral'][i]={'label':word, 'x':neutral_words0[i][0], 'y':neutral_words0[i][1]}
        dictionary1['neutral'][i]={'label':word, 'x':neutral_words1[i][0], 'y':neutral_words1[i][1]}

    
    word_embedding=word_embeddings.WordEmbeddings("", vector_size=len(next(iter(debiased_embedding.values()))))
    word_embedding.we=debiased_embedding
    name=request.json['name']+"_attract-repel_debiased"
    names=[]
    for we in wordEmbeddings:
        names.append(we.name)
    while(name in names):
        name = name+random.choice(string.ascii_letters)
    
    word_embedding.name=name
    wordEmbeddings.append(word_embedding)

    return_var.append({'name': word_embedding.name, 'vector_size': word_embedding.vector_size, 'num_words': len(word_embedding.we)})
    return_var.append(dictionary0)
    return_var.append(dictionary1)
    return jsonify(return_var)    




@app.route("/linear", methods=['GET','POST'])
def linear():
    for word_embedding in wordEmbeddings:
        if word_embedding.name==request.json['name']:
            break
   
    visualize_words=request.json['visualize_words']
    visualize_words=visualize_words.replace(" ", "").split(",")
    aux=[]
    for word in visualize_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    visualize_words=aux
    if not visualize_words:
        return
    
    if request.json['gender_direction'] == 'pca':
        pairs=request.json['pairs']
        pairs=pairs.replace(" ", "").split(";")
        aux=[]
        for pair in pairs:
            aux2=pair.split(',')
            if aux2[0] in word_embedding.we.keys() and aux2[1] in word_embedding.we.keys():
                aux.append([aux2[0], aux2[1]])
        pairs=aux
        if not pairs:
            return
        
        gender_direction=gender_direction_search.PCA_pairs(word_embedding.we, pairs)
             
        female_words_direction=[item[0] for item in pairs]
        male_words_direction=[item[1] for item in pairs]
    
    elif request.json['gender_direction'] == 'two_means':
        female_words_direction=request.json['female_words_direction']
        female_words_direction=female_words_direction.replace(" ", "").split(",")
        male_words_direction=request.json['male_words_direction']
        male_words_direction=male_words_direction.replace(" ", "").split(",")
        
        aux_female=[]
        aux_male=[]
        for i, word in enumerate(female_words_direction):
            if female_words_direction[i] in word_embedding.we.keys() and male_words_direction[i] in word_embedding.we.keys():
                aux_female.append(female_words_direction[i])
                aux_male.append(male_words_direction[i])
        female_words_direction=aux_female
        male_words_direction=aux_male
        if not female_words_direction and not male_words_direction:
            return
        
        gender_direction=gender_direction_search.two_means(word_embedding.we, female_words_direction, male_words_direction)
 
        
    else:
        return
    
    masc_words0, fem_words0, neutral_words0, vector_gender_direction0=visualization.reduction_embeddings_to_2d(word_embedding.we, male_words_direction, female_words_direction, visualize_words, gender_direction)
    masc_words1, fem_words1, neutral_words1, vector_gender_direction1=visualization.reduction_embeddings_to_2d_gender_direction_x(word_embedding.we, male_words_direction, female_words_direction, visualize_words, gender_direction)
        
    debiased_embedding=debias.linear_projection(word_embedding.we, gender_direction)

    masc_words2, fem_words2, neutral_words2, vector_gender_direction2=visualization.reduction_embeddings_to_2d_gender_direction_x(debiased_embedding, male_words_direction, female_words_direction, visualize_words, gender_direction)
    masc_words3, fem_words3, neutral_words3, vector_gender_direction3=visualization.reduction_embeddings_to_2d(debiased_embedding, male_words_direction, female_words_direction, visualize_words, gender_direction)
       
    return_var=[]
    dictionary0={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary1={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary2={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary3={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}

    
    for i, word in enumerate(female_words_direction):
        dictionary0['fem'][i]={'label':word, 'x':fem_words0[i][0], 'y':fem_words0[i][1]}
        dictionary1['fem'][i]={'label':word, 'x':fem_words1[i][0], 'y':fem_words1[i][1]}
        dictionary2['fem'][i]={'label':word, 'x':fem_words2[i][0], 'y':fem_words2[i][1]}
        dictionary3['fem'][i]={'label':word, 'x':fem_words3[i][0], 'y':fem_words3[i][1]}
        
    for i, word in enumerate(male_words_direction):
        dictionary0['masc'][i]={'label':word, 'x':masc_words0[i][0], 'y':masc_words0[i][1]}
        dictionary1['masc'][i]={'label':word, 'x':masc_words1[i][0], 'y':masc_words1[i][1]}
        dictionary2['masc'][i]={'label':word, 'x':masc_words2[i][0], 'y':masc_words2[i][1]}
        dictionary3['masc'][i]={'label':word, 'x':masc_words3[i][0], 'y':masc_words3[i][1]}
       
    for i, word in enumerate(visualize_words):
        dictionary0['neutral'][i]={'label':word, 'x':neutral_words0[i][0], 'y':neutral_words0[i][1]}
        dictionary1['neutral'][i]={'label':word, 'x':neutral_words1[i][0], 'y':neutral_words1[i][1]}
        dictionary2['neutral'][i]={'label':word, 'x':neutral_words2[i][0], 'y':neutral_words2[i][1]}
        dictionary3['neutral'][i]={'label':word, 'x':neutral_words3[i][0], 'y':neutral_words3[i][1]}

    for i in range(len(vector_gender_direction0)):
        dictionary0['gender_direction'][i]={'x':vector_gender_direction0[i][0], 'y':vector_gender_direction0[i][1]}
        dictionary1['gender_direction'][i]={'x':vector_gender_direction1[i][0], 'y':vector_gender_direction1[i][1]}
        dictionary2['gender_direction'][i]={'x':vector_gender_direction2[i][0], 'y':vector_gender_direction2[i][1]}
        dictionary3['gender_direction'][i]={'x':vector_gender_direction3[i][0], 'y':vector_gender_direction3[i][1]}

    
    word_embedding=word_embeddings.WordEmbeddings("", vector_size=len(next(iter(debiased_embedding.values()))))
    word_embedding.we=debiased_embedding
    name=request.json['name']+"_linearP_debiased"
    names=[]
    for we in wordEmbeddings:
        names.append(we.name)
    while(name in names):
        name = name+random.choice(string.ascii_letters)
    
    word_embedding.name=name
    wordEmbeddings.append(word_embedding)
    
    return_var.append({'name': word_embedding.name, 'vector_size': word_embedding.vector_size, 'num_words': len(word_embedding.we)})
    return_var.append(dictionary0)
    return_var.append(dictionary1)
    return_var.append(dictionary2)
    return_var.append(dictionary3)
    return jsonify(return_var)




@app.route("/double", methods=['GET','POST'])
def double():
    for word_embedding in wordEmbeddings:
        if word_embedding.name==request.json['name']:
            break
    female_words=request.json['female_words']
    female_words=female_words.replace(" ", "").split(",")
    aux=[]
    for word in female_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    female_words=aux
    if not female_words:
        return

    male_words=request.json['male_words']
    male_words=male_words.replace(" ", "").split(",")
    aux=[]
    for word in male_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    male_words=aux
    if not male_words:
        return

    gender_neutral_words=request.json['gender_neutral_words']
    gender_neutral_words=gender_neutral_words.replace(" ", "").split(",")
    aux=[]
    for word in gender_neutral_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    gender_neutral_words=aux
    if not gender_neutral_words:
        return

    if request.json['gender_direction'] == 'pca':
        pairs=request.json['pairs']
        pairs=pairs.replace(" ", "").split(";")
        aux=[]
        for pair in pairs:
            aux2=pair.split(',')
            if aux2[0] in word_embedding.we.keys() and aux2[1] in word_embedding.we.keys():
                aux.append([aux2[0], aux2[1]])
        pairs=aux
        if not pairs:
            return
        
        debiased_embedding, frequency_direction, we_f, gender_direction=debias.double_hard_debiasing(word_embedding.we, female_words, male_words, gender_pairs=pairs)

        female_words_direction=[item[0] for item in pairs]
        male_words_direction=[item[1] for item in pairs]
    
               
    elif request.json['gender_direction'] == 'two_means':
        female_words_direction=request.json['female_words_direction']
        female_words_direction=female_words_direction.replace(" ", "").split(",")
        male_words_direction=request.json['male_words_direction']
        male_words_direction=male_words_direction.replace(" ", "").split(",")
        
        aux_female=[]
        aux_male=[]
        for i, word in enumerate(female_words_direction):
            if female_words_direction[i] in word_embedding.we.keys() and male_words_direction[i] in word_embedding.we.keys():
                aux_female.append(female_words_direction[i])
                aux_male.append(male_words_direction[i])
        female_words_direction=aux_female
        male_words_direction=aux_male
        if not female_words_direction and not male_words_direction:
            return
        
        debiased_embedding, frequency_direction, we_f, gender_direction=debias.double_hard_debiasing(word_embedding.we, female_words, male_words, female_words_direction=female_words_direction, male_words_direction=male_words_direction)
        
    else:
        return


    female_words_all=list(dict.fromkeys(female_words+female_words_direction))
    male_words_all=list(dict.fromkeys(male_words+male_words_direction))
    masc_words0, fem_words0, neutral_words0, vector_gender_direction0=visualization.reduction_embeddings_to_2d(word_embedding.we, male_words_all, female_words_all, gender_neutral_words, frequency_direction)
    masc_words1, fem_words1, neutral_words1, vector_gender_direction1=visualization.reduction_embeddings_to_2d_gender_direction_x(word_embedding.we, male_words_all, female_words_all, gender_neutral_words, frequency_direction)
    masc_words2, fem_words2, neutral_words2, vector_gender_direction2=visualization.reduction_embeddings_to_2d_gender_direction_x(we_f, male_words_all, female_words_all, gender_neutral_words, frequency_direction)
    masc_words3, fem_words3, neutral_words3, vector_gender_direction3=visualization.reduction_embeddings_to_2d_gender_direction_x(we_f, male_words_all, female_words_all, gender_neutral_words, gender_direction)
    masc_words4, fem_words4, neutral_words4, vector_gender_direction4=visualization.reduction_embeddings_to_2d_gender_direction_x(debiased_embedding, male_words_all, female_words_all, gender_neutral_words, gender_direction)
    masc_words5, fem_words5, neutral_words5, vector_gender_direction5=visualization.reduction_embeddings_to_2d(debiased_embedding, male_words_all, female_words_all, gender_neutral_words, gender_direction)
    
    return_var=[]
    dictionary0={'fem':{}, 'masc':{}, 'neutral':{}, 'frequency_direction':{}}
    dictionary1={'fem':{}, 'masc':{}, 'neutral':{}, 'frequency_direction':{}}
    dictionary2={'fem':{}, 'masc':{}, 'neutral':{}, 'frequency_direction':{}}
    dictionary3={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary4={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}
    dictionary5={'fem':{}, 'masc':{}, 'neutral':{}, 'gender_direction':{}}

    
    for i, word in enumerate(female_words_all):
        dictionary0['fem'][i]={'label':word, 'x':fem_words0[i][0], 'y':fem_words0[i][1]}
        dictionary1['fem'][i]={'label':word, 'x':fem_words1[i][0], 'y':fem_words1[i][1]}
        dictionary2['fem'][i]={'label':word, 'x':fem_words2[i][0], 'y':fem_words2[i][1]}
        dictionary3['fem'][i]={'label':word, 'x':fem_words3[i][0], 'y':fem_words3[i][1]}
        dictionary4['fem'][i]={'label':word, 'x':fem_words4[i][0], 'y':fem_words4[i][1]}
        dictionary5['fem'][i]={'label':word, 'x':fem_words5[i][0], 'y':fem_words5[i][1]}

    for i, word in enumerate(male_words_all):
        dictionary0['masc'][i]={'label':word, 'x':masc_words0[i][0], 'y':masc_words0[i][1]}
        dictionary1['masc'][i]={'label':word, 'x':masc_words1[i][0], 'y':masc_words1[i][1]}
        dictionary2['masc'][i]={'label':word, 'x':masc_words2[i][0], 'y':masc_words2[i][1]}
        dictionary3['masc'][i]={'label':word, 'x':masc_words3[i][0], 'y':masc_words3[i][1]}
        dictionary4['masc'][i]={'label':word, 'x':masc_words4[i][0], 'y':masc_words4[i][1]}
        dictionary5['masc'][i]={'label':word, 'x':masc_words5[i][0], 'y':masc_words5[i][1]}

    for i, word in enumerate(gender_neutral_words):
        dictionary0['neutral'][i]={'label':word, 'x':neutral_words0[i][0], 'y':neutral_words0[i][1]}
        dictionary1['neutral'][i]={'label':word, 'x':neutral_words1[i][0], 'y':neutral_words1[i][1]}
        dictionary2['neutral'][i]={'label':word, 'x':neutral_words2[i][0], 'y':neutral_words2[i][1]}
        dictionary3['neutral'][i]={'label':word, 'x':neutral_words3[i][0], 'y':neutral_words3[i][1]}
        dictionary4['neutral'][i]={'label':word, 'x':neutral_words4[i][0], 'y':neutral_words4[i][1]}
        dictionary5['neutral'][i]={'label':word, 'x':neutral_words5[i][0], 'y':neutral_words5[i][1]}

    for i in range(len(vector_gender_direction0)):
        dictionary0['frequency_direction'][i]={'x':vector_gender_direction0[i][0], 'y':vector_gender_direction0[i][1]}
        dictionary1['frequency_direction'][i]={'x':vector_gender_direction1[i][0], 'y':vector_gender_direction1[i][1]}
        dictionary2['frequency_direction'][i]={'x':vector_gender_direction2[i][0], 'y':vector_gender_direction2[i][1]}
        dictionary3['gender_direction'][i]={'x':vector_gender_direction3[i][0], 'y':vector_gender_direction3[i][1]}
        dictionary4['gender_direction'][i]={'x':vector_gender_direction4[i][0], 'y':vector_gender_direction4[i][1]}
        dictionary5['gender_direction'][i]={'x':vector_gender_direction5[i][0], 'y':vector_gender_direction5[i][1]}





    word_embedding=word_embeddings.WordEmbeddings("", vector_size=len(next(iter(debiased_embedding.values()))))
    word_embedding.we=debiased_embedding
    name=request.json['name']+"_double-HD_debiased"
    names=[]
    for we in wordEmbeddings:
        names.append(we.name)
    while(name in names):
        name = name+random.choice(string.ascii_letters)
    
    word_embedding.name=name
    wordEmbeddings.append(word_embedding)
    return_var.append({'name': word_embedding.name, 'vector_size': word_embedding.vector_size, 'num_words': len(word_embedding.we)})
    return_var.append(dictionary0)
    return_var.append(dictionary1)
    return_var.append(dictionary2)
    return_var.append(dictionary3)
    return_var.append(dictionary4)
    return_var.append(dictionary5)
    return jsonify(return_var)

@app.route("/nullspace", methods=['GET','POST'])
def nullspace():
    for word_embedding in wordEmbeddings:
        if word_embedding.name==request.json['name']:
            break
    female_words=request.json['female_words']
    female_words=female_words.replace(" ", "").split(",")
    aux=[]
    for word in female_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    female_words=aux
    if not female_words:
        return

    male_words=request.json['male_words']
    male_words=male_words.replace(" ", "").split(",")
    aux=[]
    for word in male_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    male_words=aux
    if not male_words:
        return

    neutral_words=request.json['neutral_words']
    neutral_words=neutral_words.replace(" ", "").split(",")
    aux=[]
    for word in neutral_words:
        if word in word_embedding.we.keys():
            aux.append(word)
    neutral_words=aux
    if not neutral_words:
        return

    iterations=int(request.json['iterations'])

    
    masc_words0, fem_words0, neutral_words0=visualization.reduction_embeddings_to_2d(word_embedding.we, male_words, female_words, neutral_words)

    debiased_embedding=debias.INLP(word_embedding.we, female_words, male_words, neutral_words, iterations)
    
    masc_words1, fem_words1, neutral_words1=visualization.reduction_embeddings_to_2d(debiased_embedding, male_words, female_words, neutral_words)

    return_var=[]
    dictionary0={'fem':{}, 'masc':{}, 'neutral':{}}
    dictionary1={'fem':{}, 'masc':{}, 'neutral':{}}
    
    for i, word in enumerate(female_words):
        dictionary0['fem'][i]={'label':word, 'x':fem_words0[i][0], 'y':fem_words0[i][1]}
        dictionary1['fem'][i]={'label':word, 'x':fem_words1[i][0], 'y':fem_words1[i][1]}
     
    for i, word in enumerate(male_words):
        dictionary0['masc'][i]={'label':word, 'x':masc_words0[i][0], 'y':masc_words0[i][1]}
        dictionary1['masc'][i]={'label':word, 'x':masc_words1[i][0], 'y':masc_words1[i][1]}
    
    for i, word in enumerate(neutral_words):
        dictionary0['neutral'][i]={'label':word, 'x':neutral_words0[i][0], 'y':neutral_words0[i][1]}
        dictionary1['neutral'][i]={'label':word, 'x':neutral_words1[i][0], 'y':neutral_words1[i][1]}


    word_embedding=word_embeddings.WordEmbeddings("", vector_size=len(next(iter(debiased_embedding.values()))))
    word_embedding.we=debiased_embedding
    name=request.json['name']+"_INLP_debiased"
    names=[]
    for we in wordEmbeddings:
        names.append(we.name)
    while(name in names):
        name = name+random.choice(string.ascii_letters)
    
    word_embedding.name=name
    wordEmbeddings.append(word_embedding)
    
    
    return_var.append({'name': word_embedding.name, 'vector_size': word_embedding.vector_size, 'num_words': len(word_embedding.we)})    
    return_var.append(dictionary0)
    return_var.append(dictionary1)
    return jsonify(return_var)   



@app.route("/indirect", methods=['GET','POST'])
def indirect():     
    if 'name_1' in request.json and 'name_2' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_1']:
                word_embedding1=word_embedding
            if word_embedding.name==request.json['name_2']:
                word_embedding2=word_embedding
                
                
                
        if request.json['gender_direction'] == 'pca':
            pairs=request.json['pairs']
            pairs=pairs.replace(" ", "").split(";")
            aux1=[]
            aux2=[]
            for pair in pairs:
                aux3=pair.split(',')
                if aux3[0] in word_embedding1.we.keys() and aux3[1] in word_embedding1.we.keys():
                    aux1.append([aux3[0], aux3[1]])
                if aux3[0] in word_embedding2.we.keys() and aux3[1] in word_embedding2.we.keys():
                    aux2.append([aux3[0], aux3[1]])
                    
            pairs1=aux1
            pairs2=aux2
            if not pairs1 and not pairs2:
                return
            
            gender_direction1=gender_direction_search.PCA_pairs(word_embedding1.we, pairs1)
            gender_direction2=gender_direction_search.PCA_pairs(word_embedding2.we, pairs2)
            
            indirect_bias1=measurements.indirect_bias(word_embedding1.we[request.json['w']], word_embedding1.we[request.json['v']], gender_direction1)
            indirect_bias2=measurements.indirect_bias(word_embedding2.we[request.json['w']], word_embedding2.we[request.json['v']], gender_direction2)
            
            
            return jsonify({'indirect_bias1': float(indirect_bias1), 'indirect_bias2': float(indirect_bias2)})
        
        
        elif request.json['gender_direction'] == 'two_means':
            female_words_direction=request.json['female_words_direction']
            female_words_direction=female_words_direction.replace(" ", "").split(",")
            male_words_direction=request.json['male_words_direction']
            male_words_direction=male_words_direction.replace(" ", "").split(",")
            
            aux_female1=[]
            aux_male1=[]
            aux_female2=[]
            aux_male2=[]
            for i, word in enumerate(female_words_direction):
                if female_words_direction[i] in word_embedding1.we.keys() and male_words_direction[i] in word_embedding1.we.keys():
                    aux_female1.append(female_words_direction[i])
                    aux_male1.append(male_words_direction[i])
                if female_words_direction[i] in word_embedding2.we.keys() and male_words_direction[i] in word_embedding2.we.keys():
                    aux_female2.append(female_words_direction[i])
                    aux_male2.append(male_words_direction[i])
                    
            female_words_direction1=aux_female1
            male_words_direction1=aux_male1
            female_words_direction2=aux_female2
            male_words_direction2=aux_male2
            if not female_words_direction1 and not male_words_direction1 and not male_words_direction2 and not female_words_direction2:
                return
            
            gender_direction1=gender_direction_search.two_means(word_embedding1.we, female_words_direction1, male_words_direction1)
            gender_direction2=gender_direction_search.two_means(word_embedding2.we, female_words_direction2, male_words_direction2)
            
            indirect_bias1=measurements.indirect_bias(word_embedding1.we[request.json['w']], word_embedding1.we[request.json['v']], gender_direction1)
            indirect_bias2=measurements.indirect_bias(word_embedding2.we[request.json['w']], word_embedding2.we[request.json['v']], gender_direction2)

            return jsonify({'indirect_bias1': float(indirect_bias1), 'indirect_bias2': float(indirect_bias2)})
            
    elif 'name_1' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_1']:
                word_embedding1=word_embedding
                break
            
        if request.json['gender_direction'] == 'pca':
            pairs=request.json['pairs']
            pairs=pairs.replace(" ", "").split(";")
            aux1=[]

            for pair in pairs:
                aux3=pair.split(',')
                if aux3[0] in word_embedding1.we.keys() and aux3[1] in word_embedding1.we.keys():
                    aux1.append([aux3[0], aux3[1]])
                    
            pairs1=aux1

            if not pairs1:
                return
            
            gender_direction1=gender_direction_search.PCA_pairs(word_embedding1.we, pairs1)

            
            indirect_bias1=measurements.indirect_bias(word_embedding1.we[request.json['w']], word_embedding1.we[request.json['v']], gender_direction1)
            
            
            return jsonify({'indirect_bias1': float(indirect_bias1)})
        
        
        elif request.json['gender_direction'] == 'two_means':
            female_words_direction=request.json['female_words_direction']
            female_words_direction=female_words_direction.replace(" ", "").split(",")
            male_words_direction=request.json['male_words_direction']
            male_words_direction=male_words_direction.replace(" ", "").split(",")
            
            aux_female1=[]
            aux_male1=[]
            for i, word in enumerate(female_words_direction):
                if female_words_direction[i] in word_embedding1.we.keys() and male_words_direction[i] in word_embedding1.we.keys():
                    aux_female1.append(female_words_direction[i])
                    aux_male1.append(male_words_direction[i])

                    
            female_words_direction1=aux_female1
            male_words_direction1=aux_male1

            if not female_words_direction1 and not male_words_direction1:
                return
            
            gender_direction1=gender_direction_search.two_means(word_embedding1.we, female_words_direction1, male_words_direction1)
      
            indirect_bias1=measurements.indirect_bias(word_embedding1.we[request.json['w']], word_embedding1.we[request.json['v']], gender_direction1)

            return {'indirect_bias1': float(indirect_bias1)}
                
    elif 'name_2' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_2']:
                word_embedding2=word_embedding
                break
       
        if request.json['gender_direction'] == 'pca':
            pairs=request.json['pairs']
            pairs=pairs.replace(" ", "").split(";")
            aux2=[]

            for pair in pairs:
                aux3=pair.split(',')
                if aux3[0] in word_embedding2.we.keys() and aux3[1] in word_embedding2.we.keys():
                    aux2.append([aux3[0], aux3[1]])
                    
            pairs2=aux2

            if not pairs2:
                return
            
            gender_direction2=gender_direction_search.PCA_pairs(word_embedding2.we, pairs2)

            
            indirect_bias2=measurements.indirect_bias(word_embedding2.we[request.json['w']], word_embedding2.we[request.json['v']], gender_direction2)
            
            
            return jsonify({'indirect_bias2': float(indirect_bias2)})
        
        
        elif request.json['gender_direction'] == 'two_means':
            female_words_direction=request.json['female_words_direction']
            female_words_direction=female_words_direction.replace(" ", "").split(",")
            male_words_direction=request.json['male_words_direction']
            male_words_direction=male_words_direction.replace(" ", "").split(",")
            
            aux_female2=[]
            aux_male2=[]
            for i, word in enumerate(female_words_direction):
                if female_words_direction[i] in word_embedding2.we.keys() and male_words_direction[i] in word_embedding2.we.keys():
                    aux_female2.append(female_words_direction[i])
                    aux_male2.append(male_words_direction[i])

                    
            female_words_direction2=aux_female2
            male_words_direction2=aux_male2

            if not female_words_direction2 and not male_words_direction2:
                return
            
            gender_direction2=gender_direction_search.two_means(word_embedding2.we, female_words_direction2, male_words_direction2)
      
            indirect_bias2=measurements.indirect_bias(word_embedding2.we[request.json['w']], word_embedding2.we[request.json['v']], gender_direction2)

            return jsonify({'indirect_bias2': float(indirect_bias2)})
        
        
        
    return 



@app.route("/direct", methods=['GET','POST'])
def direct():    
    if 'name_1' in request.json and 'name_2' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_1']:
                word_embedding1=word_embedding
            if word_embedding.name==request.json['name_2']:
                word_embedding2=word_embedding
            
        gender_neutral_words=request.json['gender_neutral_words']
        gender_neutral_words=gender_neutral_words.replace(" ", "").split(",")
        
        aux1=[]
        aux2=[]
        for word in gender_neutral_words:
            if word in word_embedding1.we.keys():
                aux1.append(word)
            if word in word_embedding2.we.keys():
                aux2.append(word)
        gender_neutral_words1=aux1
        gender_neutral_words2=aux2
        if not gender_neutral_words1 and not gender_neutral_words2:
            return
        
        c=request.json['c']
                
        if request.json['gender_direction'] == 'pca':
            pairs=request.json['pairs']
            pairs=pairs.replace(" ", "").split(";")
            aux1=[]
            aux2=[]
            for pair in pairs:
                aux3=pair.split(',')
                if aux3[0] in word_embedding1.we.keys() and aux3[1] in word_embedding1.we.keys():
                    aux1.append([aux3[0], aux3[1]])
                if aux3[0] in word_embedding2.we.keys() and aux3[1] in word_embedding2.we.keys():
                    aux2.append([aux3[0], aux3[1]])
                    
            pairs1=aux1
            pairs2=aux2
            if not pairs1 and not pairs2:
                return
            
            gender_direction1=gender_direction_search.PCA_pairs(word_embedding1.we, pairs1)
            gender_direction2=gender_direction_search.PCA_pairs(word_embedding2.we, pairs2)
            
            direct_bias1=measurements.direct_bias([word_embedding1.we[word] for word in gender_neutral_words1], gender_direction1, float(c))
            direct_bias2=measurements.direct_bias([word_embedding2.we[word] for word in gender_neutral_words2], gender_direction2, float(c))
            
            
            return jsonify({'direct_bias1': float(direct_bias1), 'direct_bias2': float(direct_bias2)})
        
        
        elif request.json['gender_direction'] == 'two_means':
            female_words_direction=request.json['female_words_direction']
            female_words_direction=female_words_direction.replace(" ", "").split(",")
            male_words_direction=request.json['male_words_direction']
            male_words_direction=male_words_direction.replace(" ", "").split(",")
            
            aux_female1=[]
            aux_male1=[]
            aux_female2=[]
            aux_male2=[]
            for i, word in enumerate(female_words_direction):
                if female_words_direction[i] in word_embedding1.we.keys() and male_words_direction[i] in word_embedding1.we.keys():
                    aux_female1.append(female_words_direction[i])
                    aux_male1.append(male_words_direction[i])
                if female_words_direction[i] in word_embedding2.we.keys() and male_words_direction[i] in word_embedding2.we.keys():
                    aux_female2.append(female_words_direction[i])
                    aux_male2.append(male_words_direction[i])
                    
            female_words_direction1=aux_female1
            male_words_direction1=aux_male1
            female_words_direction2=aux_female2
            male_words_direction2=aux_male2
            if not female_words_direction1 and not male_words_direction1 and not male_words_direction2 and not female_words_direction2:
                return
            
            gender_direction1=gender_direction_search.two_means(word_embedding1.we, female_words_direction1, male_words_direction1)
            gender_direction2=gender_direction_search.two_means(word_embedding2.we, female_words_direction2, male_words_direction2)
            
            direct_bias1=measurements.direct_bias([word_embedding1.we[word] for word in gender_neutral_words1], gender_direction1, float(c))
            direct_bias2=measurements.direct_bias([word_embedding2.we[word] for word in gender_neutral_words2], gender_direction2, float(c))

            return jsonify({'direct_bias1': float(direct_bias1), 'direct_bias2': float(direct_bias2)})
            
    elif 'name_1' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_1']:
                word_embedding1=word_embedding
                break
        
        gender_neutral_words=request.json['gender_neutral_words']
        gender_neutral_words=gender_neutral_words.replace(" ", "").split(",")
        
        aux1=[]

        for word in gender_neutral_words:
            if word in word_embedding1.we.keys():
                aux1.append(word)

        gender_neutral_words1=aux1

        if not gender_neutral_words1:
            return
        
        c=request.json['c']
        
        if request.json['gender_direction'] == 'pca':
            pairs=request.json['pairs']
            pairs=pairs.replace(" ", "").split(";")
            aux1=[]

            for pair in pairs:
                aux3=pair.split(',')
                if aux3[0] in word_embedding1.we.keys() and aux3[1] in word_embedding1.we.keys():
                    aux1.append([aux3[0], aux3[1]])
                    
            pairs1=aux1

            if not pairs1:
                return
            
            gender_direction1=gender_direction_search.PCA_pairs(word_embedding1.we, pairs1)
            direct_bias1=measurements.direct_bias([word_embedding1.we[word] for word in gender_neutral_words1], gender_direction1, float(c))
         
            return jsonify({'direct_bias1': float(direct_bias1)})

        
        
        elif request.json['gender_direction'] == 'two_means':
            female_words_direction=request.json['female_words_direction']
            female_words_direction=female_words_direction.replace(" ", "").split(",")
            male_words_direction=request.json['male_words_direction']
            male_words_direction=male_words_direction.replace(" ", "").split(",")
            
            aux_female1=[]
            aux_male1=[]
            for i, word in enumerate(female_words_direction):
                if female_words_direction[i] in word_embedding1.we.keys() and male_words_direction[i] in word_embedding1.we.keys():
                    aux_female1.append(female_words_direction[i])
                    aux_male1.append(male_words_direction[i])

                    
            female_words_direction1=aux_female1
            male_words_direction1=aux_male1

            if not female_words_direction1 and not male_words_direction1:
                return
            
            gender_direction1=gender_direction_search.two_means(word_embedding1.we, female_words_direction1, male_words_direction1)
            direct_bias1=measurements.direct_bias([word_embedding1.we[word] for word in gender_neutral_words1], gender_direction1, float(c))
            
            return jsonify({'direct_bias1': float(direct_bias1)})

                
    elif 'name_2' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_2']:
                word_embedding2=word_embedding
                break
       
        gender_neutral_words=request.json['gender_neutral_words']
        gender_neutral_words=gender_neutral_words.replace(" ", "").split(",")
        

        aux2=[]
        for word in gender_neutral_words:
            if word in word_embedding2.we.keys():
                aux2.append(word)

        gender_neutral_words2=aux2
        if not gender_neutral_words2:
            return
        
        c=request.json['c']
       
        
        if request.json['gender_direction'] == 'pca':
            pairs=request.json['pairs']
            pairs=pairs.replace(" ", "").split(";")
            aux2=[]

            for pair in pairs:
                aux3=pair.split(',')
                if aux3[0] in word_embedding2.we.keys() and aux3[1] in word_embedding2.we.keys():
                    aux2.append([aux3[0], aux3[1]])
                    
            pairs2=aux2

            if not pairs2:
                return
            
            gender_direction2=gender_direction_search.PCA_pairs(word_embedding2.we, pairs2)
            direct_bias2=measurements.direct_bias([word_embedding2.we[word] for word in gender_neutral_words2], gender_direction2, float(c))
               
            return jsonify({'direct_bias2': float(direct_bias2)})
      
        
        elif request.json['gender_direction'] == 'two_means':
            female_words_direction=request.json['female_words_direction']
            female_words_direction=female_words_direction.replace(" ", "").split(",")
            male_words_direction=request.json['male_words_direction']
            male_words_direction=male_words_direction.replace(" ", "").split(",")
            
            aux_female2=[]
            aux_male2=[]
            for i, word in enumerate(female_words_direction):
                if female_words_direction[i] in word_embedding2.we.keys() and male_words_direction[i] in word_embedding2.we.keys():
                    aux_female2.append(female_words_direction[i])
                    aux_male2.append(male_words_direction[i])

                    
            female_words_direction2=aux_female2
            male_words_direction2=aux_male2

            if not female_words_direction2 and not male_words_direction2:
                return
            
            gender_direction2=gender_direction_search.two_means(word_embedding2.we, female_words_direction2, male_words_direction2)
            direct_bias2=measurements.direct_bias([word_embedding2.we[word] for word in gender_neutral_words2], gender_direction2, float(c))
                      
            return jsonify({'direct_bias2': float(direct_bias2)})
               
    return 



@app.route("/weat", methods=['GET','POST'])
def weat():
    if 'name_1' in request.json and 'name_2' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_1']:
                word_embedding1=word_embedding
            if word_embedding.name==request.json['name_2']:
                word_embedding2=word_embedding
            
        tarjet_words_x=request.json['tarjet_words_x']
        tarjet_words_x=tarjet_words_x.replace(" ", "").split(",")
        
        aux1=[]
        aux2=[]
        for word in tarjet_words_x:
            if word in word_embedding1.we.keys():
                aux1.append(word)
            if word in word_embedding2.we.keys():
                aux2.append(word)
        tarjet_words_x1=aux1
        tarjet_words_x2=aux2
        if not tarjet_words_x1 and not tarjet_words_x2:
            return
        
        
        
        tarjet_words_y=request.json['tarjet_words_y']
        tarjet_words_y=tarjet_words_y.replace(" ", "").split(",")
        
        aux1=[]
        aux2=[]
        for word in tarjet_words_y:
            if word in word_embedding1.we.keys():
                aux1.append(word)
            if word in word_embedding2.we.keys():
                aux2.append(word)
        tarjet_words_y1=aux1
        tarjet_words_y2=aux2
        if not tarjet_words_y1 and not tarjet_words_y2:
            return
        
        
        attr_words_a=request.json['attr_words_a']
        attr_words_a=attr_words_a.replace(" ", "").split(",")
        
        aux1=[]
        aux2=[]
        for word in attr_words_a:
            if word in word_embedding1.we.keys():
                aux1.append(word)
            if word in word_embedding2.we.keys():
                aux2.append(word)
        attr_words_a1=aux1
        attr_words_a2=aux2
        if not attr_words_a1 and not attr_words_a2:
            return
        
        
        
        attr_words_b=request.json['attr_words_b']
        attr_words_b=attr_words_b.replace(" ", "").split(",")
        
        aux1=[]
        aux2=[]
        for word in attr_words_b:
            if word in word_embedding1.we.keys():
                aux1.append(word)
            if word in word_embedding2.we.keys():
                aux2.append(word)
        attr_words_b1=aux1
        attr_words_b2=aux2
        if not attr_words_b1 and not attr_words_b2:
            return
        
       
        weat1, effect_size1, p_value1=measurements.WEAT([word_embedding1.we[word] for word in tarjet_words_x1], [word_embedding1.we[word] for word in tarjet_words_y1], [word_embedding1.we[word] for word in attr_words_a1], [word_embedding1.we[word] for word in attr_words_b1])
        weat2, effect_size2, p_value2=measurements.WEAT([word_embedding2.we[word] for word in tarjet_words_x2], [word_embedding2.we[word] for word in tarjet_words_y2], [word_embedding2.we[word] for word in attr_words_a2], [word_embedding2.we[word] for word in attr_words_b2])
        
        
        return jsonify({'weat1': float(weat1), 'effect_size1': float(effect_size1), 'p_value1':float(p_value1), 'weat2': float(weat2), 'effect_size2': float(effect_size2), 'p_value2':float(p_value2)})
      
    elif 'name_1' in request.json:    
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_1']:
                word_embedding1=word_embedding

                
        tarjet_words_x=request.json['tarjet_words_x']
        tarjet_words_x=tarjet_words_x.replace(" ", "").split(",")
        
        aux1=[]

        for word in tarjet_words_x:
            if word in word_embedding1.we.keys():
                aux1.append(word)

        tarjet_words_x1=aux1

        if not tarjet_words_x1:
            return
        
        
        
        tarjet_words_y=request.json['tarjet_words_y']
        tarjet_words_y=tarjet_words_y.replace(" ", "").split(",")
        
        aux1=[]

        for word in tarjet_words_y:
            if word in word_embedding1.we.keys():
                aux1.append(word)

        tarjet_words_y1=aux1

        if not tarjet_words_y1:
            return
        
        
        attr_words_a=request.json['attr_words_a']
        attr_words_a=attr_words_a.replace(" ", "").split(",")
        
        aux1=[]

        for word in attr_words_a:
            if word in word_embedding1.we.keys():
                aux1.append(word)

        attr_words_a1=aux1

        if not attr_words_a1:
            return
        
        
        
        attr_words_b=request.json['attr_words_b']
        attr_words_b=attr_words_b.replace(" ", "").split(",")
        
        aux1=[]

        for word in attr_words_b:
            if word in word_embedding1.we.keys():
                aux1.append(word)

        attr_words_b1=aux1

        if not attr_words_b1:
            return
        
       
        weat1, effect_size1, p_value1=measurements.WEAT([word_embedding1.we[word] for word in tarjet_words_x1], [word_embedding1.we[word] for word in tarjet_words_y1], [word_embedding1.we[word] for word in attr_words_a1], [word_embedding1.we[word] for word in attr_words_b1])
       
        
        return jsonify({'weat1': float(weat1), 'effect_size1': float(effect_size1), 'p_value1':float(p_value1)})

    elif 'name_2' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_2']:
                word_embedding2=word_embedding

                
        tarjet_words_x=request.json['tarjet_words_x']
        tarjet_words_x=tarjet_words_x.replace(" ", "").split(",")
        
        aux2=[]

        for word in tarjet_words_x:
            if word in word_embedding2.we.keys():
                aux2.append(word)

        tarjet_words_x2=aux2

        if not tarjet_words_x2:
            return
        
        
        
        tarjet_words_y=request.json['tarjet_words_y']
        tarjet_words_y=tarjet_words_y.replace(" ", "").split(",")
        
        aux2=[]

        for word in tarjet_words_y:
            if word in word_embedding2.we.keys():
                aux2.append(word)

        tarjet_words_y2=aux2

        if not tarjet_words_y2:
            return
        
        
        attr_words_a=request.json['attr_words_a']
        attr_words_a=attr_words_a.replace(" ", "").split(",")
        
        aux2=[]

        for word in attr_words_a:
            if word in word_embedding2.we.keys():
                aux2.append(word)

        attr_words_a2=aux2

        if not attr_words_a2:
            return
        
        
        
        attr_words_b=request.json['attr_words_b']
        attr_words_b=attr_words_b.replace(" ", "").split(",")
        
        aux2=[]

        for word in attr_words_b:
            if word in word_embedding2.we.keys():
                aux2.append(word)

        attr_words_b2=aux2

        if not attr_words_b2:
            return
        
       
        weat2, effect_size2, p_value2=measurements.WEAT([word_embedding2.we[word] for word in tarjet_words_x2], [word_embedding2.we[word] for word in tarjet_words_y2], [word_embedding2.we[word] for word in attr_words_a2], [word_embedding2.we[word] for word in attr_words_b2])
       
        
        return jsonify({'weat2': float(weat2), 'effect_size2': float(effect_size2), 'p_value2':float(p_value2)})
    
    
    return


@app.route("/neighborhood", methods=['GET','POST'])
def neighborhood():
    print(request.json)
    if 'name_1' in request.json and 'name_2' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_1']:
                word_embedding1=word_embedding
            if word_embedding.name==request.json['name_2']:
                word_embedding2=word_embedding
            
        female_words=request.json['female_words']
        female_words=female_words.replace(" ", "").split(",")
        
        aux1=[]
        aux2=[]
        for word in female_words:
            if word in word_embedding1.we.keys():
                aux1.append(word)
            if word in word_embedding2.we.keys():
                aux2.append(word)
        female_words1=aux1
        female_words2=aux2
        if not female_words1 and not female_words2:
            return
        
        
        
        male_words=request.json['male_words']
        male_words=male_words.replace(" ", "").split(",")
        
        aux1=[]
        aux2=[]
        for word in male_words:
            if word in word_embedding1.we.keys():
                aux1.append(word)
            if word in word_embedding2.we.keys():
                aux2.append(word)
        male_words1=aux1
        male_words2=aux2
        if not male_words1 and not male_words2:
            return
        
        X1=[]
        Y1=[]
        for word in female_words1:
            X1.append(word_embedding1.we[word])
            Y1.append(0)
            
        for word in male_words1:
            X1.append(word_embedding1.we[word])
            Y1.append(1)
       
        neighborhood_metric1=measurements.neighborhood_metric(X1, Y1)
        
        X2=[]
        Y2=[]
        for word in female_words2:
            X2.append(word_embedding2.we[word])
            Y2.append(0)
            
        for word in male_words2:
            X2.append(word_embedding2.we[word])
            Y2.append(1)
       
        neighborhood_metric2=measurements.neighborhood_metric(X2, Y2)
             
        
        return jsonify({'neighborhood_metric1': float(neighborhood_metric1), 'neighborhood_metric2': float(neighborhood_metric2)})
      
    elif 'name_1' in request.json:    
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_1']:
                word_embedding1=word_embedding

        
        female_words=request.json['female_words']
        female_words=female_words.replace(" ", "").split(",")
        
        aux1=[]

        for word in female_words:
            if word in word_embedding1.we.keys():
                aux1.append(word)

        female_words1=aux1

        if not female_words1:
            return
        
        
        
        male_words=request.json['male_words']
        male_words=male_words.replace(" ", "").split(",")
        
        aux1=[]

        for word in male_words:
            if word in word_embedding1.we.keys():
                aux1.append(word)

        male_words1=aux1

        if not male_words1:
            return
        
        X=[]
        Y=[]
        for word in female_words1:
            X.append(word_embedding1.we[word])
            Y.append(0)
            
        for word in male_words1:
            X.append(word_embedding1.we[word])
            Y.append(1)
       
        neighborhood_metric1=measurements.neighborhood_metric(X, Y)
        
        
        return jsonify({'neighborhood_metric1': float(neighborhood_metric1)})

    elif 'name_2' in request.json:
        for word_embedding in wordEmbeddings:
            if word_embedding.name==request.json['name_2']:
                word_embedding2=word_embedding

                
        female_words=request.json['female_words']
        female_words=female_words.replace(" ", "").split(",")
        
        aux2=[]

        for word in female_words:
            if word in word_embedding2.we.keys():
                aux2.append(word)

        female_words2=aux2

        if not female_words2:
            return
        
        
        
        male_words=request.json['male_words']
        male_words=male_words.replace(" ", "").split(",")
        
        aux2=[]

        for word in male_words:
            if word in word_embedding2.we.keys():
                aux2.append(word)

        male_words2=aux2

        if not male_words2:
            return
        
       
        X=[]
        Y=[]
        for word in female_words2:
            X.append(word_embedding2.we[word])
            Y.append(0)
            
        for word in male_words2:
            X.append(word_embedding2.we[word])
            Y.append(1)
       
        neighborhood_metric2=measurements.neighborhood_metric(X, Y)    
        
        return jsonify({'neighborhood_metric2': float(neighborhood_metric2)})



    
if __name__ == "__main__":   
    app.run()