import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from twilio.rest import TwilioRestClient

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
client = TwilioRestClient(os.environ.get('ACCOUNT_SID'), os.environ.get('AUTH_TOKEN'))
logger = app.logger

TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER_1')
URL = os.environ.get('URL')