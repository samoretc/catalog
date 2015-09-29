from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Category, User
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import pdb

app = Flask(__name__)

CLIENT_ID = json.loads(
	open('client_secret.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Catalog"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()





@app.route('/')
def homePage(): 
	categories = session.query(Category).all()
	items =      session.query(Item).all()
	if 'username' not in login_session:
		return render_template('public_index.html', categories=categories, items = items)
	else: 
		return render_template('private_index.html', categories=categories, items=items, login_session=login_session )

@app.route('/login')
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) 
		for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE = state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
		   % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Store the access token in the session for later use.
	login_session['credentials'] = credentials
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']
	
	#see if user exists, if it doesn't make a new one 
	user_id = getUserId(login_session['email'])
	if not user_id: 
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h5>Welcome, '
	output += login_session['username']
	output += '!</h5>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 30px; height: 30px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	return output

def createUser(login_session):
	user = User(
		name = login_session['username'] ,
		picture = login_session['picture']  ,
		email = login_session['email'] )
	session.add(user)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id

def getUserInfo(user_id): 
	user = session.query(User).filter_by(id=user_id).one()
	return user

def getUserId(email): 
	try: 
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None

@app.route('/gdisconnect')
def gdisconnect():
	# Only disconnect a connected user.
	credentials = login_session.get('credentials')
	if credentials is None:
		response = make_response(
			json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = credentials.access_token
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result['status'] == '200':
		# Reset the user's sesson.
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']

		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return redirect( url_for('homePage'))
	else:
		# For whatever reason, the given token was invalid.
		response = make_response(
			json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response


@app.route('/category/<int:category_id>/items')
def CategoryItems(category_id): 
	items = session.query(Item).filter_by( category_id = category_id)
	if 'username' not in login_session:
		return render_template('public_category.html', items = items, category_id=category_id)		
	else:
		return render_template('private_category.html', items =items, category_id=category_id, login_session = login_session) 


# JSON APIs to view Category Items
@app.route('/category/<int:category_id>/items/JSON')
def restaurantMenuJSON(category_id):
	items = session.query(Item).filter_by( category_id = category_id)
	return jsonify(Items=[i.serialize for i in items])
	

@app.route('/category/<int:category_id>/additem', methods = ['POST', 'GET'])
def addItem(category_id):
	if request.method == 'POST':
		newItem = Item(name = request.form['name'], image_url = request.form['image_url'], category_id = category_id, user_id = login_session['user_id'])
		session.add(newItem)
		session.commit()
		return redirect( url_for('CategoryItems' , category_id=category_id ) ) 
	if 'username' not in login_session:
		return redirect( url_for('login'))
	else:
		return render_template('additem.html', category_id = category_id, login_session = login_session)
			
@app.route('/category/<int:category_id>/items/<int:item_id>/edit', methods = ['POST', 'GET']) 
def editItem(category_id, item_id): 
	editItem = session.query(Item).filter_by( id = item_id).one()
	if request.method == 'POST': 
		if request.form['name']:
			editItem.name = request.form['name']
			editItem.image_url = request.form['image_url']
		session.add(editItem)
		session.commit()
		return redirect( url_for('CategoryItems', category_id=category_id))
	return render_template('editItem.html', editItem = editItem, login_session = login_session)

@app.route('/category/<int:category_id>/items/<int:item_id>/delete', methods = ['POST', 'GET']) 
def deleteItem(category_id, item_id): 
	deleteItem = session.query(Item).filter_by(  id = item_id   ).one()
	if request.method == 'POST':
		session.delete(deleteItem)
		flash( '%s Successfully Deleted' % deleteItem.name)
		session.commit()
		return redirect( url_for('CategoryItems', category_id = category_id))
		# session.delete(deleteItem)
  #       # flash('%s Successfully Deleted' % deleteItem.name)
  #       session.commit()
  #      # r
	return render_template('deleteItem.html', deleteItem=deleteItem, login_session = login_session)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)