import twilio
import random
from app import app, db, client, logger, URL, TWILIO_NUMBER
from models import Topic, Question, Language, Recording
from flask import render_template, request

"""
VIEWS
"""

@app.route('/')
def homepage():
    return render_template(
        'homepage.html',
        topics=db.session.query(Topic).all(),
        is_current=False
    )


@app.route('/choose_question', methods=['GET', 'POST'])
def choose_question():
    topic_id = request.args.get('topic_id', '')
    phone_number = request.args.get('number', '')
    record = ("on" == request.args.get('if_record', ''))
    logger.debug(record)
    question = pick_question(topic_id)
    url = "{}/handle_call?question_id={}&action=speak".format(URL, question.id)
    call = client.calls.create(
        to=phone_number,
        from_=TWILIO_NUMBER,
        url=url,
        record=record,
        status_callback=URL + "/handle_recording",
        status_callback_method="POST"
    )

    return render_template(
        'in_call.html',
        topics=db.session.query(Topic).all(),
        is_current=True,
        call_sid=call.sid,
        question_id=question.id,
        languages=db.session.query(Language).all(),
        answer=question.answer,
        answer_language=str(question.language)
    )

@app.route('/handle_call', methods=['GET', 'POST'])
def handle_call():
    action = request.args.get('action', '')
    question_id = request.args.get('question_id', '')
    question = db.session.query(Question).get(question_id)
    resp = twilio.twiml.Response()

    if action == "repeat":
        resp.say(question.text)
    elif action == "hint":
        resp.say(question.hint)
    elif action == "answer":
        resp.say(question.answer)
    else:
        resp.say(question.text)
        logger.debug(question.text)

    # pause for 5 min before hanging up
    resp.pause(length=60 * 5)
    return str(resp)

"""
IN CALL
"""

@app.route('/in_call', methods=["GET"])
def in_call():
    return render_template(
        'in_call.html'
    )

@app.route('/next-question', methods=['GET', 'POST'])
def next_question():
    sid = request.args.get('call_sid', '')
    topic_id = request.args.get('topic_id', '')
    question = pick_question(topic_id)
    update_call(sid, question.id)
    return render_template(
        'in_call.html',
        topics=db.session.query(Topic).all(),
        is_current=True,
        call_sid=sid,
        question_id=question.id,
        languages=LANGUAGES,
        answer=question.answer,
        answer_language=question.language
    )

@app.route('/upvote', methods=['GET', 'POST'])
def upvote():
    sid, question_id, voted, user_input = get_params()
    question = db.session.query(Question).get(question_id)
    user_input = request.args.get('user_input', '')
    language = request.args.get('language', '')

    if question.popularity:
        question.popularity += 1
    else:
        question.popularity = 1
    db.session.commit()
    return render_template(
        'in_call.html',
        topics=db.session.query(Topic).all(),
        is_current=True,
        call_sid=sid,
        question_id=question_id,
        voted=True,
        languages=LANGUAGES,
        user_input = user_input,
        language = language,
        answer=question.answer,
        answer_language=question.language
    )

@app.route('/repeat', methods=['GET', 'POST'])
def repeat():
    sid, question_id, voted, user_input = get_params()
    question = db.session.query(Question).get(question_id)
    update_call(sid, question_id, "repeat")
    return render_template(
        'in_call.html',
        topics=db.session.query(Topic).all(),
        is_current=True,
        call_sid=sid,
        question_id=question_id,
        voted=voted,
        languages=LANGUAGES,
        answer=question.answer,
        language = request.args.get('language', ''),
        user_input = user_input,
        answer_language=question.language
    )

@app.route('/hint', methods=['GET', 'POST'])
def hint():
    sid, question_id, voted, user_input = get_params()
    question = db.session.query(Question).get(question_id)
    update_call(sid, question_id, "hint")
    return render_template(
        'in_call.html',
        topics=db.session.query(Topic).all(),
        is_current=True,
        call_sid=sid,
        question_id=question_id,
        voted=voted,
        languages=LANGUAGES,
        answer=question.answer,
        language = request.args.get('language', ''),
        user_input = user_input,
        answer_language=question.language
    )

@app.route('/hangup', methods=['GET', 'POST'])
def hangup():
    sid = request.args.get('call_sid', '')
    call = client.calls.update(sid, status="completed")
    return render_template(
        'homepage.html',
        topics=TOPICS,
        is_current=False
    )

def order_popular_questions():
    conn = db.connect()
    questions = conn.execute("")

def pick_question(topic_id):
    if topic_id == "0":
        matches = db.session.query(Question).order_by(Question.popularity.desc())
        index = int(random.random()**2 * matches.count() )
        question = matches.all()[index]
    else:
        matches = db.session.query(Question).filter(
            Question.topic_id == topic_id
        ).order_by(Question.popularity.desc())
        index = int(random.random()**2 * matches.count() )
        question = matches.all()[index]
    return question

def get_params():
    sid = request.args.get('call_sid', '')
    question_id = request.args.get('question_id', '')
    voted = request.args.get('voted', '')
    user_input = request.args.get('user_input', '')
    return sid, question_id, voted, user_input

def update_call(sid, question_id, action=""):
    url = "http://employed.herokuapp.com/handle_call?question_id={}&action={}".format(question_id, action)
    call = client.calls.update(sid, url=url, method="POST")

"""
NEW QUESTION
"""

@app.route('/new', methods=['GET', 'POST'])
def new():
    print "in new"
    return render_template(
        'new.html',
        topics=db.session.query(Topic).all(),
        languages=db.session.query(Language).all()
    )

@app.route('/make', methods=['POST'])
def make():
    # add validations, probably through a form class
    print request.form
    text=request.form['question']
    hint=request.form['hint']
    topic_id=request.form['topic_id']
    answer=request.form['answer']
    language=request.form['language']
    print "in make:"
    print language
    new_question = Question(
        text=text,
        hint=hint,
        topic_id=topic_id,
        answer=answer,
        language=language
    )
    db.session.add(new_question)
    db.session.commit()
    print new_question.language
    flash('Question created')

    return render_template(
        'homepage.html',
        topics=db.session.query(Topic).all(),
        questions=db.session.query(Question).all()
    )

"""
RECORDINGS
"""

@app.route('/recordings', methods=["GET","POST"])
def recordings():
    return render_template(
        'recordings.html',
        recordings=db.session.query(Recording).order_by(Recording.timestamp.desc()).all()
    )


@app.route('/handle_recording', methods=["GET","POST"])
def handle_recording():
    print "HERE!"
    print request.form
    new_recording = Recording(
        url=request.form['RecordingUrl'],
        call_sid=request.form['CallSid'],
        recording_sid=request.form['RecordingSid'],
    )
    db.session.add(new_recording)
    db.session.commit()
    return render_template(
        'homepage.html',
        topics=db.session.query(Topic).all(),
        is_current=False
    )


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

