
import pandas as pd
import media_mapper as mm
import numpy as np

def tweet_rate_by_hour(df, dow = False):
    '''Calculates tweets per hour from a dataframe with unqiue entries for tweets, 
    and a datetime column. Drops the id column.
    If dow is false, will return a dataframe grouped only by hour. 
    If dow is true, will return a dataframe grouped by weekend(0) or weekday (1).'''
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
        return df
    if dow == True:
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
    '''Takes a dataframe with three columns: Geoid, measurement of tweets, and time variable.
    Takes an argument of a column_prefix, which is used to name the new time variable columns.
    Pivots the table to create a dataframe with geoid as the index, and the time variable as the features.
    '''
    df = df.pivot(index = 'geoid10', columns = timevariable)
    df = df.reset_index(1)
    df = df.rename(columns = lambda x: column_prefix + str(x))
    df.columns = df.columns.droplevel()
    return df

def create_feature_matrix_tweetrate():
	'''Retrieves twitter data from the postgres database. Returns features and X as two variables. 
	Features is a matrix with geoid as the rows. The columns are binned groups of time, and weekend vs weekday variables.
	The values are the average tweet rate per hour for each time subset.'''

	#retrieve tweet data from database
	df = mm.pipeline.retrieve_sql_tweets('tweets_with_geoV6')
	#obtain hour and day of week variables
	df  =mm.pipeline.transform_timestamp(df, hour = True, DOW = True)

	#GET TWEET RATE FOR WEEEKND AND WEEKDAY
	df_tr_wkdy = tweet_rate_by_hour(df, dow= True)
	#pivot table so DOW is columns
	df_tr_wkdy = pivot_table(df_tr_wkdy, 'wkday', column_prefix = 'wkd_')

	#GET TWEET RATE BASED ON TIMES OF DAY 
	df_tr_hr = tweet_rate_by_hour(df)
	#pivot table so time of day is columns
	df_tr_hr = pivot_table(df_tr_hr, 'hr_bin', column_prefix = 'hrbin_')

	#create one matrix of tweet rate for different times of day and weekend vs weekday
	dfk = pd.merge(df_tr_hr, df_tr_wkdy, left_on = 'hrbin_', right_on = 'wkd_').drop('wkd_', 1)
	#fill missing values with zeroes 
	dfk.fillna(0, inplace = True)

	geoids = df_tr_hr['hrbin_'].values
	feature_names =['hrbin_afternoon','hrbin_dawn',	'hrbin_evening', 'hrbin_latenight', 'hrbin_morning', 'wkd_0', 'wkd_1']

	X = dfk[['hrbin_afternoon','hrbin_dawn',
	 'hrbin_evening',
	 'hrbin_latenight',
	 'hrbin_morning',
	 'wkd_0',
	 'wkd_1']].values

	return (geoids, feature_names, X)ß

if __name__ == "__main__":
	pass
	#