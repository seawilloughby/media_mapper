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



#FUNCTIONS TO TURN TWEET JSON FILES INTO PANDAS DATAFRAME

def json_to_df(filename, columns = None):
    '''INPUT: filename - a json file (such as tweets). 
      OUTPUT: pandas dataframe'''
    
    with open(filename, 'r') as f:
        l = f.readlines()
    try:
        data = [json.loads(s) for s in l]
        if columns:
            df = pd.DataFrame(data)[columns]
        else:
            df = pd.DataFrame(data)

    #handle cases where the file is empty
    except Exception as e:
        print e, filename
        df = pd.DataFrame(None)
    
    return df

def get_mega_dataframe(filepath, columns = ['coordinates', 'text', 'timestamp_ms', 'id']):
    '''Reads a directory of json files into one pandas dataframe.

    INPUT: filepath - a directory json twitterdata.
    OUTPUT: a pandas dataframe
    '''
    #create a list of every json file in a directory
    tweet_files= glob.glob(filepath)
    #read files into a list of dataframes 
    df_list = [json_to_df(tf, columns=columns) for tf in tweet_files]
    #remove empty dataframes
    df_list = [df for df in df_list if df is not None]
    df = pd.concat(df_list).reset_index(drop = True)
    
    return df

def retrieve_shapefiles(outfile = 'data/sf_only_sql_shapes.csv'):
    '''Retrieves SF neighborhood shapefiles from the SQL database. Saves the
    dataframe to the folder give by outfile'''
    
    #connect to postgress 
    conn_dict = {'dbname':'zipfiantwitter', 'user':'clwilloughby', 'password': '', 'host':'/tmp'}
    conn = psycopg2.connect(dbname=conn_dict['dbname'], user=conn_dict['user'], host='/tmp')
    cur = conn.cursor()

    map_query = """
            SELECT
                    DISTINCT
                    ST_asGEOJSON(wkb_geometry) geometry
                    , geoid10

                    FROM sf_neighb 
                    WHERE countyfp10 = '075'
                    ;"""

    return pd.read_sql(map_query, conn)


def retrieve_sql_tweets(table_name):
    '''Connects to zipfiantwitter database. 
    Extracts the twitter data with geoid10, and returns it as a dataframe.'''
    conn_dict = {'dbname':'zipfiantwitter', 'user':'clwilloughby', 'password': '', 'host':'/tmp'}
    conn = psycopg2.connect(dbname=conn_dict['dbname'], user=conn_dict['user'], host='/tmp')
    cur = conn.cursor()
    map_query = """
    SELECT timestamp_ms, geoid10, id
    FROM %s
                    ;""" %table_name
    return pd.read_sql(map_query, conn)


def retrieve_and_merge_tweet_data(table_name = 'tweets_with_geoV6', tweet_text_file='/Users/christy/Documents/root/repos/media_mapper/data_pipeline/data/intermediate_data/json_tweets_in_df_twitokend.csv' ):
    '''
    Querys SQL to retreive a table (tablename) and merges that table with a csv (tweet_text_file)
    on the 'id' column. Rejoins a twitter table with geometry information in SQL with
    corresponding tokenized tweet text.
    
    INPUT:  a) tablename - the name of the SQL table to query.
            b) tweet_text_file - the filepath to a csv containing an id  column. 
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

#FUNCTIONS TO CLEAN DATAFRAME OF TWEETS

def exract_coordinates_from_tweets(df, outfile = '/Users/christy/Documents/root/repos/media_mapper/data_pipeline/data/intermediate_data/jsontweets_in_df.pkl'):
    '''Takes in a pandas dataframe of json tweets with coordinates.
    Extracts lattitude and longtidue.
    Returns a smaller dataframe with columns: Text, Coordinates, timestamp.
    Also saves a copy to a csv at the given outfile'''
    #only include rows with coordinates
    df = df[~df['coordinates'].isnull()]
    #make a new dataframe with coordinates, tweets, and timestamps
    df = df[['coordinates', 'text' ,'timestamp_ms', 'id']]
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
    df = df.drop_duplicates().reset_index(drop = True)
    #don't pickle with text!! Values go missing for some reason. 
    return df 

def pop_text(df):
    '''removes a pesky column of text of tweets'''
    tweet_text_df = no_dup[['text', 'id']]
    no_dup.pop('text')

#TEXT MANIPULATIO OF TWITTER DATA

#A. remove punctuation
def clean_text_for_sql(df):
    '''Takes in a dataframe with a text column containing emoticons, ect. 
    Returns a dataframe where the text has been striped of punctuation and repeats
    Orders columns in this format: timestamp_ms, text, lats, lons'''
    df = extract_columns(df)
    df['text'] = [re.sub('[^A-Za-z0-9]+', ' ',s)for s in df.text.tolist()]
    df.columns.tolist()          
    ordered_colums = [ 'timestamp_ms', 'text', 'lats', 'lons' ]
    return df[ordered_colums]

#B. tokenize with a twitter-specific tokenizer
def twokenize_text(df, outfile = '/Users/christy/Documents/root/repos/media_mapper/data_pipeline/data/intermediate_data/jsontweets_in_df_twitokend.csv'):
    '''Takes in a dataframe with a text column containing emoticons, ect. 
    Returns a dataframe where the text has been striped of punctuation and repeats
    Also reorders the columns to fit the order I want for SQL'''
    df['text'] = [twokenizer.simpleTokenize(s) for s in df.text.tolist()]
    df.columns.tolist()          
    ordered_colums = ['id','text']
    df = df[ordered_colums]
    df.to_csv(outfile)
    return df

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
    """Takes a dataframe with a 'timestamp_ms' column. Creates additional columns of date, hour, or day of week.
    Returns the dataframe with added columns."""

    df['time'] = df['timestamp_ms'].values.astype(int).astype('datetime64[ms]')
    df['date']= pd.DatetimeIndex(df["time"]).date
    if hour == True:
        df['hour']= pd.DatetimeIndex(df["time"]).hour
    if DOW == True:
        df['DOW']= pd.DatetimeIndex(df["time"]).dayofweek
    return df



#HANDY PLOTTING FUNCTIONS

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
    '''imports sql shape files for san francisco. Adds them to a dataframe based on the shared 'geoid10' column.
    Also assumes a 'tweetcnt' column. Returns the new dataframe'''
    ###Retrieve the Shape Files for Each Block:
    geodf = pd.read_csv('/Users/christy/Documents/root/repos/media_mapper/data_pipeline/data/intermediate_data/sf_only_sql_shapes.csv')
    #format the dataframe
    geodf['geoid10'] = geodf.geoid10.astype('str')
    geodf.drop('Unnamed: 0', axis = 1, inplace = True)

    df['geoid10'] =df['geoid10'].apply(lambda x: x[1:])
    #create a new dataframe 
    df = pd.merge(geodf, df, on='geoid10', how='outer')
    #fill no tweets with a zero value
    df.tweetcnt.fillna(0, inplace = True)
    #drop empty hour columns
    return df

#CLUSTERING FUNCTIONS

def dummy_time_variables(df, dow = False, hr = False):
    '''Takes a dataframe with a dow and or hour column. Adds dummy variables relating to day of week and or hour. 
    Returns new dataframe.'''
    if dow == True:
        dfdow = pd.get_dummies(df.DOW, prefix = 'dow')
        dfdow.drop('dow_0', 1, inplace = True)
        if hr == False:
            dfdow['geoid'] = df['geoid10', 'twt_cnt']
            return dfdow
        else: pass 
    if hr == True:
        dfhour = pd.get_dummies(df.hour, prefix = 'hr')
        dfhour.drop('hr_0', 1, inplace = True)
        dfhour['geoid'] = df['geoid10']
        dfhour['twt_cnt'] = df['twt_cnt']
        if dow == False:
            return dfhour
        else:
            df = pd.concat([dfdow,dfhour],axis = 1)
            return df