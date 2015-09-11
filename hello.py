import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def rello():
    return 'Hello World!'
