import pandas as pd
import numpy as np
import json
import psycopg2
import random
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import string
import datetime

#RETRIEVE DATA
def get_sql_data(table = "tweeted_neighb_wk2"):
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
    '''Called by sql_tweets_sum_and_tokenized. Tokenizes a sting.'''
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
    '''Takes a sql dataframe of tweets, geoids, and timestamps.
    Tokenizes the tweets. Groupsby geoid and timestamp (if True) to create overal counts
    Returns a new dataframe.'''
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
        #somethign about time. This will be difficult. 
        return df
    return df_group


def add_time_varaibles(df):
	"""Takes a dataframe with a timestamp_ms column. Generates a column of hour, day of week, and date"""
	df['times'] = df['timestamp_ms'].values.astype(int).astype('datetime64[ms]')
	df['hour']= pd.DatetimeIndex(df["times"]).hour
	df['DOW']= pd.DatetimeIndex(df["times"]).dayofweek
	df['date']= pd.DatetimeIndex(df["times"]).date
	return df

def filter_sf_only(df):
    '''Takes a dataframe with a geoid10 column. Subselects only rows that have a geoid10 within san francisco
    Returns the new dataframe.'''
    #get the list of unique geoids for san francisco
    with open('data/sf_geoids.csv', 'rb') as f:
        reader = csv.reader(f)
        sf_geolist = list(reader)[0]
    return df[df['geoid10'].astype(str).isin(sf_geolist)]


if __name__ == "__main__":
	
    #Retrieve data from sql table
    df = get_sql_data()

	#tokenize the tweets
	df_timetweet = sql_tweets_sum_and_tokenized(df_tweet_shapes, True)
	#add some time columns 
	df =add_time_varaibles(df)

    #filter so only SF tweets
	df = filter_sf_only(df)
	
    #save this as csv
	df_timetweet.to_csv('data/tweets_with_time_wk2.csv')
