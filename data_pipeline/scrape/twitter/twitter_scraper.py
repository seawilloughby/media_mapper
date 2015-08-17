
import media_mapper  #package which contains the API keys for twitter
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import sys
import time
import os

'''code modified from Stream Lister Libray : https://github.com/tweepy/tweepy

Once initialized from the command line, script continues to run until manually stopped by the operator'''

class StdOutListener(StreamListener):

    def __init__(self,file_handle, production = True, stop = 1000):
        self.file_handle = file_handle
        self.production = production
        self.counter = 0
        self.stop = stop
    
    #This function gets called every time a new tweet is received on the stream
    def on_data(self, data):
        #Just write data to one line in the file
        self.file_handle.write(data)
        self.counter += 1

        if self.production == False:
            #Convert the data to a json object (shouldn't do this in production; might slow down and miss tweets)
            j=json.loads(data)

            #See Twitter reference for what fields are included -- https://dev.twitter.com/docs/platform-objects/tweets
            text=j["text"] #The text of the tweet
            print(text) #Print it out
        if self.counter >= self.stop:
            broken

    def on_error(self, status):
        print("ERROR")
        print(status), 'sleeping for one minute'
        time.sleep(60) 


# ###Run Script.
# ###Stream twitter data. Save it to ouputfile --> output.json
# If code is run in an ipython notebook, then sys.argv[1] equals -f.
# This way it knows you are in notebook and want limited streaming 
# Else, assume you are running the entire script.


if sys.argv[1] == '-f':
    production = False
    stop = 4
else:
    production = True
    stop = 1000
    
print 'production is ',production,' stop in: ',stop

try:
    os.mkdir('./results')
except:
    pass



def write_stream(out_file, production = False, stop = 1000, locations = [-122.75,36.8,-121.75,37.8]):
    try:
        #Create a file to store output or add on to previous information.
        fhOut = open(out_file,"a")

        #Create the listener
        l = StdOutListener(fhOut, production = production, stop = stop)
        
        auth = OAuthHandler(media_mapper.keys.TWITTER_CONSUMER_KEY, media_mapper.keys.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(media_mapper.keys.TWITTER_ACCESS_TOKEN, media_mapper.keys.TWITTER_TOKEN_SECRET)

        #Connect to the Twitter stream
        stream = Stream(auth, l, timeout=90)

        #Terms to track
        #stream.filter(track = key_words_list) #track=["oxford","london","wolverhampton"])

        #Alternatively, location box  for geotagged tweets
        stream.filter(locations=locations)#[-122.3145,37.3643,-122.2037,37.4855])

        #stream.filter(locations=[-122.75,36.8,-121.75,37.8])
        #$$c(W 122°31'45"--W 122°20'37"/N 37°48'55"--N 37°36'43")

    except (RuntimeError, TypeError, NameError, KeyboardInterrupt):
        #User pressed ctrl+c -- get ready to exit the program
        #Close the 
        fhOut.close()


if __name__=='__main__':
#     while True:
    if production:
        while True:
            try:
                write_stream('./results/tweets'+str(int(time.time()))+'.json', 
                             production = production, 
                             stop = stop, 
                             locations = [-122.75,36.66,-122.35,37.82])

            except:
                continue  #if something fails, it loops up and trie again
    
    else:  #you are testing in notebook, production = false by default
        try:
            write_stream('./results/tweets'+str(int(time.time()))+'.json', 
                         production = production, 
                         stop = stop, 
                         locations = [-122.75,36.66,-122.35,37.82])
        
        #if the stream is interrupted, restart the script
        except Exception as e:
            print e #continue



