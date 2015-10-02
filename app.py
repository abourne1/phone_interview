import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from twilio.rest import TwilioRestClient

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
client = TwilioRestClient(app.config['ACCOUNT_SID'], app.config['AUTH_TOKEN'])
logger = app.logger

TWILIO_NUMBER = app.config['TWILIO_NUMBER']
URL = "http://0746eada.ngrok.io" #"https://polar-basin-7600.herokuapp.com"