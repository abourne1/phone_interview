import os
from flask import Flask
from twilio.rest import TwilioRestClient

app = Flask(__name__)
client = TwilioRestClient(os.environ.get('ACCOUNT_SID'), os.environ.get('AUTH_TOKEN'))
logger = app.logger

from views import *
