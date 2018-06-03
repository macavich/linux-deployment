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
    return render_template(
        'sports.html', dSports=dSports, itemsToShow=itemsToShow)
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
