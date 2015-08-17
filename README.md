media_mapper
=====================================================================================================

Geographical localization of twitter activity within the blocks of San Francisco,

###Motiviation & Inspiration

Where is everybody? In a big city, it can be difficult find this out. Websearches may describe 'shopping districts' or parks, but its often hard to determine where popular parks, street festivals, or other various congregations of people are located withoout painstakingly visiting every block by foot or car. 

[Twitter](https://dev.twitter.com/overview/documentation) represents a rich sorce of potential signal: thousands of users volunteer information about thier location and potentially information regarding thier whereabouts.

In order to answer 1) where are people 2) when are they there and 3) what they doing, I mapped the frequency of tweets and message content across the neighborhoods of San Francisco. By breaking down analysis to every block across the city, I was able to pick out block-specific features, such as popular barks, or coffee shops, that may have gotten lost in the noise of a larger neighborhood region.  

Browse my interactive maps yourself at  [chattermapper.info](http://chattermapper.info/)


###Data Flow Chart
<img align="center" src="data_pipeline/flowchart.png" height="575" width="1400">

Links
-----
[App](docs/md/installation.md) Contains the code for the maps via flask on chattermapper.info

[Scripts](docs/md/versioning.md) Used for setting up EC2 instances on AWS.

[data_pipeline](docs/md/documentation.md)


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
