
# coding: utf-8

# ###install main packages:

# In[22]:

import media_mapper 
import json
import sys
import time
import os
import instagram
from instagram.client import InstagramAPI
from instagram import subscriptions
from collections import defaultdict


# In[23]:

import time
import calendar
import ast
from time import sleep


# In[24]:

#if running in notebook, just do a few.
#else, do a bunch.

if sys.argv[1] == '-f':
    production = False

else:
    production = True

    
print 'production is ',production

try:
    os.mkdir('./results')
except:
    pass


# In[28]:

def write_stream(out_file, production = False, iterations = 61):

    #Create a file to store output. "a" means append (add on to previous file)
    fhOut = open(out_file,"a")

    #authorize 
    access_token = media_mapper.keys.INSTAGRAM_ACCESS_TOKEN
    client_secret = media_mapper.keys.INSTAGRAM_CLIENT_SECRET
    api = InstagramAPI(access_token=access_token, client_secret=client_secret)

    #set time limit for the current time
    time_marker = calendar.timegm(time.gmtime())
    begin_time = time_marker
    sleep(10) #sleep ten seconds so some instagrams have some time to come in

    #query for a new batch of 20 photos
    
    for i in xrange(iterations): #make sure that it only loops 60 times 
        media_search = api.media_search(lat="37.7833",lng="-122.4167",distance=5000, min_timestamp=time_marker)
   
        #get all the metadata in a list
        instagram_list = instagram_metadata(media_search, time_marker)
        [json.dump(item, fhOut, indent = 1) for item in instagram_list]
        time_marker = calendar.timegm(time.gmtime()) 
    
    #check to make sure that this cycle has taken an hour for request limits
    end_time = calendar.timegm(time.gmtime()) 
    seconds_left = 3600 -(begin_time-end_time) #find out how much time has passed
    if seconds_left > 0:  #if an hour hasn't passed, sleep so I don't overrequest
        sleep(seconds_left)
    fhOut.close()

    #make a timestamp so only photos in the future from now will be found

def instagram_metadata(media_search, time_marker):
    '''Takes in a list of instagram media tags. 
    Iterates through all of them, and extracts relevant information. Comments, time, ect'''
    instagram_list = []
                                        
    for media in media_search:
        #The info from each instragram is turned into a dictionary
        #There will be a list of dictionaries. 
        name = media
        name = 'insgstr' + str(name)[7:]
        instadic = defaultdict(str)
        instadic['id']= name  #give each item a key which is the name
        if media.caption:
            instadic['caption'] = str(media.caption)[8:] #the text we want
        if media.created_time:
            instadic['created_time'] = str(media.created_time)  #a date and time
        if media.location:
            loc= media.location.point
            instadic['loc'] = ast.literal_eval(str(loc)[7:])  #a tuple of location
        if media.tags:
            instadic['tags'] = str(media.tags)  
        instagram_list.append(instadic)
    return instagram_list
    

if __name__=='__main__':
#     while True:
    if production:
        while True:
            try:
                write_stream('./results/instagram'+str(int(time.time()))+'.json', 
                             production = production)

            except:
                continue  #if something fails, try again! 
    
    else:  #you are testing in notebook, production = false by default
        try:
            write_stream('./results/instagram'+str(int(time.time()))+'.json', 
                         production = production, iterations = 1)
    
        except Exception as e:
            print e#continue


# In[ ]:



