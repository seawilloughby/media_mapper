media_mapper
=====================================================================================================

Geographical localization of twitter activity within the blocks of San Francisco.

###Motiviation & Inspiration

Where is everybody? In a big city, it can be difficult find this out. Websearches may describe 'shopping districts' or parks, but its often hard to determine where popular parks, street festivals, or other various congregations of people are located withoout painstakingly visiting every block by foot or car. 

[Twitter](https://dev.twitter.com/overview/documentation) represents a rich sorce of potential signal: thousands of users volunteer information about thier location and potentially information regarding thier whereabouts.

In order to answer 1) where are people 2) when are they there and 3) what they doing, I mapped the frequency of tweets and message content across the neighborhoods of San Francisco. By breaking down analysis to every block across the city, I was able to pick out block-specific features, such as popular barks, or coffee shops, that may have gotten lost in the noise of a larger neighborhood region.  

Browse my interactive maps yourself at  [chattermapper.info](http://chattermapper.info/)


###Data Flow Chart
<img align="center" src="data_pipeline/flowchart.png" height="575" width="1400">

###Data Collection
####Twitter Data 
The dataset consisted of 16 days of twitter data during the last week of July and first week of August. I used the python library [Tweepy](https://github.com/tweepy/tweepy) and an [Amazon EC2](https://aws.amazon.com/ec2/) to obtain live data form the [Twitter API](https://dev.twitter.com). From this collection, I obtained 95,840 tweets. 

####United States 2010 Census Data
I obtained shape files for the neighborhood blocks of San Francisco. I wanted a high resolution data set so that I could detect events block by block. My goal was to have a map that could potentially differentiate between local buisnesses and parks, and so I wanted to break the geography down into small sections.


###Data Analysis 

[PostGIS](http://postgis.net) allows for convenient processing of shape files with Postgress. I used PostGIS to match each tweet with its corresponding block, and retrieve the geographical coordinates of that block for mapping. 

Using the shape of blocks also allowed me to bin tweets together in similar regions. For every tweet, I had a precise latitude and longitude. Using shape files allowed me to toss these discrete points into a larger land mass. Because I am interested in text analysis of tweets, binning tweets into larger neighborhoods makes it easier to create a larger corpus of words to analyze for each neighborhood, as opposted to having to consider every tweet individually. 

####Tweet Density
I wanted to map where people are most active in San Francisco. High density of tweets could suggest areas of interest.
I calculated the average number of tweets per hour for each san francisco neighborhood.

I further binned the data into different chunks of the day, and into weekday or weekend activity.
I made this decision by plotting the frequency of tweets over time for all of san francisco, and for a couple of randomly selected neighborhoods. There was quite a bit of variety in tweet activity, but there were clear daily and weekly cycles, as would be expcted based on the activities of humans. 

####Unsupervised Clustering: K-Means
When I looked at tweet frequency over time, it was clear that for some blocks, there were fluxuations based on time of day, and day of week. Intuitively, this makes sense based on the activity patterns of humans, and the fact that I am looking at a variety of neighborhoods. I used K-means to cluster neighborhood blocks based on thier activity. My hypothesis was that this would group blocks with high and low activity, and diffentiate blocks with high weekend activity, such as at a city park vs blocks with high weekday activity, such as an office. 

K-means can suffer from the problem of high dimensionality with two many features. In my data set, blocks with low activity had a fairly low number of tweets overall. In fact, when time is broken into even rough chunks of weekend vs weekday, many neighborhoods don't have any twitter activity. To limit the number of features, and allow for a sizable number of data to do analysis, I created a feature matrix of the average tweet per hour for every neighborhood on the weekend, week day, and at five major intervals of time throughout the day.

On my first pass of K-Means with an N of 6 (a random number to begin), three clusters appeared with only one block group! These three blocks were completely outliers from the rest of the blocks. All three blocks had dramatically higher activity than any other block (30 - 80 tweets/hour vs common values of 1-10 tweets/hour). Two of these blocks were at odd locations that did not make geographical sense. One was off in a tiny island in the ocean, and the other was approximately in the center of san francisco, in a very small block in the Tenderloin. The most common words associated with the blocks included, 'San Francisco', 'Jobs', 'Hiring'. I left these two blocks out of all of my analysis, as I think they represent mislabeling of latitude and longitude.  The third outlier was golden gate park. This was very exciting to me. During the weekend of the analysis, a giant three day music festival occured at this neighborhood block. K-Means was able to detect the abnormal tweeting activity, and assigned the event to its own cluster!

After this first analysis, I removed these three outliers from my dataset, and used silhouette analysis to select the number of clusters. I varied the number of clusters from 2 to 12, and plotting the mean silhouette score of the clusters. I chose 6 as it led to highest average silhouette coefficient values, while maintainign a relatively low number of clusters. I was worried about overfitting my data to my test set, because it was relatively small. 

I plotted the average tweet rate for each cluster to assess the features K-mean uncovered. 
Different blocks varied both in tweet rate, and in specific activity during times of day, and weekend vs weekday. I mapped the clusters, and assigned descriptive labels to thier activity pattern. This is visualized in the app. 


####Tweet Content 
I used [TweetMotif](https://github.com/brendano/tweetmotif) to break tweets into tokens. This library is based off of of some interesting natural language processing being done by http://www.ark.cs.cmu.edu/TweetNLP/. I also used [Natural Language Toolkit](www.nltk.org) to remove stopwords (frequent words in the english language. 

####Word Frequency
I created a wordcloud that contained the most frequent words for each neighborhood.  
In order to assess the success of this model, I looked at the resulting word cloud for known major neighborhoods. Excitingly, this was sufficent to pull out local areas of interest across San Francisco. Many of the tourists places in San Franciso (the sports park, the Ferry Building, Coit Tower, Lombardo Street), appear predomintely in the word cloud at their location. Popular local businesses such as Blue Bottle Coffee and the Craftsman & Wolves also appear. 

However, many of the word clouds do not tell a coherent narrative about thier block. There is a wide variety of additional feature engineering to do with tweets. Many of the predominat tweets are about grafitti clean up, and ticketing. I suspect these tweets may be due to frequent tweeting from a minority of twitter users. Improvements in my model will defnitely include weighting tweets so that every user has an equal vote toward what words make it into the top features. I hypothesize that this will clean up some of the noise in my word clouds.

####Preliminary Unsupervised Clustering
I performed preliminary unsupervised clustering using non-negative matrix factorization (NMF). I created a feature matrix of words using TF-IDF, with all the tweets from each neighborhood block as different documents. This technique pulled out major themes in tweet content: Tweets with words about the outdoors,  local buisnesses and hiring/job opportunities. The largest group of latent features that NMF pulled out were tweets I would mark as not relevant to local events (dsicussed above). 

I mapped the localtions of the clusters NMF unconvered. While the map did highlight some interesting neighborhoods, I did not find a fetching story or pattern from this first pass of analysis. For instance, NMF only found three blocks in the 'park' category. However, San Francisco has at least 20 parks. More feature engineering with the various tools of natural language processing is definitely needed to improve the model. 

###Data Visulization

I visualized the frequency of tweets in each neighborhood, and the most frequency words in each neighborhood using [Mapbox](http://bids.github.io/2015-06-04-berkeley/testing/), which has nice integration with GIS shapefiles to create choropleths. 

###Future Goals

There are a lot of exciting ways I could improve and extend my model.

Additional twitter data is still being streamed, but has yet to be incorpoated into the model. With increased data, I will have better resolution in some of the quieter neighborhoods. More longitudinal data coudl also aid in a stable model of what normal actiivty is for each neighborhood.  Future analysis could utilize time series analysis to predict future activity. This could be used as a way to detect events, as activity should be substantially larger than normal (such as in Golden Gate Park during the OutsideLands music festival).

I think that the content of tweets could be as equally informative about events as changes in tweet frequency. Future work could include both similarity of tweets within a corpus over time, and changes in content of tweets over time as a way to detect events. 

Another quick extension of my webapp will be to include real-time updating. This could be an fantastic visual way to see novel events in real time. 

If you look at /scrape, I have some code written for scraping instagram API. I have been streaming instagram posts, but have not yet included the text into my model.  I want to encorporate content from instagram to improve my abillity to detect event content in specific neighborhoods. My hypothesis is that instagram will have more location-specific language than twitter, because of the nature of the application.


Links
-----
[App](docs/md/installation.md) Contains the code for the maps via flask on chattermapper.info

[scripts](docs/md/versioning.md) Used for setting up EC2 instances on AWS.

[data_pipeline](/data_pipeline)


Toolkits &  Credits 
---------------

- [United States Census](https://www.census.gov/geo/maps-data/data/cbf/cbf_tracts.html) - California cartographic bonudary shapefiles from the 2010 Census.
- [PostgreSQL](http://www.postgresql.org) Chosen for its support for geographical objects via the spatial database extender [PostGIS](http://postgis.net)
- [Mapbox](http://bids.github.io/2015-06-04-berkeley/testing/) A great tool for mapping data.


- [Tweepy](https://github.com/tweepy/tweepy) A python library specialized in assisting streaming data from the Twitter Api. 

- [TweetMotif](https://github.com/brendano/tweetmotif) A python wrapper for twitter-specific tokenization. 


- [scikit-learn](http://bids.github.io/2015-06-04-berkeley/testing/08-ci.html) A fantastic resource for python machine learning libraries. 

- [Natural Language Toolkit](www.nltk.org) An incrediably useful python library for natural language processing. 

- [Word_Cloud](https://github.com/amueller/word_cloud) An easy to use python library for generating word clouds.


- [AWS](https://aws.amazon.com/) Provides great support for website hosting, and remote computing. 
- [Stencil](https://github.com/jshiv/stencil) Template for setting up a general python package.
- [Bootstrap](http://getbootstrap.com/) Templates for setting up webpages. 


- [Zipfian Academy, Galvanize](http://www.zipfianacademy.com/) An amazing place for resources, learning, and mentorship. Crucial for this project's existance.




- Thanks to Zein Tawil and Kevin DelRosso who were essential resources for setting up PostGIS and Mapbox.

Setup
-----

[Bash](https://github.com/barryclark/bashstrap)

[Environment](https://github.com/jshiv/media_mapper/blob/master/scripts/setup_env.sh)