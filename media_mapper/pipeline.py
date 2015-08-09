import glob
import pandas as pd
import json
import tokenizer
import psycopg2
import string 
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sqlalchemy import create_engine


#FUNCTIONS TO TURN TWEET JSON FILES INTO PANDAS DATAFRAME

def json_to_df(filename):
    '''Takes in a json file (such as tweets). Returns a pandas dataframe'''
    with open(filename, 'r') as f:
        l = f.readlines()
    try:
        data = [json.loads(s) for s in l]
    except Exception as e:
        print e, filename
        return None 
    return pd.DataFrame(data)

def get_mega_dataframe(filepath):
    '''Takes a filepath to a directory of json files for twitterdata.
    Reads every file into a pandas dataframe. Calls helper function json_to_df.
    Returns a mega-dataframe of all the json files appended together.
    Saves a copy of the '''
    tweet_files= glob.glob(filepath)
    df = pd.concat([json_to_df(tf) for tf in tweet_files]).drop_duplicates().reset_index(drop=True)
    return df


#FUNCTIONS TO CLEAN DATAFRAME OF TWEETS

def exract_coordinates_from_tweets(df, outfile = 'data/intermediate_data/jsontweets_in_df.csv'):
    '''Takes in a pandas dataframe of json tweets with coordinates.
    Extracts lattitude and longtidue.
    Returns a smaller dataframe with columns: Text, Coordinates, timestamp.
    Also saves a copy to a csv at the given outfile'''
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
    df.to_csv(outfile) 
    return df 

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
def tokenize_text(df, outfile = 'data/intermediate_data/jsontweets_in_df_twitokend.csv'):
    '''Takes in a dataframe with a text column containing emoticons, ect. 
    Returns a dataframe where the text has been striped of punctuation and repeats
    Also reorders the columns to fit the order I want for SQL'''
    df['text'] = [tokenizer.simpleTokenize(s) for s in df.text.tolist()]
    df.columns.tolist()          
    ordered_colums = [u'timestamp_ms',u'text', 'lats', 'lons' ]
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
    return text_list


#TWITTER DATA INTO SQL

def retrieve_sql_tweets():
    '''Connects to zipfiantwitter database. Need to hard code table to extract.
    Extracts the twitter data with geoid10, and returns it as a dataframe.'''
    conn_dict = {'dbname':'zipfiantwitter', 'user':'clwilloughby', 'password': '', 'host':'/tmp'}
    conn = psycopg2.connect(dbname=conn_dict['dbname'], user=conn_dict['user'], host='/tmp')
    cur = conn.cursor()
    map_query = """
    SELECT timestamp_ms, text, geoid10
    FROM tweeted_neighb_wk2
                    ;"""
    return pd.read_sql(map_query, conn)


# FILTER TWITTER DATAFRAME FOR JUST TWEETS IN SAN FRANCISCO
# MAY BE UNNECISSARY IF PULLING DATA FROM SQL. Already joined on tweets within SF 
def extract_sanfrancisco_tweets(df, outfile = 'data/intermediate_data/sf_geo_tweets.csv'):
    '''Takes a twitter dataframe with a geoid10 column.
    Uses the csv file 'sf_geoids.csv' to extract only tweets occuring in SF.'''
    #get a list of all sf geoids
    with open('data/sf_geoids.csv', 'rb') as f:
        reader = csv.reader(f)
    sf_geolist = list(reader)[0]
    df = df[df['geoid10'].astype(str).isin(sf_geolist)]
    df.to_csv()


#PLACE TWITTER DATA IN SQL. USE TO GET GEO COORDINATES
def create_tweet_table(df):
    '''Takes a dataframe. Puts it into sql.  Creates a geometry column and
    infers the geoid'''

    engine = create_engine('postgresql://clwilloughby:christy@localhost:5432/zipfiantwitter')
    df.to_sql("tweet_middle", engine, if_exists='replace')

    conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
    c = conn.cursor()

    query = """ SELECT AddGeometryColumn('tweet_middle','geom',4326,'POINT',2);"""
    c.execute(query)
    conn.commit()
    

    conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
    c = conn.cursor()
    query = """UPDATE "tweet_middle" SET geom = ST_SetSRID(ST_MakePoint(lons, lats), 4326);"""
    c.execute(query)
    conn.commit()            

    conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
    c = conn.cursor()
    query = """SELECT UpdateGeometrySRID('sf_neighb', 'wkb_geometry', 4326);""" 
    c.execute(query)
    conn.commit() 

    conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')

    #create a new table with geometry columns only in san francisco
    c = conn.cursor()
    query = """ SELECT points.*, polys.geoid10
                    INTO tweets_with_geo 
                    FROM sf_neighb polys
                    JOIN "tweetedBIGwk2" points 
                    ON (ST_Within(points.geom,polys.wkb_geometry) AND
                    polys.countyfp10 = '075');"""
    c.execute(query)
    conn.commit()
    conn.close()

def append_tweet_table():
    pass


