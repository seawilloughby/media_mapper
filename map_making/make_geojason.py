
import pandas as pd
import json
import psycopg2
import random


def send_example_json():
    """Connects to database to retreive neighborhood coordinates. Returns a geojason"""
    
    conn_dict = {'dbname':'zipfiantwitter', 'user':'clwilloughby', 'password': '', 'host':'/tmp'}
    conn = psycopg2.connect(dbname=conn_dict['dbname'], user=conn_dict['user'], host='/tmp')
    cur = conn.cursor()

    map_query = """
    		SELECT
                    DISTINCT
                    ST_asGEOJSON(wkb_geometry) geometry
                    , sfn.geoid10
                    
                    FROM sf_neighb sfn
                    ;"""

    df = pd.read_sql(map_query, conn)
    df = getrandom_color(df, 'colors.csv')  #now the df also has a hexcolors column. See notebook
    
    def getrandom_color(df, color_file):
        '''takes in a dataframe of gemoetry and geoid, and a list of hex colors
        Creates a new colomn of shape colors. Returns the new dataframe.'''
        #import the colors csv
        cdf = pd.read_csv('colors.csv')
        cdf.dropna(inplace = True)
        #make it a list
        colors = cdf['#9966CC'].tolist() 
        num_col = df.shape[0] 
        df['hexcolors'] = [random.choice(colors) for i in xrange(num_col)]
        return df

    #did this part in ipython notebook. Will it work?!

    def add_properties_geo(row):
    	geoid = row['geoid10']
            hexcolor = row['hexcolors']
    	geo_json = {"type": "Feature", "geometry": json.loads(row['geometry']),  "properties": {'geoid': geoid , 'hexcolor' : hexcolor }}
    	return geo_json

    list_to_export = []	
    for idx, row in df.iterrows():
    	list_to_export.append((add_properties_geo(row)))
    return list_to_export