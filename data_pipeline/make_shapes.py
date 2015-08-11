import pandas as pd
import psycopg2

def retrieve_shapefiles(outfile = 'data/sf_only_sql_shapes.csv'):
    '''Retreives SF neighborhood shapefiles from the SQL database. Saves the dataframe to the output folder'''
    
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