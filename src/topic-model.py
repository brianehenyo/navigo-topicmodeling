import pandas as pd
import numpy as np
import gensim
import string
import json
import os.path
import re
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim import corpora, models
from gensim.test.utils import datapath
import nltk
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *

np.random.seed(2018)

nltk.download('wordnet')
stemmer = SnowballStemmer('english')

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result

def removeURLFromText(text):
    result = re.sub(r"http\S+", "", text)
    result = result.strip()
    return result

def prepareTFIDF(fileURL):
    json_file = open(fileURL)
    json_data = json.load(json_file)
    documents = pd.DataFrame(json_data)

    processed_docs = documents['body'].map(removeURLFromText)
    processed_docs = processed_docs.map(preprocess)

    dictionary = gensim.corpora.Dictionary(processed_docs)

    dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)

    bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

    # TF-IDF
    tfidf = models.TfidfModel(bow_corpus)
    corpus_tfidf = tfidf[bow_corpus]
    return corpus_tfidf, dictionary, bow_corpus

def saveModel(lda_model_tfidf, community):
    path = '../output/topics_tf-idf_' + str(community) + '.csv'
    out = open(path, 'w+')
    out.write("topic,word\n")
    for idx, topic in lda_model_tfidf.print_topics(-1):
        out.write(str(idx) + "," + topic + "\n")
    out.close()

    # # Save model to disk.
    # modelFileName = "../model/tm_tf-idf_" + str(community)
    # temp_file = datapath(modelFileName)
    # lda_model_tfidf.save(temp_file)

def trainIndieModel(community):
    fileURL = "../raw/raw_textonly_" + str(community) + ".json"
    corpus_tfidf, dictionary, bow_corpus = prepareTFIDF(fileURL)

    # Train LDA using TF-IDF
    lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=10, id2word=dictionary, passes=2, workers=4)

    saveModel(lda_model_tfidf, community)

    scoreData(community, lda_model_tfidf, bow_corpus)

def scoreData(community, lda_model_tfidf, bow_corpus):
    path = '../output/scores_tf-idf_' + str(community) + '.csv'
    out = open(path, 'w+')
    out.write("doc_id,topic_index,score\n")

    for i in range(len(bow_corpus)):
        for index, score in sorted(lda_model_tfidf[bow_corpus[i]], key=lambda tup: -1*tup[1]):
            out.write(str(i) + "," + str(index) + "," + str(score) + "\n")
            break
    
    out.close()

# def trainAllModel():
#     corpus_tfidf_waze, dictionary_waze = prepareTFIDF("../raw/raw_textonly_waze.json")
#     corpus_tfidf_apple, dictionary_apple = prepareTFIDF("../raw/raw_textonly_applemaps.json")
#     corpus_tfidf_google, dictionary_google = prepareTFIDF("../raw/raw_textonly_GoogleMaps.json")

#     # Train LDA using TF-IDF
#     lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf_waze, num_topics=10, id2word=dictionary, passes=2, workers=4)
#     lda_model_tfidf.update(corpus_tfidf_apple)
#     lda_model_tfidf.update(corpus_tfidf_google)

#     saveModel(lda_model_tfidf, "all")

trainIndieModel("waze")

# for index, score in sorted(lda_model_tfidf[bow_corpus[432]], key=lambda tup: -1*tup[1]):
#     print("\nScore: {}\t \nTopic: {}".format(score, lda_model_tfidf.print_topic(index, 10)))