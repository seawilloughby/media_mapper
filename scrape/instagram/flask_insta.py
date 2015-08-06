from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth, OAuthException
import media_mapper.keys

FACEBOOK_APP_ID = media_mapper.keys.INSTAGRAM_CLIENT_ID
FACEBOOK_APP_SECRET = media_mapper.keys.INSTAGRAM_CLIENT_SECRET


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

# facebook = oauth.remote_app(
#     'facebook',
#     consumer_key=FACEBOOK_APP_ID,
#     consumer_secret=FACEBOOK_APP_SECRET,
#     request_token_params={'scope': 'email'},
#     base_url='https://api.instagram.com/',
#     request_token_url=None,
#     access_token_url='/oauth/access_token',
#     access_token_method='GET',
#     authorize_url='https://api.instagram.com/oauth/authorize'
# )

# Instagram

#from app.config import INSTAGRAM_APP_KEY, INSTAGRAM_APP_SECRET

instagram_oauth = oauth.remote_app(
    'instagram',
    consumer_key=media_mapper.keys.INSTAGRAM_CLIENT_ID,#INSTAGRAM_APP_KEY, 
    consumer_secret=media_mapper.keys.INSTAGRAM_CLIENT_SECRET,#INSTAGRAM_APP_SECRET,
    base_url='https://api.instagram.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.instagram.com/oauth/access_token',
    authorize_url='https://api.instagram.com/oauth/authorize',
)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    callback = url_for(
        'instagram_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return instagram_oauth.authorize(callback=callback)


@app.route('/login/authorized')
def instagram_authorized():
    resp = instagram_oauth.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = instagram_oauth.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))


@instagram_oauth.tokengetter
def get_instagram_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)