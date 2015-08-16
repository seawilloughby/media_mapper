import pandas as pd
import media_mapper as mm
import numpy as np
from sklearn.cluster import KMeans
import json
import matplotlib.pyplot as plt
import matplotlib.cm as cm
%matplotlib inline
from sklearn.metrics import silhouette_samples, silhouette_score
import nltk
from ast import literal_eval


#CREATE A FEATURE MATRIX FOR K MEANS

def tweet_rate_by_hour(df, dow = False):
    '''
    INPUT: Dataframe with unqiue entries for tweets, and a datetime column. Drops the id column
    
    Calculates tweets rate per hour.

    OUTPUT: If dow is false, will return a dataframe grouped only by hour. 
            If dow is true, will return a dataframe grouped by weekend(0) or weekday (1).
    '''
    #column of ones serves as a counter for number of tweets during group bys
    df['twt_cnt'] = 1
    #group by hour, so we have the total tweets for every hour
    df = df.groupby(['geoid10', 'date', 'hour']).agg(np.sum).reset_index().drop('id', 1)
    #At this point, the twt_count is the number of tweets for every hour 
    df['twt_rate'] = df['twt_cnt']
    
    if dow == False:
        #groupby geoid and hour to get the average rate for every hour
        df = df.groupby(['geoid10', 'hour']).agg(np.mean).reset_index()
        df.drop('DOW', 1, inplace = True)
        df.drop('twt_cnt', 1, inplace = True )  
        df['hr_bin'] = pd.cut(df.hour, bins = 5, labels = ['latenight', 'dawn','morning','afternoon','evening'])
        df = df.groupby(['geoid10', 'hr_bin']).agg(np.mean).reset_index().drop('hour', 1)
   
    else: dow == True:
        #group by date for the average tweet rate every day
        df = df.groupby(['geoid10', 'date', 'DOW']).agg(np.mean).reset_index()
        df.drop('hour',1, inplace = True)
        df.drop('twt_cnt',1, inplace = True)    
        df['wknd']=df['DOW'].where(df['DOW'] > 5) 
        df['wkday'] = df['wknd'].isnull().astype(int)
        df.drop('DOW', 1, inplace = True)
        df.drop('wknd', 1, inplace = True)
        #final groupby to get an average count for week days or weekends 
        df = df.groupby(['geoid10', 'wkday']).agg(np.mean).reset_index()
    
    return df


def pivot_table(df, timevariable, column_prefix ):
    '''
    INPUT: Dataframe with three columns: Geoid, tweet rate, and a time variable..
           The argument column_prefix, is used to name the time variable columns.
    OUTPUT: Pivots the table to create a dataframe with geoid as the index, 
            and the time variable as the features.
    '''
    df = df.pivot(index = 'geoid10', columns = timevariable)
    df = df.reset_index(1)
    df = df.rename(columns = lambda x: column_prefix + str(x))
    df.columns = df.columns.droplevel()
    #rename the geoid column 
    df['geoid10'] = df['hr_bin']
    return df

#RUN K MEANS, TAKE OUT STRANGE POINTS


def modified_clean_and_run_kmeans(df, numberofclusters = 6, run_kmeans = True, plt_silouette = True):
    '''Cleans a dataframe, and then calls a a function to run kmeans with sklearn. 
    Has Special additions to take out outliers I previously found.
    Arguments:
    1) df: A dataframe with a timestamp, geolabel, and tweet id column. 
    2) numberofclusters: k for Kmeans
    3) run_kmeans: 
        True: If run_kmeans is True, calls the function run_k_means. 
            Returns a three part tuple with the kmeans model, and two dictionaries of geoides and clusters.
        False: If run_kmeans is False, returns an X feature matrix for kmeans analysis.
    4) plt_silouette:
        True: If plot_silouette is true plots the silouette. 
     '''
    #get datetime columns to help with cleaning
    df =mm.pipeline.transform_timestamp(df, hour = True, DOW = True)
    
    #filter out the outliers
    #get rid of golden gate park during the music festival
    nogg = df[(df['geoid10']!= '060759803001030')]
    gg = df[(df['geoid10']== '060759803001030')]
    ggdf = pd.concat([nogg, gg[(gg['time'].dt.day > 10) | (gg['time'].dt.month < 8)]])
    #get rid of the other two strange values
    ggdf = ggdf[(ggdf['geoid10']!= '060750201001001')]
    ggdf = ggdf[(ggdf['geoid10']!= '060759804011003')]
    
    df =ggdf
    
    dfwk = tweet_rate_by_hour(df, dow= True)
    #pivot table so DOW is columns
    dfwk = pivot_table(dfwk, 'wkday', column_prefix = 'wkday_')
    #get tweet rate by hour
    dfhr = tweet_rate_by_hour(df)
    #pivot table so time of day is columns
    dfhr = pivot_table(dfhr, 'hr_bin', column_prefix = 'hrbin_')
    dfkmeans = pd.merge(dfhr, dfwk, left_on = 'geoid10', right_on = 'wkday_').drop('wkday_', 1)
    #reorder the columns 
    dfkmeans = dfkmeans[['geoid10','wkday_0','wkday_1','hrbin_morning','hrbin_afternoon','hrbin_evening',
     'hrbin_latenight','hrbin_dawn']]
    #fill missing values with zeroes 
    dfkmeans.fillna(0, inplace = True)
    if run_kmeans == True:
        kmeans, geoid_dict, cluster_dict = run_k_means(dfkmeans, numberofclusters, plot_silouette = plt_silouette)
        for k, v in cluster_dict.iteritems():
            print k,'\n number of neighborhoods: ', len(v), '\n', dfkmeans[dfkmeans['geoid10'].isin(v)].mean(),'\n','\n'
        return kmeans, geoid_dict, cluster_dict, dfkmeans 
    else:
        return dfkmeans

def run_k_means(df, numberclusters, geoidlabel ='geoid10', plot_silouette = True):
	'''Uses sklearn to run kmeans. 
	
	INPUT:
	1) df: A dataframe with a geoid column
	2) geoidlabel: the label of the geoid column. 
	3) plot_silouette: whether or not to plot the silouettes of each cluster
	
	OUTPUT: Returns a three part tuple:
	1) the kmeans sklearn model 
	2) a dictionary with geoids as the key, and the cluster as the value
	3) a dictionary with clusters as the key, and a list of related geoids as the value'''

	#Use K means to cluster the dataset. 
	x = df[['wkday_0','wkday_1','hrbin_morning',
	        'hrbin_afternoon','hrbin_evening',
	         'hrbin_latenight','hrbin_dawn']].values
	kmeans = KMeans(n_clusters = numberclusters)
	kmeans.fit(X = x )
	features = df.columns.tolist()[1:]
	geoids = df[geoidlabel]

	#store values in a dictionary
	geoid_dict = defaultdict(int)
	cluster_dict = defaultdict(list)

	#Transforms x into a cluster-distance space. 
	#In this array, each column is a cluster with the value of the distance from 
	#a given neighborhood block (geoid) in each row. 
	#This function returns the cluster belonging to each neighborhood block:
		#the cluster with the smallest distance value 
	assigned_cluster = kmeans.transform(x).argmin(axis=1)


	for i in range(kmeans.n_clusters):
	    cluster = np.arange(0, x.shape[0])[assigned_cluster==i]
	    geoids = [df.ix[geoindx]['hrbin_'] for geoindx in cluster]
	    print len(geoids), 'cluster #', i
	    #make a dictionary with cluster as the key, and geoids as the list
	    cluster_dict[i] = geoids
	    #second dictionary to quickly look up what cluster each geoid belongs to
	    for geo in geoids:
	        geoid_dict[geo] = i
	if  plot_silouette == True:
	    plot_cluster_silouette_values(X, assigned_cluster, n_clusters)
	return kmeans, geoid_dict, cluster_dict


#PLOT K MEANS


def add_properties_geo(row):
    '''Creates the properties geoid, tweetcnt, cluster number'''
    geoid = row['geoid10']
    tweetrate = row['tweetcnt']
    hexcolor = row['hexcolor']
    cluster = row['cluster']
    geo_json = {"type": "Feature", "geometry": json.loads(row['geometry']), "properties": {'geoid': geoid ,'tweetrate': tweetrate, 'cluster': cluster , 'hexcolor' : hexcolor}}
    return geo_json

def dataframe_to_geojson(df, outfilename):
    '''Takes in a dataframe with a count, geoid10, and list of tokens. Dumps it into a json geojason file'''
    df['geoid10'] = df['geoid10'].astype('str')
    df["tweetcnt"] = df['tweetcnt'].astype('str')
    list_to_export = []
    for idx, row in df.iterrows():
        list_to_export.append(add_properties_geo(row))
    with open(outfilename, 'w') as outfile:
        json.dump(list_to_export, outfile)


if __name__ == '__main__':
    pass 
