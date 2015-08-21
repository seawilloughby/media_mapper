import pandas as pd
import json
import random
import matplotlib.pyplot as plt
%matplotlib inline
from collections import defaultdict
import numpy as np
import media_mapper as mm
from wordcloud import WordCloud
import ast
from string import punctuation
from nltk.corpus import stopwords
import re
import glob

def process_dataframe():
	'''Runs a dataframe of twitter data from PostgreSQL through helper functions 
	to output the average tweet rate per san francisco neighborhood block, 
	and aggregates tweets. '''
	
    #retreive tweetdata from PostgreSQL
    ddf = mm.pipeline.retrieve_and_merge_tweet_data()
    #greate date and hour columns from the timestamp column
    df = mm.pipeline.transform_timestamp(df, hour = True)
    dfh = get_tweets_per_hour(df)
    #calculate the number of tweets per hour for analysis. 
    dfr = average_tweet_rate(dfh)
    #the list of tokens is inappropriate coded as a string. Corrests this.
    dfr['tokens'] = dfr['tokens'].apply(lambda x: ast.literal_eval(x)[0])

    #the twitter tokenizer doesn't remove all stop words. Remove stop words. 
    stop = stopwords.words('english')
    stop.extend([p for p in punctuation])
    stop.extend(['...',',,',',,,','..', 't','y','(@',')', 'c','i','I','a', \
                '@','.', 'co', 'com','amp', 'via','http','htt','https', '()',']')
    stop =[unicode(word) for word in stop]

    #remove san frnacisco blocks in the water
    odd_ids = ['060750601001016', '060750179021003','060759901000003', \
                '060759901000002', '060750179021000','060750601001000', \
                '060759804011003', '060750201001001']
    dfr = dfr[~dfr['geoid10'].isin(odd_ids)]
    
    #create world cloud images 
    generate_wordcloud(df)

    #format tweet rate so it is limited to two decimals
    dfr['tph'] = dfr.tph.apply(lambda x: format(x, '.2f'))

    #get a list of the generated word clouds for refrence
    wordcloud_files = glob.glob( '../app/static/wrdcld/*png')
    wordcloud_list = ['0' + word[21:-4] for word in wordcloud_files ]

    #add geometry data for each block to the dataframe
    dfr = merge_shapes_with_dataframe(dfr)

    #remove blocks that do not have word clouds 
    dfr = dfr[dfr['geoid10'].isin(wordcloud_list)]

    dfr = dfr.dropna()
    #create a geojson file for mapping.
    dataframe_to_geojson(df, '../app/data/wordcloud.json')

#GET A COUNT OF TWEETS EVERY HOUR OF EVERY DAY 
def get_tweets_per_hour(df):
    '''
    PARAMETERS 
    df - a dataframe with tweets tagged with time information.
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
    PARAMETERS
    df -  Dataframe whicn includes a date column, and average tweets per hour.
    date - If date == True, return a dataframe with the average
            tweets for each day.
            If date == False, return a dataframe grouped over all dates.
    
    OUPUT: Dataframe containing the average tweets per hour.
    '''
    
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

def remove_stopwords(token_row):
    ''' 
    PARAMETERS
    token_row - a string or list of tokens. 
    
    OUTPUT: customized stopwords are removed.'''
    
    if type(token_row) != list:
        token_row = [token_row]
    return [i.lower() for i in token_row if i.lower() not in stop]


def generate_wordcloud(df, outpath ='../../app/static/wrdcld/'):
    '''Generates and saves a word cloud images corresponding to each neighborhood block.
    PARAMETERS 
    df - a dataframe containing tokens and geoid (block id)
    
    OUTPUT: saved .png image wordcloud'''
    
    #remove stopwords
    df['tokens'] = df['tokens'].apply(lambda x:remove_stopwords(x))
    
    #generate a word cloud from each row 
    for idx in df.index:
        label = str(df.geoid10[idx]) + '.png'
        tokens = df.tokens[idx]
        #don't generate a word cloud if there are no tokens.
        try:
            #remove links 
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
    PARAMETERS
    df -  A dataframe containing tweet data and the geoid for each tweet. 
    
    OUPUT
    Merges dataframe with a csv containing the corresponding 
    shape file for each goid. Returns a pandas dataframe containing the 
    geoid and coordinates for each neighborhood block in San Francisco.
    ''' 
    
    ###Retrieve the Shape Files for Each Block:
    geo_df = pd.read_csv('data/intermediate_data/sf_only_sql_shapes.csv')
    #format the dataframe
    geo_df['geoid10'] = geo_df.geoid10.astype('str')
    geo_df.drop('Unnamed: 0', axis = 1, inplace = True)

    df['geoid10'] =df['geoid10'].apply(lambda x: x[1:])
    #create a new dataframe 
    df = pd.merge(geo_df, df, on='geoid10', how='outer')
    
    return df

#GENERATE GEOJSON FILE

def add_properties_geo(row):
    geoid = row['geoid10']
    tweetrate = row['tph']
    
    #image = "{{ url_for('static', filename='wrdcld/%s.png') }}" %(geoid)
    image = '../static/wrdcld/%s.png' %(geoid)
    geo_json = {"type": "Feature", "geometry": json.loads(row['geometry']), \
     "properties": {'image': image, 'geoid': geoid ,'tweetrate': tweetrate }}
    return geo_json

def dataframe_to_geojson(df, outfilename):
    '''Takes in a dataframe with a count and geoid10. Dumps it into a json geojason file'''
    df['geoid10'] = df['geoid10'].astype('str')
    df["tph"] = df['tph'].astype('str')
    list_to_export = []
    for idx, row in df.iterrows():
        list_to_export.append(add_properties_geo(row))
    with open(outfilename, 'w') as outfile:
        json.dump(list_to_export, outfile)



if __main__ == '__main__':
    '''Accesses stored twitter data, and generates a word cloud for each san francisco 
    neighborhood block, and generates a geojson file for mapping the cloud in mapbox. '''
    #run script
    process_dataframe()