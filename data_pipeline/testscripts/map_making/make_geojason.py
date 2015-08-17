
import pandas as pd
import json
import psycopg2
import random


def collect_sf_shapes():
    """Connects to database to retreive neighborhood coordinates. Returns a Dataframe"""
    
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
    return df


def add_properties_geo(row):
	geoid = row['geoid10']
        hexcolor = row['hexcolors']
	geo_json = {"type": "Feature", "geometry": json.loads(row['geometry']),  "properties": {'geoid': geoid , 'hexcolor' : hexcolor }}
	return geo_json

def dataframe_to_geojson(df, outfilename):
    '''Takes in a dataframe with a count and geoid10. Dumps it into a json geojason file'''
    df['geoid10'] = df['geoid10'].astype('str')
    df["count"] = df['count'].astype('str')
    list_to_export = []
    for idx, row in test.iterrows():
        imgvalue = 'http://i357.photobucket.com/albums/oo11/clwillerbee/' + str(idx) + '.png'
        list_to_export.append(add_properties_geo(row, imgvalue))
    with open(outfilename, 'w') as outfile:
        json.dump(list_to_export, outfile)