import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from twilio.rest import TwilioRestClient

app = Flask(__name__)
print os.environ
db = SQLAlchemy(app)
client = TwilioRestClient(os.environ['ACCOUNT_SID'], os.environ['AUTH_TOKEN'])
logger = app.logger

TWILIO_NUMBER = os.environ['TWILIO_NUMBER']
URL = "https://polar-basin-7600.herokuapp.com"
