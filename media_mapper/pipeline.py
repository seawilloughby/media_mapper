import glob
import pandas as pd
import json
import psycopg2
import string 
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sqlalchemy import create_engine
from media_mapper import twokenizer
import matplotlib.pyplot as plt


def retrieve_sql_tweets(table_name = 'tweets_with_geo'):
    '''Connects to zipfiantwitter PostgreSQL database. 
    Extracts the twitter data with geoid10, and returns it as a dataframe.'''
    conn_dict = {'dbname':'zipfiantwitter', 'user':'clwilloughby', 'password': '', 'host':'/tmp'}
    conn = psycopg2.connect(dbname=conn_dict['dbname'], user=conn_dict['user'], host='/tmp')
    cur = conn.cursor()
    map_query = """
    SELECT timestamp_ms, geoid10, id
    FROM %s
                    ;""" %table_name
    return pd.read_sql(map_query, conn)


def retrieve_and_merge_tweet_data(table_name = 'tweets_with_geo', tweet_text_file='/Users/christy/Documents/root/repos/media_mapper/data_pipeline/data/intermediate_data/json_tweets_in_df_twitokend.csv' ):
    '''
    Querys PostgreSQL to retreive a table (tablename) and merges that table with a csv 
    (tweet_text_file) on the 'id' column. Rejoins a twitter table with geometry information 
    in PostgreSQL withcorresponding tokenized tweet text.
    
    PARAMETERS:  
    tablename - the name of the PostgreSQL table to query.
    tweet_text_file - the filepath to a csv containing an 'id' column. 
    
    OUTPUT: A merged pandas dataframe. '''
    
    #get SF Data From SQL
    df_sql = retrieve_sql_tweets(table_name)
    #get tokenized text data 
    ds_tokens = pd.read_csv(tweet_text_file)
    df_sql = df_sql.set_index('id')
    ds_tokens = ds_tokens.set_index('id')
    df = df_sql.join(ds_tokens).reset_index()
    df.drop('Unnamed: 0', 1, inplace = True)
    return df

#TEXT MANIPULATION OF TWITTER DATA

#B. tokenize with a twitter-specific tokenizer
def twokenize_text(df, outfile = '/Users/christy/Documents/root/repos/media_mapper/data_pipeline/data/intermediate_data/jsontweets_in_df_twitokend.csv'):
    '''Takes in a dataframe with a text column containing emoticons, ect. 
    Applies a twitter specific tokenizer, and saves the dataframe. 
    '''
    
    df['text'] = [twokenizer.simpleTokenize(s) for s in df.text.tolist()]
    df.to_csv(outfile)
    

#C. use the general nltk library 
def tokenize_text_nltk(text):
    '''Tokenizes a sting with the nltk library. 
    To apply function to an entire dataframe: df['text'] = df.text.apply(tokenize_text_nltk)'''
    
    punct = string.punctuation
    stop_words = stopwords.words('english')
    text_list = []
    snowball = SnowballStemmer('english')
    for word in text.lower().split():
        word = word.strip(punct)
        if word not in stop_words:
            text_list.append(snowball.stem(word))
    return text_lisy


#ADD DATE VARIABLES TO A DATAFRAME FROM A TIMESTAMP 

def transform_timestamp(df, date = True, hour = False, DOW = False ):
    """
    PARAMETERS
    df - A dataframe with a 'timestamp_ms' column. C
    Creates additional columns of date, hour, or day of week (DOW).
    
    Returns the dataframe with added columns."""

    df['time'] = df['timestamp_ms'].values.astype(int).astype('datetime64[ms]')
    df['date']= pd.DatetimeIndex(df["time"]).date
    if hour == True:
        df['hour']= pd.DatetimeIndex(df["time"]).hour
    if DOW == True:
        df['DOW']= pd.DatetimeIndex(df["time"]).dayofweek
    return df


#PLOTTING FUNCTIONS

def plot_neighborhoods(df,  column_labels='geoid10', x_colname ='hour', y_colname ='tweet_cnt'):
    '''Takes a dataframe with groups to plot as a color dimentions. 
    column_labels : the column to group by
    x and y colname: the columns names to plot on x and y axis'''
    groups = df.groupby(column_labels)
    # Plot
    fig, ax = plt.subplots()
    fig.set_figwidth(15)
    fig.set_figheight(10)
    ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling
    for name, group in groups:
        ax.plot(group[x_colname], group[y_colname], marker='o', linestyle='', ms=12, label=name)
    ax.legend()
    plt.show()


def merge_shapes_with_dataframe(df):
    '''
    INPUT: A dataframe containing tweet data and the geoid
            for each tweet. 
            Merges dataframe with a csv containing the corresponding 
            shape file for each goid.
    OUPUT: A pandas dataframe containing the geoid and coordinates for each 
            neighborhood block in San Francisco.''' 
    
    ###Retrieve the Shape Files for Each Block:
    geo_df = pd.read_csv('/Users/christy/Documents/root/repos/media_mapper/data_pipeline/data/intermediate_data/sf_only_sql_shapes.csv')
    #format the dataframe
    geo_df['geoid10'] = geo_df.geoid10.astype('str')
    geo_df.drop('Unnamed: 0', axis = 1, inplace = True)

    df['geoid10'] =df['geoid10'].apply(lambda x: x[1:])
    #create a new dataframe 
    df = pd.merge(geo_df, df, on='geoid10', how='outer')
    return df



