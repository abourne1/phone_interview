import datetime
from app import db

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    pw_hash = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)

    def __init__(self, name, password, email):
        self.name = name
        self.set_password(password)
        self.email = email
        self.timestamp = datetime.date.now()

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

class Language(db.Model):
    __tablename__ = 'languages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    text = db.Column(db.Text(2000))
    hint = db.Column(db.Text(2000))
    timestamp = db.Column(db.DateTime)
    popularity = db.Column(db.Integer)
    answer = db.Column(db.Text(2000))
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'))

    def __init__(self, text, user_id, hint, topic_id, answer, language_id):
        self.topic_id = topic_id
        self.text = text
        self.hint = hint
        self.timestamp = datetime.datetime.now()
        self.answer = answer
        self.popularity = 0
        self.language_id = language_id
        self.user_id = user_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def language(self):
        l = db.session.query(Language).get(self.language_id)
        print l.name
        return l.name

class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Recording(db.Model):
    __tablename__ = 'recordings'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200))
    call_sid = db.Column(db.String(300))
    recording_sid = db.Column(db.String(300))
    sent = db.Column(db.Boolean)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime)

    def __init__(self, url, call_sid, recording_sid):
        self.url = url
        self.call_sid = call_sid
        self.recording_sid = recording_sid
        self.timestamp = datetime.datetime.now()

    def question(self):
        if self.question_id:
            return db.session.query(Question).get(self.question_id)
        else: 
            return ""

    def prettify(self):
        return self.remove_zero(self.timestamp.strftime("%a, %d %b %Y %I:%M %p")) if self.timestamp else ""

    def remove_zero(self, timestamp):
        time_list = timestamp.split()
        if time_list[-2][0]=='0':
            time_list[-2] = time_list[-2][1:]
        return ' '.join(time_list)  

    def __repr__(self):
        return '<id {}>'.format(self.id)

