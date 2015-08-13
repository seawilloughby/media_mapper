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
    '''Takes in a json file (such as tweets). Returns a pandas dataframe'''
    with open(filename, 'r') as f:
        l = f.readlines()
    try:
        data = [json.loads(s) for s in l]
        if columns:
            df = pd.DataFrame(data)[columns]
        else:
            df = pd.DataFrame(data)

    except Exception as e:
        print e, filename
        df = pd.DataFrame(None)
    return df

def get_mega_dataframe(filepath, columns = ['coordinates', 'text', 'timestamp_ms', 'id']):
    '''Takes a filepath to a directory of json files for twitterdata.
    Reads every file into a pandas dataframe. Calls helper function json_to_df.
    Returns a mega-dataframe of all the json files appended together.
    Saves a copy of the '''
    tweet_files= glob.glob(filepath)
    df_list = [json_to_df(tf, columns=columns) for tf in tweet_files]
    df_list = [df for df in df_list if df is not None]
    df = pd.concat(df_list).reset_index(drop = True)
    return df


def retrieve_and_merge_tweet_data():
    '''Retrieves twitter geo data from SQL, and tweet text that has been tokenized. 
    Returns the merged dataframe.'''
    #get SF Data From SQL
    df = retrieve_sql_tweets('tweets_with_geoV6')
    #get text data from picke
    dftxt = pd.read_csv('../data_pipeline/data/intermediate_data/json_tweets_in_df_twitokend.csv')
    df = df.set_index('id')
    dftxt = dftxt.set_index('id')
    dfall = df.join(dftxt).reset_index()
    dfall.drop('Unnamed: 0', 1, inplace = True)
    return dfall

#FUNCTIONS TO CLEAN DATAFRAME OF TWEETS

def exract_coordinates_from_tweets(df, outfile = 'data/intermediate_data/jsontweets_in_df.pkl'):
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
def twokenize_text(df, outfile = 'data/intermediate_data/jsontweets_in_df_twitokend.csv'):
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


#PLACE TWITTER DATA IN SQL. USE TO GET GEO COORDINATES
def create_tweet_table_sql(df, tablename='tweetsv4', remove_text_column = True):
    ''' Insersts a dataframe into SQL, but remoces the text column if True,and returns the text and id dataframe. '''
    if remove_text_column == True:
        tweettext_df = df[['text', 'id']]
        df.pop('text')
        engine = create_engine('postgresql://clwilloughby:christy@localhost:5432/zipfiantwitter')
        df.to_sql(tablename, engine, if_exists='replace')
        return tweettext_df
    else:
        engine = create_engine('postgresql://clwilloughby:christy@localhost:5432/zipfiantwitter')
        df.to_sql(tablename, engine, if_exists='replace')

def format_tweet_table_sql(tweet_table='tweetsv3' , new_geo_tweet_table = 'tweets_with_geo'):
    '''Takes an existing twitter table (tweet_table). Adds a geo column, and fills with the proper geoid.
    Filters out tweets that are not in SF county, and creates a table with tweet information, and relevant
    geojason information (new_geo_tweet_table). '''

    conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
    c = conn.cursor()

    query = """ SELECT AddGeometryColumn(%s,'geom',4326,'POINT',2);""" %tweet_table
    c.execute(query)
    conn.commit()

    conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
    c = conn.cursor()
    query = """UPDATE %s SET geom = ST_SetSRID(ST_MakePoint(lons, lats), 4326);""" %tweet_table 
    c.execute(query)
    conn.commit()            

    conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
    c = conn.cursor()
    query = """SELECT UpdateGeometrySRID('sf_neighb', 'wkb_geometry', 4326);""" 
    c.execute(query)
    conn.commit() 

    conn = psycopg2.connect(dbname='zipfiantwitter', user ='clwilloughby', host = '/tmp')
    c = conn.cursor()
    query = """ SELECT points.*, polys.geoid10
                    INTO %s 
                    FROM sf_neighb polys
                    JOIN %s points 
                    ON (ST_Within(points.geom,polys.wkb_geometry) AND
                    polys.countyfp10 = '075');""" %(new_geo_tweet_table, tweet_table)
    c.execute(query)
    conn.commit()
    conn.close()
 

def retrieve_sql_tweets(tablename):
    '''Connects to zipfiantwitter database. Need to hard code table to extract.
    Extracts the twitter data with geoid10, and returns it as a dataframe.'''
    conn_dict = {'dbname':'zipfiantwitter', 'user':'clwilloughby', 'password': '', 'host':'/tmp'}
    conn = psycopg2.connect(dbname=conn_dict['dbname'], user=conn_dict['user'], host='/tmp')
    cur = conn.cursor()
    map_query = """
    SELECT timestamp_ms, geoid10, id
    FROM %s
                    ;""" %tablename
    return pd.read_sql(map_query, conn)


#ADD DATE VARIABLES TO A DATAFRAME FROM A TIMESTAMP 

def transform_timestamp(df, date = True, hour = False, DOW = False ):
    """Takes a dataframe with a 'timestamp_ms' column. Creates additionall columns of date, hour, or day of week.
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
    Also assmes a 'tweetcnt' column. Returns the new dataframe'''
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