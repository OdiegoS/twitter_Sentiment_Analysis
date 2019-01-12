# -*- coding: utf-8 -*

import os
import time
from nltk.corpus import stopwords
import nltk

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

'''
if __name__ == "__main__": 
    nltk.download('stopwords')
    conj = stopwords.words('english')
'''
    
    