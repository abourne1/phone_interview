import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from twilio.rest import TwilioRestClient

app = Flask(__name__)
db = SQLAlchemy(app)
client = TwilioRestClient(os.environ['ACCOUNT_SID'], os.environ['AUTH_TOKEN'])
logger = app.logger

TWILIO_NUMBER = "+18582155230"
URL = "http://soloscreen.herokuapp.com"
