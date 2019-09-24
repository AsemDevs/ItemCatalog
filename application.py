from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import User
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
def ShowCities():
	return "This Page will list all the cities"

@app.route('/city/new')
def newCity():
	return "This Page will be for making a new city"

@app.route('/city/<int:city_id>/edit')
def editCity(city_id):
	return "This Page will be for editing city %s" % city_id

@app.route('/city/<int:city_id>/delete')
def deleteCity(city_id):
	return "This Page will be for deleting city %s" % city_id

@app.route('/city/<int:city_id>/')
@app.route('/city/<int:city_id>/places')
def ShowPlaces(city_id):
	return "This Page will list all the the places for the city %s" % city_id

@app.route('/city/<int:city_id>/place/new')
def newPlace(city_id):
	return "This Page will be for making a new place for city %s" % city_id

@app.route('/city/<int:city_id>/<int:place_id>/edit')
def eidtPlace(city_id, place_id):
	return "This Page will be for editing place %s" % place_id

@app.route('/city/<int:city_id>/<int:place_id>/delete')
def deletePlace(city_id, place_id):
	return "This Page will be for deleting place %s" % place_id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=7000)