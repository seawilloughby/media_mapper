#scp means remote copy, or transfer files. 
#point it at files on the server, tell it where to put them locally
#put in whatever path you want. 

scp -i ~/.aws/rootkey1.pem ubuntu@ec2-52-2-75-46.compute-1.amazonaws.com:/home/ubuntu/playGround/twitter_scraper/results/tweets.json ./tmp/