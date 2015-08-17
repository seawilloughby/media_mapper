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
	df = mm.pipeline.transform_timestamp(df, hour = True)
	df = get_tweet_rate(df)

	#remove geoids that are in the ocean
	odd_ids = ['060750601001016', '060750179021003','060759901000003',\
               '060759901000002', '060750179021000','060750601001000',\
               '060759804011003', '060750201001001']  
	df = df[~df['geoid10'].isin(odd_ids)]

	#customize stopwords for editing tokens
	stopwords = nltk.corpus.stopwords.words('english')
	stopwords.extend(['...',',,',',,,','..', 't','y','(@',')', 'c','i','I','a',\
	                '@','.', 'co', 'com','amp', 'via','http','htt','https', '()',']'])
	sstopwords=[unicode(word) for word in stopwords]


	#break dataframe into four hour chunks of time throughout the day
	df_hour = tweets_by_hour(df)
	#obtain geometry data for each geoid for mapping 
	df_hour = retrieve_geometry_information(df_hour)
	#get top ten tokens for each group 
	df_hour['top_ten'] = df_hour.tokens.apply(top_tokens)
	
	#generate geojsons 
	for time in df_hour.hr_bin.unique():
	    time_df = df_hour[df_hour['hr_bin']== time]
	    outfilename = 'data/' + time + '.json'
	    dataframe_to_geojson(time_df, outfilename)


def get_tweet_rate(df):
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

def tweets_by_hour(df):
	'''Groups twitter data by the geoid and hour of day. 
	Preserves tokens. Returns modified dataframe.'''

	hdf = df.groupby(['geoid10', 'hour']).agg(np.mean).reset_index()
	#get a grouped sum of the words
	hour_df_txt = df.groupby(['geoid10', 'hour'])['tokens'].apply(lambda x: ','.join(x)).reset_index()
	#merge these two dataframes together
	hdf['tokens'] = hour_df_txt['tokens']
	
	#cut time into five bins throughout the day
	hdf['hr_bin'] = pd.cut(hdf.hour, bins = 5, \
		labels = ['latenight', 'dawn','morning','afternoon','evening'])
	
	return hdf

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
    hourlydf = pd.merge(geodf, df, on='geoid10', how='outer')
    #fill no tweets with a zero value
    hourlydf.dropna(subset = ['hour'], inplace = True)
    
    return hourlydf



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
    tweetrate = row['tph']
    top_ten = row['top_ten']
    geo_json = {"type": "Feature", "geometry": json.loads(row['geometry']), \
                "properties": {'geoid': geoid ,'tph': tph, 'top_ten': top_ten }}
    return geo_json

def dataframe_to_geojson(df, outfilename):
    '''Takes in a dataframe with a count, geoid10, and list of tokens. 
    Dumps it into a geojson file for mapping.ß'''
    
    df['geoid10'] = df['geoid10'].astype('str')
    df["tph"] = df['tph'].astype('str')
    list_to_export = []
    for idx, row in df.iterrows():
        list_to_export.append(add_properties_geo(row))
    with open(outfilename, 'w') as outfile:
        json.dump(list_to_export, outfile)


if __name__ == '__main__':
	#create geojson maps based on grouping the day into five time blocks. 
	create_maps()