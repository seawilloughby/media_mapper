from flask import Flask
from flask import request
#from send_example_sf import send_example_json
from flask import render_template
import json
import psycopg2
#don't forget to import api key later

app = Flask(__name__)

# api_key = 'sk.eyJ1IjoiZHJ4dHdpbG9iIiwiYSI6ImZkY2Y2ZDhjZmJlYmRmZDEzMWYyMWQ2ZDcwMjA1OGIyIn0.MoXwl6VNoTW2Cw8VeZWY7Q'

#list_to_features = send_example_json()  #drxt: send it out a list of features
#sf_cong_113 = json.dumps(list_to_features) #drxt: convert this to a json object.

in_file = open('data/twet_count_geo.json','r')
sf_cong_113 = json.load(in_file)
in_file.close()

sf_cong_113 = json.dumps(sf_cong_113)

@app.route('/')  
def map():
    ## Have the home page be a place to input a file or paste the lat/long (address if ambitious)
    return render_template("testing_maps.html", sf_cong_113 = sf_cong_113)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6979, debug=True)