# -*- coding: utf-8 -*

import os
import time
from nltk.corpus import stopwords
import nltk

import pickle
import numpy as np

from sklearn import model_selection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif
from sklearn.naive_bayes import GaussianNB

from sklearn.feature_extraction.text import CountVectorizer

features_trainG = None
labels_trainG = None
analiser = None
stopWordss = ["a","able","about","across","after","all","almost","also","am","among","an","and","any","are","as","at","be","because","been","but","by","can","cannot","could","dear","did","do","does","either","else","ever","every","for","from","get","got","had","has","have","he","her","hers","him","his","how","however","i","if","in","into","is","it","its","just","least","let","like","likely","may","me","might","most","must","my","neither","no","nor","not","of","off","often","on","only","or","other","our","own","rather","said","say","says","she","should","since","so","some","than","that","the","their","them","then","there","these","they","this","tis","to","too","twas","us","wants","was","we","were","what","when","where","which","while","who","whom","why","will","with","would","yet","you","your","ain't","aren't","can't","could've","couldn't","didn't","doesn't","don't","hasn't","he'd","he'll","he's","how'd","how'll","how's","i'd","i'll","i'm","i've","isn't","it's","might've","mightn't","must've","mustn't","shan't","she'd","she'll","she's","should've","shouldn't","that'll","that's","there's","they'd","they'll","they're","they've","wasn't","we'd","we'll","we're","weren't","what'd","what's","when'd","when'll","when's","where'd","where'll","where's","who'd","who'll","who's","why'd","why'll","why's","won't","would've","wouldn't","you'd","you'll","you're","you've"]

def isStopWord(word):
    if word.lower() in stopWordss:
        return True
    else:
        return False

def cleanTweet (tweet):
    return list(filter(lambda word: not isStopWord(word), tweet))

def cleanTweet2 (tweet):
    return ' '.join([word for word in tweet.split() if word.lower() not in stopWordss])

def cleanTweet3 (tweet, conj):
    return ' '.join([word for word in tweet.split() if word.lower() not in conj])

# Recebe o tweet no forma array de str depois de pre processado
def sentimentalAnalysis(tweet):
    global analiser, features_trainG

    vectorizer = TfidfVectorizer()
    features_train_transformed = vectorizer.fit_transform(features_trainG)
    features_test_transformed  = vectorizer.transform([tweet])
		
    selector = SelectPercentile(f_classif, percentile=1)
    selector.fit(features_train_transformed, labels_trainG)
    x  = selector.transform(features_test_transformed).toarray()
	
    labels_predict = analiser.predict(x)
    labels_analysis = ['positive' if item == 1 else 'negative' for item in labels_predict] 
		
    return labels_analysis[0] 

def prepareTrainData():
	global features_trainG, labels_trainG
	words_filePos = 'train/positiveText'
	with open(words_filePos, "r", encoding="utf8") as f:
		contentP = f.readlines()
	contentP = [x.strip() for x in contentP]	
	
	words_fileNeg = 'train/negativeText'
	with open(words_fileNeg, "r", encoding="utf8") as f:
		contentN = f.readlines()
	contentN = [x.strip() for x in contentN]
	
	total = 4000
						   
	features_train = contentP[:total] + contentN[:total]
	labels_train = [1 if i < total else -1 for i in range(total*2)]
	
	features_trainG, labels_trainG = features_train, labels_train

	vectorizer = TfidfVectorizer()
	features_train_transformed = vectorizer.fit_transform(features_train)
	selector = SelectPercentile(f_classif, percentile=1)
	selector.fit(features_train_transformed, labels_train)
	features_train_transformed = selector.transform(features_train_transformed).toarray()
	
	classifier = GaussianNB()
	
	classifier.fit(features_train_transformed, labels_train)
	
	with open('classifier.pkl', 'wb') as file:
		pickle.dump(classifier, file)   
	with open('classifier_var.pkl', 'wb') as file:
		pickle.dump([features_trainG, labels_trainG], file)   

	return classifier

def load_classifier():
    global analiser, features_trainG, labels_trainG
    if (not os.path.isfile("classifier.pkl") ):
        print("Treinando...")
        analiser = prepareTrainData()
    else:
        with open('classifier.pkl', 'rb') as file:
            print("Carregando classificador...")
            analiser = pickle.load(file)
            features_trainG, labels_trainG = pickle.load(open('classifier_var.pkl', 'rb'))