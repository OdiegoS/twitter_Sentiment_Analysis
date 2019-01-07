# -*- coding: utf-8 -*

import os
import time
import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 

import pickle
import numpy as np

from sklearn import cross_validation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif
from sklearn.naive_bayes import GaussianNB

from sklearn.feature_extraction.text import CountVectorizer

global features_trainG, labels_trainG, analiser

str_query = 'Donald Trump'
qt_tweets = 10
# keys and tokens from the Twitter Dev Console
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

class TwitterClient(object): 
	''' 
	Generic Twitter Class for sentiment analysis. 
	'''
	def __init__(self): 
		global consumer_key, consumer_secret, access_token, access_token_secret
		''' 
		Class constructor or initialization method. 
		'''
		# attempt authentication 
		try: 
			# create OAuthHandler object 
			self.auth = OAuthHandler(consumer_key, consumer_secret) 
			# set access token and secret 
			self.auth.set_access_token(access_token, access_token_secret) 
			# create tweepy API object to fetch tweets 
			self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True) 
		except: 
			print("Error: Authentication Failed") 

	def clean_tweet(self, tweet): 
		''' 
		Utility function to clean tweet text by removing links, special characters 
		using simple regex statements. 
		'''
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 

	def get_tweets(self, query, qt_tweets = 10): 
		''' 
		Main function to fetch tweets and parse them. 
		'''
		# empty list to store parsed tweets 
		tweets = [] 
		last_id = -1
		try:
			while len(tweets) <= qt_tweets:
				count = (qt_tweets - len(tweets)) if (qt_tweets - len(tweets)) < 100 else 100
				# call twitter api to fetch tweets 
				fetched_tweets = self.api.search(q=query, count=count, max_id=str(last_id - 1))
				
				if not fetched_tweets:
					break
				last_id = fetched_tweets[-1].id

				# parsing tweets one by one 
				for tweet in fetched_tweets: 
					# empty dictionary to store required params of a tweet 
					parsed_tweet = {} 

					# saving text of tweet 
					parsed_tweet['text'] = tweet.text 
					# saving sentiment of tweet 
					#parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 
					textT = tirarStopWords(tweet.text)
					parsed_tweet['sentiment'] = sentimentalAnalysis([textT]) #funcao recebe um array de string com os tweets, por enquanto só tá recebendo 1, mas pode ser mais de um por vez

					# appending parsed tweet to tweets list 
					if tweet.retweet_count > 0: 
						# if tweet has retweets, ensure that it is appended only once 
						if parsed_tweet not in tweets: 
							tweets.append(parsed_tweet) 
					else: 
						tweets.append(parsed_tweet) 

			# return parsed tweets 
			return tweets 

		except tweepy.TweepError as e: 
			# print error (if any) 
			print("Error : " + str(e)) 



# função que tira as stopwords do texto e retorna o texto

def tirarStopWords(tweet):
	#Separar texto em palavras e tirar os q estão no arquivo de stopword
	return tweet


def prepareTrainData():
	global features_trainG, labels_trainG
	words_filePos = 'train/positiveText'
	with open(words_filePos, "r") as f:
		contentP = f.readlines()
	contentP = [x.strip() for x in contentP]	
	
	words_fileNeg = 'train/negativeText'
	with open(words_fileNeg, "r") as f:
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
	
	return classifier

# Recebe o tweet no forma array de str depois de pre processado
def sentimentalAnalysis(tweet):
	global analiser
	vectorizer = TfidfVectorizer()
	features_train_transformed = vectorizer.fit_transform(features_trainG)
	features_test_transformed  = vectorizer.transform(tweet)
	
	selector = SelectPercentile(f_classif, percentile=1)
	selector.fit(features_train_transformed, labels_trainG)
	x  = selector.transform(features_test_transformed).toarray()
	
	labels_predict = analiser.predict(x)
	
	labels_analysis = ['positive' if item == 1 else 'negative' for item in labels_predict] 
	
	#retornando a analise de um tweet
	return labels_analysis[0] 

def main(): 
	
	#Treinando dataset
	global analiser
	analiser = prepareTrainData()
	
	# creating object of TwitterClient Class 
	api = TwitterClient() 
	
	# calling function to get tweets 
	tweets = api.get_tweets(query = str_query, qt_tweets = qt_tweets) 

	# picking positive tweets from tweets 
	ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
	# percentage of positive tweets 
	print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
	# picking negative tweets from tweets 
	ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
	# percentage of negative tweets 
	print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
	# percentage of neutral tweets 
	print("Neutral tweets percentage: {} % ".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets))) 

	# printing first 5 positive tweets 
	print("\n\nPositive tweets:") 
	for tweet in ptweets[:10]: 
		print(tweet['text']) 

	# printing first 5 negative tweets 
	print("\n\nNegative tweets:") 
	for tweet in ntweets[:10]: 
		print(tweet['text']) 

def get_keys():
	global consumer_key, consumer_secret, access_token, access_token_secret

	current_directory = os.path.dirname(os.path.realpath(__file__))
	keys_file = open(current_directory + "/TwitterApi_Key.txt",'r')
	linhas_file = keys_file.read().splitlines()
	
	consumer_key = linhas_file[0]
	consumer_secret = linhas_file[1]
	access_token = linhas_file[2]
	access_token_secret = linhas_file[3]

if __name__ == "__main__": 
	# calling main function
    get_keys()
    start = time.time()
    main() 
    end = time.time()
    print("#######")
    print("A aplicação demorou {} segundos para tratar {} tweets".format(end - start, qt_tweets))
    print("#######")
