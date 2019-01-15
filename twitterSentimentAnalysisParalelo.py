# -*- coding: utf-8 -*

import os
import time
import sentimentAnalysis_util as util
import threading

if(os.name == 'posix'):
    import multiprocessing as mp
else:
    import multiprocess as mp

import re 
import tweepy 
from tweepy import OAuthHandler 

#################################################
control = "T" # T thread , P processo, N normal
str_query = 'Donald Trump'
qt_tweets = 200 
n_multi = 1 #{1,2,4,5,10}
#################################################
qt_multi = qt_tweets / n_multi

if(control == 'T'):
    var_lock = threading.Lock()

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

    def get_tweetsNormal(self, query, qt_tweets):
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
                    parsed_tweet['sentiment'] = util.sentimentalAnalysis(self.clean_tweet(tweet.text)) 

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
            
    #Com lock: uma mesma lista para todas as threads, cada thread irá armazenar em uma lista temporária e ao final
    #adquire o lock para jogar na lista principal de uma só vez
    def get_tweetsThread2(self, query, qt_tweets, tweets):
        global var_lock
        ''' 
		Main function to fetch tweets and parse them. 
		'''
		# empty list to store parsed tweets
        tweetsTemp = []
        last_id = -1
        try:
            while len(tweetsTemp) < qt_tweets:
                count = (qt_tweets - len(tweetsTemp)) if (qt_tweets - len(tweetsTemp)) < 100 else 100
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
                    parsed_tweet['sentiment'] = util.sentimentalAnalysis(self.clean_tweet(tweet.text)) 

					# appending parsed tweet to tweets list
                    if tweet.retweet_count > 0: 
                        # if tweet has retweets, ensure that it is appended only once
                        if parsed_tweet not in tweetsTemp:
                            tweetsTemp.append(parsed_tweet) 

                    else:
                        tweetsTemp.append(parsed_tweet) 

            var_lock.acquire()
            tweets.extend(tweetsTemp)
            var_lock.release()

        except tweepy.TweepError as e: 
			# print error (if any)
            print("Error : " + str(e)) 

    # Sem lock, cada thread tem sua própria lista
    def get_tweetsThread3(self, query, qt_tweets, tweetsTemp):
        ''' 
		Main function to fetch tweets and parse them. 
		'''
        last_id = -1
        try:
            while len(tweetsTemp) < qt_tweets:
                count = (qt_tweets - len(tweetsTemp)) if (qt_tweets - len(tweetsTemp)) < 100 else 100
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
                    parsed_tweet['sentiment'] = util.sentimentalAnalysis(self.clean_tweet(tweet.text)) 

					# appending parsed tweet to tweets list
                    if tweet.retweet_count > 0: 
                        # if tweet has retweets, ensure that it is appended only once
                        if parsed_tweet not in tweetsTemp:
                            tweetsTemp.append(parsed_tweet) 
                    else:
                        tweetsTemp.append(parsed_tweet) 

        except tweepy.TweepError as e: 
			# print error (if any)
            print("Error : " + str(e)) 

    # Utiliza FIFO com sincronização (Queue), todos os processos inserem na mesma fila
    # ao fim das execuções dos processos a FIFO é transformada em uma lista
    def get_tweetsProcess(self, query, qt_tweets, queue, last_id):
        ''' 
		Main function to fetch tweets and parse them. 
		'''
        tweetsTemp = []
        try:
            while len(tweetsTemp) < qt_tweets:
                count = (qt_tweets - len(tweetsTemp)) if (qt_tweets - len(tweetsTemp)) < 100 else 100
                # call twitter api to fetch tweets
                id = last_id.get()-1
                fetched_tweets = self.api.search(q=query, count=count, max_id=str(id))
                
                if not fetched_tweets:
                    last_id.put(id)
                    break
                last_id.put(fetched_tweets[-1].id)

                # parsing tweets one by one
                for tweet in fetched_tweets: 
					# empty dictionary to store required params of a tweet
                    parsed_tweet = {} 

					# saving text of tweet
                    parsed_tweet['text'] = tweet.text 
					# saving sentiment of tweet
                    parsed_tweet['sentiment'] = util.sentimentalAnalysis(self.clean_tweet(tweet.text)) 

					# appending parsed tweet to tweets list
                    if tweet.retweet_count > 0: 
                        # if tweet has retweets, ensure that it is appended only once
                        if parsed_tweet not in tweetsTemp:
                            tweetsTemp.append(parsed_tweet)
                            queue.put(parsed_tweet)
                    else:
                        tweetsTemp.append(parsed_tweet)
                        queue.put(parsed_tweet)
                    
        except tweepy.TweepError as e: 
			# print error (if any)
            print("Error : " + str(e)) 

def main(): 
    # creating object of TwitterClient Class 
    api = TwitterClient()
    tweets = []

    util.load_classifier()
    
    if( control == 'N'):
        print("Execução Normal")
        start = time.time()
        tweets = api.get_tweetsNormal(str_query, qt_tweets) 
    else:
        multi = []
    
        if control == 'T':
            print("Execução utilizando Threads")

            ''' Usar apenas se for usar o get_tweetsThread3 '''
            #retornos = [[] for i in range(n_multi)]

            start = time.time()
            for i in range(0,n_multi):
                ''' Com lock: uma mesma lista para todas as threads, cada thread irá armazenar em uma lista temporária
                        e ao final adquire o lock para jogar na lista principal '''
                multi.append(threading.Thread(target=api.get_tweetsThread2, args = (str_query, qt_multi, tweets)))

                ''' Sem lock, cada thread tem sua própria lista...e ao final todas as listas são transformadas em uma
                        grande lista através do sum(retornos,[]) 
                        Descomentar: linha 300 e 332 que usam o array retornos'''
                #multi.append(threading.Thread(target=api.get_tweetsThread3, args = (str_query, qt_multi, retornos[i])))

                multi[-1].start()
        
        else:
            print("Execução utilizando Processos")
            m = mp.Manager()
            queue = m.Queue()
            last_id = m.Queue()
            last_id.put(-1)
            start = time.time()
            for i in range(0,n_multi):
                ''' Utiliza FIFO com sincronização (Queue), todos os processos inserem na mesma fila ao fim
                        das execuções dos processos a FIFO é transformada em uma lista '''
                multi.append(mp.Process(target=api.get_tweetsProcess, args = (str_query, qt_multi, queue, last_id)))
                multi[-1].start()
        
        for m in multi:
            m.join()

        ''' Usar apenas se for usar o get_tweetsThread3 '''
        #tweets = sum(retornos,[])

    ''' Comentar o if se for analisar tempo  '''
    if(control == 'P'):
        while queue.qsize() != 0:
            tweets.append(queue.get())

    end = time.time()
    print("#######")
    print("A aplicação demorou {} segundos para executar e analisar {} tweets".format(end - start, len(tweets)))
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
    print("Executando para {} tweets.".format(qt_tweets))
    main()
