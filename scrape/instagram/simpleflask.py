
from flask import Flask
from flask import request
app = Flask(__name__)

# OUR HOME PAGE
#============================================

@app.route('/hook/parse-instagram')
def parse_instagram():
    from instagram import client, subscriptions

    mode         = request.values.get('hub.mode')
    challenge    = request.values.get('hub.challenge')
    verify_token = request.values.get('hub.verify_token')
    if challenge: 
        return challenge
    else:
        return 'oh dear'

@app.route('/', methods = ['POST', 'GET'])
def index():

    return '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>NOTHING</title>
    </head>
  <body>
    <!-- page content -->
    <div>
        This is where text or pics or anything your little heart wishes can go.
    </div>
  </body>
</html>
'''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)