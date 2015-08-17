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

in_file = open('data/afternoon.json','r')
sf_cong_113 = json.load(in_file)
in_file.close()

sf_cong_113 = json.dumps(sf_cong_113)

# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('index.html', sf_cong_113 = sf_cong_113, api_key = api_key)   # render a template
	
@app.route('/index.html')
def index():
	return home()


if __name__ == '__main__':
    app.run(debug=True)
