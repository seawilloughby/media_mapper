from flask import Flask
from flask import request
#from send_example_sf import send_example_json
from flask import render_template
import json
import psycopg2
import media_mapper.keys

# create the application object
app = Flask(__name__)
api_key = media_mapper.keys.MAPBOX_API_KEY

#load data from kmeans clustering
in_file = open('data/kmeans6_geo.json','r')
kmeans = json.load(in_file)
in_file.close()
kmeans = json.dumps(kmeans)

#load data from overal tweet density
in_file = open('data/wordcloud.json','r')
wordcld = json.load(in_file)
in_file.close()
wordcld = json.dumps(wordcld)

in_file = open('data/time/weekend.json','r')
weekend = json.load(in_file)
in_file.close()
weekend = json.dumps(weekend)

in_file = open('data/time/weekday.json','r')
weekday = json.load(in_file)
in_file.close()
weekday = json.dumps(weekday)

# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('index.html')   #

@app.route('/index.html')
def index():
	return home()

@app.route('/post.html')
def first_post():
	return render_template('post.html' , kmeans = kmeans, api_key = api_key )

@app.route('/contact.html')
def contact():
	return render_template('contact.html', weekday = weekend, api_key = api_key )  

@app.route('/about.html')
def about():
	return render_template('about.html', wordcld = wordcld, api_key = api_key) 


app.route('/test.html')
def test():
	return render_template('test.html') 

# @app.route('/marketing')
# def marketing():
# 	return render_template('marketing.html')

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
