import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import json
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.metrics import silhouette_samples, silhouette_score
import nltk
from ast import literal_eval

import media_mapper as mm #library with custom frequently called functions 



def modified_clean_and_run_kmeans(numberofclusters = 6, run_kmeans = True, plt_silouette = True):
    '''Loads a dataframe, and then calls a a function to run k-means using sklearn. 
    Has Special additions to take out outliers I previously found.
    
    Arguments:
    1) numberofclusters: the number of clusters (k)
    2) run_kmeans: 
        True: If run_kmeans is True, calls the function run_k_means. 
            Returns a three part tuple:
            1) The fit k-means model
			2) a dictionary with geoid as the key, and cluster as the value
			3) a dictionary with the cluster name as the key, and with
				the value as a list of all the geoids belonging to that cluster 
        False: If run_kmeans is False, returns an X feature matrix for kmeans analysis.
    3) plt_silouette:
        True: If plot_silouette is true plots the silouette. 
     '''
    
    #obtain tiwtter data 
    df = mm.pipeline.retrieve_sql_tweets('tweets_with_geoV6')
    #generate datetime columns to help with cleaning
    df = mm.pipeline.transform_timestamp(df, hour = True, DOW = True)
    
    #filter out the outliers identified in previous runs of K-Means.
    #see the 'exploratory kmeans' ipython notebook for details. 
    nogg = df[(df['geoid10']!= '060759803001030')]
    gg = df[(df['geoid10']== '060759803001030')]
    ggdf = pd.concat([nogg, gg[(gg['time'].dt.day > 10) | (gg['time'].dt.month < 8)]])
    #get rid of the other two strange values
    ggdf = ggdf[(ggdf['geoid10']!= '060750201001001')]
    ggdf = ggdf[(ggdf['geoid10']!= '060759804011003')]
    
    df =ggdf
    
    #create a feature matrix for k-means. 
    #this matrix will have time divided into weekends, weekdays
    #and four hour blocks of times over 24 hours 
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


#RUN K-MEANS WITH STRANGE GEOIDS REMOVED 



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

	#save the dictionaries as CSVs
	save_dictionary_as_csv(cluster_dict, 'data/intermediate_data/kmeans/kmeans_clusterdict.csv')
	save_dictionary_as_csv(geoid_dict, 'data/intermediate_data/kmeans/kmeans_geoiddict.csv')

	return kmeans, geoid_dict, cluster_dict

def save_dictionary_as_csv(dictionary, outfile):
	'''saves a python dictionary as a csv to the path specified by outfile. 
	Used to save the unique cluster data generated by K-means.'''

	with open(outfile, 'wb') as f:  
    w = csv.DictWriter(f, dictionary)
    w.writeheader()
    w.writerow(dictionary)


#VISUALIZE K-MEANS GENERATED CLUSTERS

def print_top_cluster_features(df_kmeans, cluster_dict, kmeans_model):
	'''INPUT:   df_kmeans - a dataframe formatted to run k-means analysis
				cluster_dict - a dictionary. the key is the cluster
							the value is a list of geoids that belong in the cluster
				kmeans_model - the fit sklean model 
		OUTPUT: a print out of the top features for each cluster, and a summary
				of the average tweet rate for each cluster in each category. 

	'''

	for cluster, blocks in cluster_dict.iteritems():
	    print cluster,'\n number of neighborhoods: ', len(blocks), \
	    	'\n', df_kmeans[df_kmeans['geoid10'].isin(blocks)].mean(),'\n','\n'
	features = df_kmeans.columns.tolist()

	top_centroids = kmeans_model.cluster_centers_.argsort()[:,-1:-11:-1]
	print "top features for each cluster:"
	for num, centroid in enumerate(top_centroids):
	    print num
	    print centroid
	    print "%d: %s" % (num, ", ".join(features[i] for i in centroid)), '\n'


def plot_clusters(df_kmeans, cluster_dict):
    '''
    INPUT: df_kmeans - a dataframe formated for k-means analysis.
           cluster_dict - a dictionary with each cluster uncovered by
           k means as the key, and a list of associated geoids as the values.
    OUTPUT:  Plots the tweet rate over time for each cluster.'''
    
    num_clust = len(cluster_dict.keys())
    fig, axes = plt.subplots(nrows=numclust/2, ncols=2)
    
    for cluster_id, blocks in cluster_dict.iteritems():
        #set row and column indexes for each subplot
        if cluster_id < num_clust/2: 
            ci = 0 #column index
            ri = cluster_id #row index 
        else:
            ci = 1
            ri = cluster_id - num_clust/2
            
        df_kmeans[df_kmeans['geoid10'].isin(blocks)].plot(kind = 'box', 
            figsize = (20,12), ylim = (0,12),
            ax=axes[ri,ci]).set_title('cluster # ' + str(cluster_id))
   
    plt.tight_layout()
    plt.show()

def create_cluster_geojson(df, geoid_dictionary, outfilename):

	#OBTAIN THE TWITTER TEXT DATA
	df_text = retrieve_and_merge_tweet_data()
	#FUSS WITH DATA TO GET IT FORMATED
	hour_df = mm.pipeline.transform_timestamp(df_text, hour = True)
	hour_df['tweetcnt'] = 1
	#get a total count of tweets
	hdf = hour_df.groupby(['geoid10']).agg(sum).reset_index().drop('id', 1)
	#get a grouped sum of the words
	hour_df_txt = hour_df.groupby(['geoid10'])['text'].apply(lambda x: ','.join(x)).reset_index()
	#merge these two dataframes together
	hdf['tokens'] = hour_df_txt['text']

	#GET THE TOP TEN TOKENS FOR EACH CATEGORY
	top_ten = hdf.tokens.apply(top_tokens, number = 15)
	#make a new column of the top tweets
	hdf['top_ten'] = top_ten
	#merge with shape geometry
	###Retrieve the Shape Files for Each Block:
	geodf = pd.read_csv('data/intermediate_data/sf_only_sql_shapes.csv')
	#format the dataframe
	geodf['geoid10'] = geodf.geoid10.astype('str')
	geodf.drop('Unnamed: 0', axis = 1, inplace = True)
	#set the index as the geoid
	# need to alter the geoid10 column to merge with shape files
	hdf['geoid10'] =hdf['geoid10'].apply(lambda x: x[1:])
	#create a new dataframe 
	hourlydf = pd.merge(geodfm, hdf, on='geoid10', how='outer')
	#fill no tweets with a zero value
	hourlydf.tweetcnt.fillna(0, inplace = True)
	#drop empty hour columns
	hourlydf.dropna(subset = ['hour'], inplace = True)

	#MERGE THE TEXT INFORMATION WITH CLUSTER INFORMATION
	df = df.merge(hourlydf, on='geoid10' )
	colors = ['#FF76BC', '#E1B700', '#91D100', '#00D8CC', '#56C5FF', '#1B58B8','#B81B6C' ,'#15992A' ]

	df['hexcolor'] =df["geoid10"].apply(lambda x:colors[geoid_dictionary[x]]


	#save dataframes with all tokens for later reference
	df.to_pickle('data/intermediate_data/kmeans/df_kmeans.pkl')

	#group then again by cluster 
	#get a mean so can get mean rate for each cluster 
	df['tweetcnt_x'] =df['tweetcnt_x'].astype(float)
	df_cluster = df.groupby(['cluster']).agg(np.mean).reset_index()
	df_cluster_txt = df.groupby(['cluster'])['tokens'].apply(lambda x: ','.join(x)).reset_index()
	df_cluster['tokens'] = df_cluster_txt['tokens']
	df_cluster = df_cluster[['cluster','tweetcnt_x', 'tokens']]

	top_ten = geo_k8_cluster.tokens.apply(top_tokens, number = 40)
	#make a new column of the top tweets
	geo_k8_cluster['top_ten'] = top_ten

	dataframe_to_geojson(geo_k6, outfilename)


def add_properties_geo(row):
    '''Creates the properties geoid, tweetcnt, cluster number'''
    geoid = row['geoid10']
    tweetrate = row['tweetcnt_x']
    hexcolor = row['hexcolor']
    cluster = row['cluster']
    top_ten  = row['top_ten']
    geo_json = {"type": "Feature", "geometry": json.loads(row['geometry']), "properties": {'geoid': geoid ,'tweetrate': tweetrate, 'top_ten': top_ten, 'cluster': cluster , 'hexcolor' : hexcolor}}
    return geo_json

def dataframe_to_geojson(df, outfilename):
    '''Takes in a dataframe with a count, geoid10, and list of tokens. Dumps it into a json geojason file'''
    df['geoid10'] = df['geoid10'].astype('str')
    df["tweetcnt_x"] = df['tweetcnt_x'].astype('str')
    list_to_export = []
    for idx, row in df.iterrows():
        list_to_export.append(add_properties_geo(row))
    with open(outfilename, 'w') as outfile:
        json.dump(list_to_export, outfile)

def retrieve_and_merge_tweet_data():
    '''Retrieves twitter geo data from SQL, and tweet text. 
    Returns the merged dataframe.'''
    #get SF Data From SQL
    df = mm.pipeline.retrieve_sql_tweets('tweets_with_geoV6')
    #get text data from picke
    dftxt = pd.read_csv('data/intermediate_data/json_tweets_in_df_twitokend.csv')
    df = df.set_index('id')
    dftxt = dftxt.set_index('id')
    dfall = df.join(dftxt).reset_index()
    dfall.drop('Unnamed: 0', 1, inplace = True)
    return dfall



def top_tokens(corpus_list, stopwrds=stopwords, number=10):
    '''Takes a list of tokens. Returns the top ten, unless a different number given.'''

    stopwords = nltk.corpus.stopwords.words('english')
	stop.extend(['...',',,',',,,','..', 't','y','(@',')', 'c','i','I','a', \
                '@','.', 'co', 'com','amp', 'via','http','htt','https', '()',']',\
                'S', 'C', 't', 'i', 'a', 'at')
    stop =[unicode(word) for word in stop]
    #Checks to make sure the tokens are in a list, and not a string
    tokens = literal_eval(corpus_list)
    #If there are multiple tweets, flatten the list
    if type(tokens) == tuple:
        tokens =[item for sublist in tokens for item in sublist]  
    tokens = nltk.FreqDist(w.lower() for w in tokens if w not in stopwrds) 
    most_common = tokens.most_common(number)
    top_ten_string = ' '.join([tup[0] for tup in most_common])
    return top_ten_string

if __name__ == '__main__':
    
    #create a feature matrix to run k-means analysis
    df = modified_clean_and_run_kmeans(run_kmeans = False)
    #train a k-means model to generate clusters
	kmeans_object, geoid_dictionary, cluster_dictionary =run_k_means(df, 6) 
	#save the clusters as a geojson file for mapping
	create_cluster_geojson (df,geoid_dictionary, outfilename = 'map_making/clusters/data/clustergeo_k6.json')

