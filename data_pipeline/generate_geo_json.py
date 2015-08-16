import pandas as pd
import json
import random
import matplotlib.pyplot as plt
%matplotlib inline
from collections import defaultdict
import numpy as np
import media_mapper as mm
from wordcloud import WordCloud
from string import punctuation
from nltk.corpus import stopwords

def process_dataframe(df):
	'''Runs a dataframe of twitter data from sql through helper functions 
	to output the average tweet rate per san francisco neighborhood block, 
	and aggregates tweets.'''
	df = mm.pipeline.retrieve_and_merge_tweet_data()
	df = mm.pipeline.transform_timestamp(df, hour = True)
	dfh = get_tweets_per_hour(df)
	dfr = average_tweet_rate(dfh)
	#the list of tokens is inappropriate coded as a string. 
	dfr['tokens'] = dfr['tokens'].apply(lambda x: ast.literal_eval(x)[0])
	#remove stopwords
	stop = stopwords.words('english')
    stop.extend([p for p in punctuation])
    stop.extend(['...',',,',',,,','..', 't','y','(@',')', 'c','i','I','a', '@','.', 'co', 'com','amp', 'via','http','htt','https', '()'])
    stop =[unicode(word) for word in stop]


#GET A COUNT OF TWEETS EVERY HOUR OF EVERY DAY 
def get_tweets_per_hour(df):
    '''
    INPUT: a dataframe with tweets tagged with time information.
    OUTPUT: a transformed dataframe, where dataframe has been grouped
        to obtain the rate of tweets per hour for each day.
        Tokenized tweet text for every hour has been appended to one mater list.'''
    
    #set a count of tweets to determine tweet rate
    df['tweetcnt'] = 1
    #get a total count of tweets
    dfh = df.groupby(['geoid10','date', 'hour']).agg(sum).reset_index().drop('id', 1)
    #append the tokenized tweet data together
    d_txt = df.groupby(['geoid10', 'date','hour'])['text'].apply(lambda x: ','.join(x)).reset_index()
    #merge dataframes
    dfh['tokens'] = d_txt['text']
    dfh['tph'] = dfh['tweetcnt']
    dfh.drop('tweetcnt', 1, inplace = True)
    return dfh

def average_tweet_rate(df, date = False):
    '''
    INPUT: Dataframe with a date column, and average tweets per hour.
    OUPUT: Dataframe with the average tweets per hour.
            If date == True, return a dataframe with the average
            tweets for each day.
            If date == False, return a dataframe grouped over all dates.'''
    
    #get the average tweets per hour over days 
    df_date = df.groupby(['geoid10','date']).agg(np.mean).reset_index()
    #get a grouped sum of the words
    df_txt = df.groupby(['geoid10', 'date'])['tokens'].apply(lambda x: ','.join(x)).reset_index()
    #merge these two dataframes together
    df_date['tokens'] = df_txt['tokens']
    
    if date == True:
        return df_date
    
    else:
        dff = df_date.groupby(['geoid10']).agg(np.mean).reset_index()
        #get a grouped sum of the words
        dff_txt = df_date.groupby(['geoid10'])['tokens'].apply(lambda x: ','.join(x)).reset_index()
        #merge these two dataframes together
        dff['tokens'] = dff_txt['tokens']
        return dff

def remove_stopwords_and_links(token_row):
    if type(token_row) != list:
        token_row = [token_row]
    return [i.lower() for i in token_row if i.lower() not in stop]


def generate_wordcloud(df, outpath ='../../app/static/wrdcld/'):
    '''generates and saves a word cloud images corresponding to each neighborhood block.
    INPUT: dataframe containing tokens and geoid
    OUTPUT: saved .png image wordcloud'''
    
    #remove stopwords
    df['tokens'] = df['tokens'].apply(lambda x:remove_stopwords(x))
    #generate a word cloud from each row 
    for idx in df.index:
        label = str(df.geoid10[idx]) + '.png'
        tokens = df.tokens[idx]
        #don't generate a word cloud if there are no tokens.
        try:
            tokens = [re.sub(r'http.*$', '', item) for item in tokens]
            wordcloud = WordCloud(min_font_size = 6,font_step = 1,  \
                     background_color = 'white', scale= 1 ).generate(' '.join(tokens))
            plt.imshow(wordcloud)
            plt.axis("off")
            #plt.show()
            plt.savefig(outpath + label,  bbox_inches='tight')
        except:
            pass

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
    #fill no tweets with a zero value
    df.tweetcnt.fillna(0, inplace = True)
    #drop empty hour columns
    return df

if __main__ == '__main__':
	#retrieve twitter data with shape files 
	df = mm.pipeline.retrieve_and_merge_tweet_data()
	#obtain rate of tweets per hour for each neighborhood block and aggregate tweets
	df = process_dataframe(df)
    #generate a wordcloud from the images 
    generate_wordcloud(df)
