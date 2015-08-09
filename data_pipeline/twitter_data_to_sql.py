import pandas as pd
import json
import requests
import re
import psycopg2
import glob
import time
from sqlalchemy import create_engine

#READ TWITTER JSON FILES FROM FOLDER:

def json_to_df(filename):
    '''Takes in a json file. Returns a pandas dataframe'''
    with open(filename, 'r') as f:
        l = f.readlines()

    data = [json.loads(s) for s in l]
    return pd.DataFrame(data)

def get_mega_dataframe(filepath):
    '''Takes a filepath to a directory of json files for twitterdata
    Runs through all the files, reads them into a pandas dataframe, 
    and returns a mega-dataframe of all the json files appended together'''
    tweet_files= glob.glob(filepath)
    df = json_to_df(tweet_files[0])
    for tf in tweet_files[1:]:
        temp_df = json_to_df(tf)
        df.append(temp_df)      
    return df


#CLEAN TWITTER DATA IN DATAFRAMES TO INSERT INTO DATABASE

def extract_columns(df):
    '''Called by clean_text_for_sql. Takes in a pandas dataframe. Returns a smaller dataframe:
    Text, Coordinates, timestamp'''
    #only include rows with coordinates
    df = df[~df['coordinates'].isnull()]
    #make a new dataframe with coordinates, tweets, and timestamps
    df = df[['coordinates', 'text' ,'timestamp_ms']]
    #get a list of coordinates to break it into long and lat data
    coor = df.coordinates.tolist()
    #list of the longitude coordinates
    lons = [c['coordinates'][0] for c in coor]
    #list of the latitude coordinates 
    lats = [c['coordinates'][1] for c in coor] 
    #turn lats and longs into panda series. Append them to the dataframe.
    df['lons'] = pd.Series(lons)
    df['lats'] = pd.Series(lats)
    df = df.drop('coordinates', 1)   
    return df 

def clean_text_for_sql(df):
    '''Takes in a dataframe with a text column containing emoticons, ect. 
    Returns a dataframe where the text has been striped of punctuation and repeats
    Also reorders the columns to fit the order I want for SQL'''
    df = extract_columns(df)
    #remove unicode and punctuation to make text compatible with sql
    df['text'] = [re.sub('[^A-Za-z0-9]+', ' ',s)for s in df.text.tolist()]
    df.columns.tolist()          
    #select the columns to input into sql
    ordered_colums = ['timestamp_ms','text', 'lats', 'lons' ]
    df = df[ordered_colums]
    #drop any replicate rows
    df = df.drop_duplicates()
    return df

def format_sql_database(dbname = 'zipfiantwitter', user = 'clwilloughby', twitter_table = 'tweetedBIGwk2', geo_table='sf_neighb', geo_twitter_table =  'tweeted_neighb_wk2' ):
	
	engine = create_engine('postgresql://clwilloughby:christy@localhost:5432/zipfiantwitter')
	df_twitter.to_sql(twitter_table, engine, if_exists='replace')

	conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
	c = conn.cursor()
	query = """ SELECT AddGeometryColumn(twitter_table,'geom',4326,'POINT',2);"""
	c.execute(query)
	conn.commit()

	conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
	c = conn.cursor()
	query = """UPDATE twitter_table SET geom = ST_SetSRID(ST_MakePoint(lons, lats), 4326);"""
	c.execute(query)
	conn.commit()  

	conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
	c = conn.cursor()
	query = """SELECT UpdateGeometrySRID(geo_table, 'wkb_geometry', 4326);""" 
	c.execute(query)
	conn.commit() 

	conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
	c = conn.cursor()
	query = """ SELECT points.*, polys.geoid10
	                INTO geo_twitter_table 
	                FROM geo_table polys
	                JOIN twitter_table points 
	                ON ST_Within(points.geom,polys.wkb_geometry);"""
	c.execute(query)
	conn.commit()
	conn.close()

if __main__ == '__name__':
	#call tweets from a filepath: 	
	df_tweets = get_mega_dataframe('../../../../../Desktop/toomanytweets/*json')
	
	#extract meaningful info from the columns:
	df_tweets = clean_text_for_sql(df_tweets)

	#output a raw CSV of the cleaned data
	df_tweets.to_csv('data/tweets_cleaned.csv', encoding = 'utf-8', index = False, header=False, if_exists ='append')
