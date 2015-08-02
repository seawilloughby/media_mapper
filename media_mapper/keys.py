'''
Instructions for using keys:

BASH:
$export TWITTER_CONSUMER_KEY=whatyourkeyis

IPYTHON
IN[] import os
IN[] TWITTER_CONSUMER_KEY = os.environ['TWITTER_CUSUMER_KEY']


YOU MAY HAVE TO SOURCE IT WHEN YOU START BASH
go to root toor 
$ cd
$ source .keys/make_keys.sh   

THIS IS ASSUMING THAT THE expor TWITTER_CONSUMER_KEY=whatyourkeyis
ect is al lin that make_keys.sh file. This just re-runs it on bash so it is 
initailized.


'''

import os

#PYTHON
try:
	TWITTER_CONSUMER_KEY = os.environ['TWITTER_CUSUMER_KEY']

except:
	print 'TWITTER_CONSUMER_KEY not found.'

#INSTAGRAM
try:
	INSTAGRAM_CLIENT_ID = os.environ['INSTAGRAM_CLIENT_ID']

except:
	print 'INSTAGRAM_CLIENT_ID not found.'

try:
	INSTAGRAM_CLIENT_SECRET = os.environ['INSTAGRAM_CLIENT_SECRET']

except:
	print 'INSTAGRAM_CLIENT_SECRET not found.'


try:
	INSTAGRAM_ACCESS_TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']

except:
	print 'INSTAGRAM_ACCESS_TOKEN not found.'

#FLICKER
try:
	FLICKR_API_KEY = os.environ['FLICKR_API_KEY']

except:
	print 'FLICKR_API_KEY not found.'

try:
	FLICKR_API_SECRET = os.environ['FLICKR_API_SECRET']

except:
	print 'FLICKR_API_SECRET not found.'


