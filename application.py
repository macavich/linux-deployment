from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Sport, SportItem, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


#Connect to Database and create database session
engine = create_engine('sqlite:///sportscatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid State Parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # then exchange client token for the long-lived server-side token with GET
    app_id = json.loads(open('fb_client_secrets.json','r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json','r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type=' +
        'fb_exchange_token&client_id={}&client_secret={}'.format(app_id, app_secret) +
        '&fb_exchange_token={}'.format(access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print(json.loads(result))
    token = json.loads(result)['access_token']
    #token = result.split('&')[0]

    # assuming the token works, we should be able to make api calls
    url = 'https://graph.facebook.com/v2.8/me?access_token={}&fields=name,id,email'.format(token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print('url sent for API access: {}'.format(url))
    # print('API JSON result: {}'.format(result))
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    # get photos
    url = ('https://graph.facebook.com/{}'.format(login_session['facebook_id']) +
           '/picture?type=square&redirect=0')
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']

    # see if a user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    print(login_session)
    return output

@app.route('/gconnect', methods=['POST'])
def gconnect():
    print(login_session)
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secrets.json', scope = '', redirect_uri = 'postmessage')
        # exchanging authorization code for access token
        dCredentials = json.loads(oauth_flow.step2_exchange(code).to_json())
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the ' +
            'authorization code.'), 401)
        response.headers['Content-Type'] = 'application.json'
        return response
    # check that the access token is valid
    access_token = dCredentials['access_token']
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=' +
        '{}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    print(result)
    # if there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # verify that the access token is used for the intended user
    gplus_id = dCredentials['id_token']['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401
        )
        print("Token's client ID does not match apps's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    # check to see the user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already' +
            ' connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': dCredentials['access_token'], 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    # store the access token in the session for later use.
    login_session['credentials'] = dCredentials
    login_session['gplus_id'] = gplus_id

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if the user exists, if it doesn't make a new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    print(login_session)
    return output

@app.route("/disconnect")
def disconnect():
    # only disconnect a connected user
    if login_session['provider'] == 'google':
        dCredentials = login_session.get('credentials')
        print(dCredentials)
        if dCredentials is None:
            if login_session.get('credentials') is not None:
                del login_session['credentials']
            if login_session.get('gplus_id') is not None:
                del login_session['gplus_id']
            if login_session.get('username') is not None:
                del login_session['username']
            if login_session.get('email') is not None:
                del login_session['email']
            if login_session.get('picture') is not None:
                del login_session['picture']
            response = make_response(json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Execute HTTP GET request to revoke current token
        access_token = dCredentials['access_token']
        print(access_token)
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        h = httplib2.Http()
        resp, content = h.request(url, 'POST', headers=headers)
        if int(resp['status']) == 200:
            del login_session['credentials']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']

            # response = make_response(json.dumps('Successfully disconnected'), 200)
            # response.headers['Content-Type'] = 'application/json'
            flash("You have been successfully logged out!")
            return redirect(url_for('showSports'))
        else:
            if login_session.get('credentials') is not None:
                del login_session['credentials']
            if login_session.get('gplus_id') is not None:
                del login_session['gplus_id']
            if login_session.get('username') is not None:
                del login_session['username']
            if login_session.get('email') is not None:
                del login_session['email']
            if login_session.get('picture') is not None:
                del login_session['picture']
            # for whatever reason, the given token was invalid
            response = make_response(json.dumps('Failed to revoke the token' +
                ' for given user.'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response
    elif login_session['provider'] == 'facebook':
        facebook_id = login_session['facebook_id']
        url = 'https://graph.facebook.com/{}/permissions'.format(facebook_id)
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['facebook_id']
        flash("You have been successfully logged out!")
        return redirect(url_for('showSports'))

@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
        string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/sports/<int:sport_id>/items/<int:item_id>/')
def showSportItem(sport_id, item_id):
    session = DBSession()
    try:
        item = session.query(SportItem).filter_by(id=item_id).one()
        sport = session.query(Sport).filter_by(id=sport_id).one()
    except NoResultFound:
        return jsonify({'error': 'incorrect sport or item id'}), 404
    return render_template('showSportItem.html', item=item, sport=sport)

#Show the homepage
@app.route('/')
@app.route('/sports/')
def showSports():
    if login_session.get('username') is not None:
        print(login_session['username'])
        logged_in = True
    else:
        print("No one's logged in.")
        logged_in = False
    session = DBSession()
    sports = session.query(Sport).order_by(asc(Sport.name)).all()
    dSports = {}
    items = session.query(SportItem).order_by(desc(SportItem.id)).all()
    itemsToShow = []
    for index, item in enumerate(items):
        if index > 9:
            break
        else:
            itemsToShow.append(item)
    for sport in sports:
        dSports[sport.id] = sport.name
    return render_template('sports.html', dSports=dSports,
        itemsToShow=itemsToShow, logged_in=logged_in)
    # if 'username' not in login_session:
    #     return render_template('publicsports.html', sports = sports)
    # else:
    #     return render_template('sports.html', sports = sports)


# #Create a new restaurant
# @app.route('/restaurant/new/', methods=['GET','POST'])
# def newRestaurant():
#     if 'username' not in login_session:
#         return redirect('/login')
#     if request.method == 'POST':
#         session = DBSession()
#         newRestaurant = Restaurant(name = request.form['name'],
#                                    user_id = login_session['user_id'])
#         session.add(newRestaurant)
#         flash('New Restaurant %s Successfully Created' % newRestaurant.name)
#         session.commit()
#         return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('newRestaurant.html')
#
# #Edit a restaurant
# @app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
# def editRestaurant(restaurant_id):
#     if 'username' not in login_session:
#         return redirect('/login')
#     session = DBSession()
#     editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
#     if request.method == 'POST':
#         if request.form['name']:
#             editedRestaurant.name = request.form['name']
#             flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
#             return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('editRestaurant.html', restaurant = editedRestaurant)
#
#
# #Delete a restaurant
# @app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
# def deleteRestaurant(restaurant_id):
#     if 'username' not in login_session:
#         return redirect('/login')
#     session = DBSession()
#     restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
#     if restaurantToDelete.user_id != login_session['user_id']:
#         return """<script>function myFunction() {alert('You are not authorized
#             to delete this restaurant.  Please create our own restaurant
#             in order to delete.');}</script><body onload='myFunction()'>"""
#     if request.method == 'POST':
#         session.delete(restaurantToDelete)
#         flash('%s Successfully Deleted' % restaurantToDelete.name)
#         session.commit()
#         return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))
#     else:
#         return render_template('deleteRestaurant.html',restaurant = restaurantToDelete)


#Show a restaurant menu
@app.route('/sport/<int:sport_id>/')
@app.route('/sport/<int:sport_id>/items/')
def showSportsItems(sport_id):
    session = DBSession()
    sport = session.query(Sport).filter_by(id = sport_id).one()
    items = session.query(SportItem).filter_by(sport_id = sport_id).all()
    return render_template('sportsItems.html', items = items, sport = sport)
    # creator = getUserInfo(restaurant.user_id)
    # if 'username' not in login_session or creator.id != login_session['user_id']:
    #     return render_template(
    #         'publicmenu.html', items = items, restaurant = restaurant, creator = creator)
    # else:
    #     return render_template(
    #         'menu.html', items = items, restaurant = restaurant, creator = creator)


#Create a new menu item
@app.route('/sports/new/',methods=['GET','POST'])
def newSportItem():
    # if 'username' not in login_session:
    #     return redirect('/login/')
    session = DBSession()
    if request.method == 'POST':
        if request.form['sport']:
            try:
                sport_id = session.query(Sport).filter_by(
                    name = request.form['sport']).one().id
            except NoResultFound:
                flash("You didn't enter a valid sport, please choose from " +
                      "one of the below sports")
                return redirect(url_for('showSports'))
            newItem = SportItem(name = request.form['name'],
                                description = request.form['description'],
                                sport_id = sport_id)
            session.add(newItem)
            session.commit()
            flash('New Menu %s Item Successfully Created' % (newItem.name))
            return redirect(url_for('showSports'))
        elif not request.form['name'] or not request.form['description']:
            flash('You were missing some fields, please try again')
            return render_template('newSportItem.html')
        else:
            flash("Something unknown happened, please try again")
            return render_template('newSportItem.html')
    else:
        return render_template('newSportItem.html')
#
# #Edit a menu item
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
# def editMenuItem(restaurant_id, menu_id):
#     print(login_session)
#     if 'username' not in login_session:
#         print('uh')
#         return redirect('/login')
#     print(login_session['username'])
#     session = DBSession()
#     editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
#     restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
#     if restaurant.user_id != login_session['user_id']:
#         return """<script>function myFunction() {alert('You are not authorized
#             to delete this restaurant.  Please create our own restaurant
#             in order to delete.');}</script><body onload='myFunction()'>"""
#     if request.method == 'POST':
#         if request.form['name']:
#             editedItem.name = request.form['name']
#         if request.form['description']:
#             editedItem.description = request.form['description']
#         if request.form['price']:
#             editedItem.price = request.form['price']
#         if request.form['course']:
#             editedItem.course = request.form['course']
#         session.add(editedItem)
#         session.commit()
#         flash('Menu Item Successfully Edited')
#         return redirect(url_for('showMenu', restaurant_id = restaurant_id))
#     else:
#         return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = editedItem)
#
#
# #Delete a menu item
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
# def deleteMenuItem(restaurant_id,menu_id):
#     if 'username' not in login_session:
#         return redirect('/login')
#     session = DBSession()
#     restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
#     itemToDelete = session.query(MenuItem).filter_by(id = menu_id).one()
#     if restaurant.user_id != login_session['user_id']:
#         return """<script>function myFunction() {alert('You are not authorized
#             to delete this restaurant.  Please create our own restaurant
#             in order to delete.');}</script><body onload='myFunction()'>"""
#     if request.method == 'POST':
#         session.delete(itemToDelete)
#         session.commit()
#         flash('Menu Item Successfully Deleted')
#         return redirect(url_for('showMenu', restaurant_id = restaurant_id))
#     else:
#         return render_template('deleteMenuItem.html', item = itemToDelete)

def getUserID(email):
    session = DBSession()
    try:
        try:
            user = session.query(User).filter_by(email = email).one()
            return user.id
        except:
            user = session.query(User).filter_by(email = email).all()
            return user[0].id
    except:
        return None


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id = user_id).one()
    return user

def createUser(login_session):
    session = DBSession()
    newUser = User(name = login_session['username'],
                   picture = login_session['picture'],
                   email = login_session['email'])
    session.add(newUser)
    session.commit()
    try:
        user = session.query(User).filter_by(picture = login_session['picture']).one()
    except:
        user = session.query(User).filter_by(picture = login_session['picture']).all()
        return user[0].id
    return user.id

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
