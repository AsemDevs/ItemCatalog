#!/usr/bin/env python3

from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import User, City, Place, Base
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Cities & Places"

# Connect to Database and create database session
engine = create_engine('sqlite:///citiescatalog.db')

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

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
    output += '''"style = "width: 300px; height: 300px;border-radius: 150px;
    -webkit-border-radius: 150px;-moz-border-radius: 150px;">'''
    print ("done!")
    return output


# Authorization (Local permission system)
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except IndexError:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        ncmsg = 'Current user not connected.'
        response = make_response(json.dumps(ncmsg), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = '''https://accounts.google.com/o/oauth2/revoke?
    token=%s''' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        frmsg = 'Failed to revoke token for user.'
        response = make_response(json.dumps(frmsg), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Places Information

@app.route('/city/<int:city_id>/place/JSON')
def showPlacesJSON(city_id):
    city = session.query(City).filter_by(id=city_id).one()
    places = session.query(Place).filter_by(
        city_id=city_id).all()
    return jsonify(places=[i.serialize for i in places])


@app.route('/city/<int:city_id>/place/<int:place_id>/JSON')
def PlaceJSON(city_id, place_id):
    place = session.query(Place).filter_by(id=place_id).one()
    return jsonify(place=place.serialize)


@app.route('/city/JSON')
def showCitiesJSON():
    city = session.query(City).all()
    return jsonify(city=[c.serialize for c in city])


# All the routes
@app.route('/')
@app.route('/cities')
def showCities():
    cities = session.query(City).all()
    return render_template('cities.html', cities=cities)


@app.route('/city/new', methods=['GET', 'POST'])
def newCity():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newCity = City(name=request.form['name'],
                       user_id=login_session['user_id'])
        session.add(newCity)
        session.commit()
        return redirect(url_for('showCities'))
    else:
        return render_template('newCity.html')


@app.route('/city/<int:city_id>/edit', methods=['GET', 'POST'])
def editCity(city_id):
    if 'username' not in login_session:
        return redirect('/login')

    editedCity = session.query(City).filter_by(id=city_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCity.name = request.form['name']
            session.add(editedCity)
            session.commit()
            return redirect(url_for('showCities'))
    else:
        return render_template('editCity.html', city=editedCity)


@app.route('/city/<int:city_id>/delete', methods=['GET', 'POST'])
def deleteCity(city_id):
    if 'username' not in login_session:
        return redirect('/login')

    deletedCity = session.query(City).filter_by(id=city_id).one()
    if request.method == 'POST':
        session.delete(deletedCity)
        session.commit()
        return redirect(url_for('showCities', city_id=city_id))
    else:
        return render_template('deleteCity.html', city=deletedCity)


@app.route('/city/<int:city_id>/')
@app.route('/city/<int:city_id>/places')
def showPlaces(city_id):
    city = session.query(City).filter_by(id=city_id).one()
    creator = getUserInfo(city.user_id)
    places = session.query(Place).filter_by(city_id=city_id).all()
    u_id = 'user_id'
    if 'username' not in login_session or creator.id != login_session[u_id]:
        return render_template('publicplaces.html', places=places,
                               city=city, creator=creator)
    else:
        return render_template('places.html', places=places, city=city,
                               city_id=city_id, creator=creator)


@app.route('/city/<int:city_id>/place/new', methods=['GET', 'POST'])
def newPlace(city_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCity = session.query(City).filter_by(id=city_id).one()
    city = session.query(City).filter_by(id=city_id).one()
    if request.method == 'POST':
        newPlace = Place(name=request.form['name'],
                         description=request.form['description'],
                         city_id=city_id,
                         user_id=city.user_id)
        session.add(newPlace)
        session.commit()
        return redirect(url_for('showPlaces', city_id=city_id))
    else:
        return render_template('newPlace.html', city_id=city_id)


@app.route('/city/<int:city_id>/<int:place_id>/edit', methods=['GET', 'POST'])
def eidtPlace(city_id, place_id):
    if 'username' not in login_session:
        return redirect('/login')
    city = session.query(City).filter_by(id=city_id).one()
    editedPlace = session.query(Place).filter_by(id=place_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedPlace.name = request.form['name']
        if request.form['description']:
            editedPlace.description = request.form['description']
        session.add(editedPlace)
        session.commit()
        return redirect(url_for('showCities'))
    else:
        return render_template('editPlace.html', city_id=city_id,
                               place_id=place_id, place=editedPlace)


@app.route('/city/<int:city_id>/<int:place_id>/delete',
           methods=['GET', 'POST'])
def deletePlace(city_id, place_id):
    if 'username' not in login_session:
        return redirect('/login')

    deletedPlace = session.query(Place).filter_by(id=place_id).one()
    if request.method == 'POST':
        session.delete(deletedPlace)
        session.commit()
        return redirect(url_for('showCities', city_id=city_id))
    else:
        return render_template('deletePlace.html',
                               city_id=city_id, place_id=place_id,
                               place=deletedPlace)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=7000)
