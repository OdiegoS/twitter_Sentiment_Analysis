# -*- coding: utf-8 -*

import os
import time
import sentimentAnalysis_util as util

import re 
import tweepy 
from tweepy import OAuthHandler 

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
		temp = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 
		return util.cleanTweet2(temp)

	def get_tweets(self, query, qt_tweets = 10): 
		''' 
		Main function to fetch tweets and parse them. 
		'''
		# empty list to store parsed tweets 
		tweets = [] 
		last_id = -1
		try:
			while len(tweets) < qt_tweets:
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
					parsed_tweet['sentiment'] = util.sentimentalAnalysis(self.clean_tweet(tweet.text)) #funcao recebe um array de string com os tweets, por enquanto só tá recebendo 1, mas pode ser mais de um por vez

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

def main(): 
	global qt_tweets

	util.load_classifier()

	# creating object of TwitterClient Class 
	api = TwitterClient() 
	print("Iniciando...")
	start = time.time()
	# calling function to get tweets 
	tweets = api.get_tweets(query = str_query, qt_tweets = qt_tweets) 
	end = time.time()
	print("#######")
	print("A aplicação demorou {} segundos para tratar {} tweets".format(end - start, qt_tweets))
	print("#######")

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
	'''
	# printing first 5 positive tweets 
	print("\n\nPositive tweets:") 
	for tweet in ptweets[:10]: 
		print(tweet['text']) 

	# printing first 5 negative tweets 
	print("\n\nNegative tweets:") 
	for tweet in ntweets[:10]: 
		print(tweet['text']) 
	'''

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
    main()
