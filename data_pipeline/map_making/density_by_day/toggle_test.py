from flask import Flask
from flask import request
#from send_example_sf import send_example_json
from flask import render_template
import json
import psycopg2
import media_mapper.keys
#don't forget to import api key later

app = Flask(__name__)

api_key = media_mapper.keys.MAPBOX_API_KEY

#list_to_features = send_example_json()  #drxt: send it out a list of features
#sf_cong_113 = json.dumps(list_to_features) #drxt: convert this to a json object.

in_file = open('data/afternoon.json','r')
afternoon = json.load(in_file)
in_file.close()
afternoon = json.dumps(afternoon)

in_file = open('data/dawn.json','r')
dawn = json.load(in_file)
in_file.close()
dawn = json.dumps(dawn)

in_file = open('data/evening.json','r')
evening = json.load(in_file)
in_file.close()
evening = json.dumps(evening)

in_file = open('data/latenight.json','r')
latenight = json.load(in_file)
in_file.close()
latenight = json.dumps(latenight)

in_file = open('data/morning.json','r')
morning = json.load(in_file)
in_file.close()
morning = json.dumps(morning)

@app.route('/')  
def text():
	return ''' '''
@app.route('/afternoon')  
def map1():
    ## Have the home page be a place to input a file or paste the lat/long (address if ambitious)
    return render_template("afternoon.html", sf_cong_113 = afternoon, api_key = api_key)

@app.route('/dawn')  
def map2():
    ## Have the home page be a place to input a file or paste the lat/long (address if ambitious)
    return render_template("dawn.html", sf_cong_113 = dawn, api_key = api_key)

@app.route('/evening')  
def map3():
    ## Have the home page be a place to input a file or paste the lat/long (address if ambitious)
    return render_template("evening.html", sf_cong_113 = evening, api_key = api_key)


@app.route('/latenight')  
def map4():
    ## Have the home page be a place to input a file or paste the lat/long (address if ambitious)
    return render_template("latenight.html", sf_cong_113 = latenight, api_key = api_key)

@app.route('/morning')  
def map5():
    ## Have the home page be a place to input a file or paste the lat/long (address if ambitious)
    return render_template("morning.html", sf_cong_113 = afternoon, api_key = api_key)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6969, debug=True)
