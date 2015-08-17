import pandas as pd
import numpy as np
import json
import random
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import string
import datetime
import json
import psycopg2
import random
from collections import defaultdict


#RETRIEVE DATA
def get_swl_data(table = "tweeted_neighb_wk2"):
	'''
	INPUT: postgress table containing tweet information: timestamp, id, geoid
	OUTPUT: A dataframe of retrieved twitter information: timestamp_ms, text, geoid10
	'''
	conn_dict = {'dbname':'zipfiantwitter', 'user':'clwilloughby', 'password': '', 'host':'/tmp'}
	conn = psycopg2.connect(dbname=conn_dict['dbname'], user=conn_dict['user'], host='/tmp')
	cur = conn.cursor()

	map_query = """
	SELECT timestamp_ms, text, geoid10
	FROM table
	                ;"""

	df = pd.read_sql(map_query, conn)
	return df 

#TOKENIZE THE TEXT FOR LATER
def tokenize_tweets(text):
    '''Called by sql_tweets_sum_and_tokenized. Tokenizes a sting.
    INPUT: a string of tweet text
    OUPUT: a list of tokens '''
    punct = string.punctuation
    stop_words = stopwords.words('english')
    text_list = []
    snowball = SnowballStemmer('english')
    for word in text.lower().split():
        word = word.strip(punct)
        if word not in stop_words:
            text_list.append(snowball.stem(word))
    return text_list

def sql_tweets_sum_and_tokenized(df, timeseries= True):
    ''' Tokenizes the text column of a dataframe, and groups by geoid to create tweet count by geoid. 
    INPUT: a dataframe containing tweet text( 'text'), geoid('geoid10'), timestamp ('timestamp_ms').
    OUTPUT: A new dataframe with tokenized text and tweet count by geoid'''
    #take the string and tokenize words for a list 
    df['text'] = df.text.apply(tokenize_tweets)
    #create a column of ones for quick sum column during groupby
    df.insert(1, 'count', 1)
    #groupby parameters. Counts Tweets and appends tweet tokens to a master list. 
    if timeseries == False:
        df_group = df.groupby('geoid10').apply(lambda x: x.sum())
        #drop redundant columns
        df_group.drop('geoid10', 1, inplace=True)
        df_group.drop('timestamp_ms', 1, inplace=True)
        df_group = df_group.reset_index()
    else:
        #unfinished.
        return df
    return df_group


def add_time_variables(df):
	"""
	INPUT: dataframe with  timestamp_ms column. 
	OUTPUT: new dataframe with additional time-columns: hour, day of week, date
	"""
	df['times'] = df['timestamp_ms'].values.astype(int).astype('datetime64[ms]')
	df['hour']= pd.DatetimeIndex(df["times"]).hour
	df['DOW']= pd.DatetimeIndex(df["times"]).dayofweek
	df['date']= pd.DatetimeIndex(df["times"]).date
	return df



if __name__ == "__main__":
	#extract the data from SQL 
	df = get_swl_data()
	#tokenize the tweets
	df = sql_tweets_sum_and_tokenized(df, True)
	
	#add some time columns 
	df =add_time_variables(df)
	
	df= filter_out_bay(df)
	#save this as csv
	df.to_csv('data/tweets_with_time_wk2.csv')
