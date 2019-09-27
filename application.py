from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import User, City, Place
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

# Connect to Database and create database session
engine = create_engine('sqlite:///citiescatalog.db')

DBSession = sessionmaker(bind=engine)
session = DBSession()

# JSON APIs to view Restaurant Information

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



@app.route('/cities')
def showCities():
	cities = session.query(City).all()
	return render_template('cities.html', cities=cities)

@app.route('/city/new', methods=['GET', 'POST'])
def newCity():
	if request.method == 'POST':
		newCity = City(name=request.form['name'])
		session.add(newCity)
		session.commit()
		return redirect(url_for('showCities'))
	else:
		return render_template('newCity.html')

@app.route('/city/<int:city_id>/edit', methods=['GET', 'POST'])
def editCity(city_id):
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
	places = session.query(Place).filter_by(city_id=city_id).all()
	return render_template('places.html', places=places, city=city,city_id=city_id)

@app.route('/city/<int:city_id>/place/new', methods=['GET', 'POST'])
def newPlace(city_id):
	city = session.query(City).filter_by(id=city_id).one()
	if request.method == 'POST':
		newPlace = Place(name=request.form['name'], description=request.form['description'], city_id=city_id, user_id=city.user_id)
		session.add(newPlace)
		session.commit()
		return redirect(url_for('showPlace', city_id=city_id))
	else:
		return render_template('newPlace.html', city_id=city_id)

@app.route('/city/<int:city_id>/<int:place_id>/edit', methods=['GET', 'POST'])
def eidtPlace(city_id, place_id):
	editedCity = session.query(City).filter_by(id=city_id).one()
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
		return render_template('editPlace.html', city_id=city_id, place_id = place_id, place=editedPlace)

@app.route('/city/<int:city_id>/<int:place_id>/delete', methods=['GET', 'POST'])
def deletePlace(city_id, place_id):
	city = session.query(City).filter_by(id=city_id).one()
	deletedPlace = session.query(Place).filter_by(id=place_id).one()
	if request.method == 'POST':
		session.delete(deletedPlace)
		session.commit()
		return redirect(url_for('showCities', city_id=city_id))
	else:
		return render_template('deletePlace.html', city_id=city_id, place_id = place_id, place = deletedPlace )


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=7000)