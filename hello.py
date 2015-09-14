import os
from flask import Flask, render_template, request
from twilio.rest import TwilioRestClient

app = Flask(__name__)
client = TwilioRestClient(os.environ.get('ACCOUNT_SID'), os.environ.get('AUTH_TOKEN'))
logger = app.logger

TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER_1')
URL = os.environ.get('URL')
LANGUAGES = os.environ.get('LANGUAGES')

@app.route('/')
def homepage():
    return render_template(
        'homepage.html',
        topics=db.session.query(Topic).all(),
        is_current=False
    )


@app.route('/choose_question', methods=['GET', 'POST'])
def choose_question():
    print "In choose question"
    topic_id = request.args.get('topic_id', '')
    phone_number = request.args.get('number', '')
    print request.args
    record = ("on" == request.args.get('if_record', ''))
    print record
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
        languages=LANGUAGES,
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


