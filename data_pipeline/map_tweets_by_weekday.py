import pandas as pd
import media_mapper as mm
import nltk
from ast import literal_eval
import json
import numpy as np
from string import punctuation
from nltk.corpus import stopwords



def create_maps():
    '''generates geojson files for creating maps of twitter activity
    broken down into weekend vs week day, and by major chunks of time.'''

    df = mm.pipeline.retrieve_and_merge_tweet_data()
    wkd_df = mm.pipeline.transform_timestamp(df, DOW = True)
    wkd_df = get_tweets_per_day(wkd_df)

    #remove geoids that are in the ocean
    odd_ids = ['060750601001016', '060750179021003','060759901000003',\
               '060759901000002', '060750179021000','060750601001000',\
               '060759804011003', '060750201001001']  
    df = df[~df['geoid10'].isin(odd_ids)]

    #get the average number of tweets per day for every day of the week
    wkd_df = wkd_df.groupby(['geoid10', 'DOW']).agg(np.mean).reset_index()
    #get a grouped sum of the words
    wkd_df_txt = wkd_df.groupby(['geoid10', 'DOW'])['tokens'].apply(lambda x: ','.join(x)).reset_index()
    #merge these two dataframes together
    wkd_df['tokens'] = wkd_df_txt['tokens']

    #create a dataframe of only weekend values
    df_weekend = seperate_weekends(wkd_df, True)
    #create a dataframe of only weekday values 
    df_weekday = seperate_weekends(wkd_df, False)

    #customize stopwords for editing tokens
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend(['...',',,',',,,','..', 't','y','(@',')', 'c','i','I','a', ',',\
                    '@','.', 'co', 'com','amp','?' 'via','http','htt','https', '()',']'])
    stopwords.extend([str(char) for char in punctuation])
    sstopwords=[unicode(word) for word in stopwords]


    #get the most frequent words for visualization
    dfwkday['top_ten'] = dfwkday.tokens.apply(top_tokens)
    df_weeknd['top_ten'] = df_weeknd.tokens.apply(top_tokens)

    #get geometry information for each san francisco block
    df_end = retrieve_geometry_information(df_weeknd)
    df_day = retrieve_geometry_information(dfwkday)

    #generate geojsons 
    dataframe_to_geojson(df_end, 'data/weekend.json')
    dataframe_to_geojson(df_day, 'data/weekday.json')


def get_tweets_per_day(df):
    ''' INPUT: a dataframe with tweets tagged with time information.
        OUTPUT: a transformed dataframe, where dataframe has been grouped by date
        to obtain the rate of tweets per day. '''
    
    #set a count of tweets to determine tweet rate
    df['tweetcnt'] = 1
    #get a total count of tweets
    dfh = df.groupby(['geoid10','DOW', 'date']).agg(sum).reset_index().drop('id', 1)
    #append the tokenized tweet data together
    d_txt = df.groupby(['geoid10', 'DOW', 'date'])['text'].apply(lambda x: ','.join(x)).reset_index()
    #merge dataframes
    dfh['tokens'] = d_txt['text']
    #tweetcnt is now the tweets per day (tpd)
    dfh['tpd'] = dfh['tweetcnt']
    dfh.drop('tweetcnt', 1, inplace = True)
    return dfh

def seperate_weekends(df, weekend = True):
    '''Takes a dataframe with a column marked with the day of week.
    If weekend is True, returns a dataframe with just the weekend values
    If false, returns a dataframe with just the weekday values.
    Performs groupby to get mean tweet per day based on this grouping.'''
    if weekend == True:
        daysofweek = [6,7]
    else:
        threshold = [1,2,3,4,5]
    df = df[df['DOW'].isin(daysofweek)].drop('DOW', 1)
    dfweek = df.groupby('geoid10').agg(np.mean).reset_index()
    dfweek_txt = df.groupby('geoid10')['tokens'].apply(lambda x: ','.join(x)).reset_index()
    #merge these two dataframes together
    dfweek['tokens'] = dfweek_txt['tokens']



def retrieve_geometry_information(df):
    '''Obtains the geometry data for each geoid10. 
    Returns the dataframe with an extra geometry column.'''
    ###Retrieve the Shape Files for Each Block:
    geodf = pd.read_csv('../../../data/intermediate_data/sf_only_sql_shapes.csv')
    #format the dataframe
    geodf['geoid10'] = geodf.geoid10.astype('str')
    geodf.drop('Unnamed: 0', axis = 1, inplace = True)
    #set the index as the geoid
    #need to alter the geoid10 column to merge with shape files
    
    df['geoid10'] =df['geoid10'].apply(lambda x: x[1:])
    #create a new dataframe 
    weekdf = pd.merge(geodf, df, on='geoid10', how='outer')
    #fill no tweets with a zero value
    weekdf.dropna(subset = ['tpd'], inplace = True)
    return weekdf



def top_tokens(corpus_list, stopwords= stopwords, number=10):

    '''Takes a list of tokens. Returns the top ten, unless a different number given.'''

    #Checks to make sure the tokens are in a list, and not a string
    tokens = literal_eval(corpus_list)
    #If there are multiple tweets, flatten the list
    if type(tokens) ==tuple:
        tokens =[item for sublist in tokens for item in sublist]  
    allWordExceptStopDist = nltk.FreqDist(w.lower() for w in tokens if w not in stopwords) 
    mostCommon= allWordExceptStopDist.most_common(number)
    top_ten_string = ' '.join([tup[0] for tup in mostCommon])
    
    return top_ten_string


#CREATE GEOJSON FILES

def add_properties_geo(row):
    '''Translates a row of a dataframe into a geo_json string'''

    geoid = row['geoid10']
    tweetrate = row['tpd']
    top_ten = row['top_ten']
    geo_json = {"type": "Feature", "geometry": json.loads(row['geometry']), \
                "properties": {'geoid': geoid ,'tpd': tpd, 'top_ten': top_ten }}
    return geo_json

def dataframe_to_geojson(df, outfilename):
    '''Takes in a dataframe with a count, geoid10, and list of tokens. 
    Dumps it into a geojson file for mapping.ß'''
    
    df['geoid10'] = df['geoid10'].astype('str')
    df["tpd"] = df['tpd'].astype('str')
    list_to_export = []
    for idx, row in df.iterrows():
        list_to_export.append(add_properties_geo(row))
    with open(outfilename, 'w') as outfile:
        json.dump(list_to_export, outfile)


if __name__ == '__main__':

    #create geojson maps based on grouping the day into five time blocks. 
    create_maps()