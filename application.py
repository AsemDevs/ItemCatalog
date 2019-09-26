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
engine = create_engine('sqlite:///citiescatalog.db')

DBSession = sessionmaker(bind=engine)
session = DBSession()


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

@app.route('/city/<int:city_id>/edit')
def editCity(city_id):
	return render_template('editCity.html', cities=cities, city=city, city_id=city_id)

@app.route('/city/<int:city_id>/delete')
def deleteCity(city_id):
	return render_template('deleteCity.html', city_id=city_id)

@app.route('/city/<int:city_id>/')
@app.route('/city/<int:city_id>/places')
def ShowPlaces(city_id):
	return render_template('places.html', city_id=city_id)

@app.route('/city/<int:city_id>/place/new')
def newPlace(city_id):
	return render_template('newPlace.html', city_id=city_id)

@app.route('/city/<int:city_id>/<int:place_id>/edit')
def eidtPlace(city_id, place_id):
	return render_template('editPlace.html', city_id=city_id, place_id = place_id)

@app.route('/city/<int:city_id>/<int:place_id>/delete')
def deletePlace(city_id, place_id):
	return render_template('deletePlace.html', city_id=city_id, place_id = place_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=7000)