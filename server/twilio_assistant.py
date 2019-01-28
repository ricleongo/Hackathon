from __future__ import print_function
import json
from flask import Flask, jsonify, render_template, request
from twilio.twiml.voice_response import Gather, VoiceResponse
from watson_developer_cloud import AssistantV2
from secret.keys import *
from functions.functions import *

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/airecruiter", methods = ['POST'])
def airecruiter():
    """End point dedicated to communicate with the user as assistant"""
    # welcome_message = ['Wellcome to the AI Recruiter Tool...',
    # # 'How can I help you?',
    # 'You can ask for status of your licences, check the candidates growth in latest month, and even know the most used actions from recruiters.',
    # 'Just ask whenever you feel ready, saying Please let me know the candidates grow, for example...']

    message = ''
    number = ''
    twilio_number = ''
    session = None

    assistant = AssistantV2(
        username=watson_username,
        password=watson_password,
        url=watson_url,
        version=watson_version)

    if request.values.get('SpeechResult'):
        message = request.values['SpeechResult']

    if request.values.get('From'):
        number = request.values['From']

    if request.values.get('To'):
        twilio_number = request.values['To']  


    twilio_response = VoiceResponse()
    gather = Gather(input='speech', action='/airecruiter', speechTimeout='auto')

    if session is None:
        session = assistant.create_session(watson_assistanceID).get_result()

    sessionID = session['session_id']

    if message != '':
        print("message: {}".format(message))

        message = assistant.message(
            watson_assistanceID,
            sessionID,
            input={'text': message}).get_result()

        if (len(message['output']['generic']) > 0):
            for intern_response in message['output']['generic'] :
                if intern_response['response_type'] == 'text':
                    print(intern_response['text'])

                    if intern_response['text'] == "{userName}":
                        messageApi = assistant.message(
                            watson_assistanceID,
                            sessionID,
                            input={'text': login()}).get_result()

                        if (len(messageApi['output']['generic']) > 0):
                            for intern_api_response in messageApi['output']['generic'] :
                                if intern_api_response['response_type'] == 'text':
                                    print(intern_api_response['text'])
                                    gather.say(intern_api_response['text'], voice= 'alice')

                    elif intern_response['text'] == "{growth}":
                        gather.say('sure, I will let you know about the candidates growth in a second.', voice= 'alice')

                        for idea_response in get_candidate_growth() :
                            gather.say(idea_response, voice= 'alice')

                    elif intern_response['text'] == "{resumeviewed}":
                        gather.say('sure thing, I will let you know about the most recent resumes viewed.', voice= 'alice')

                        for idea_response in most_viewed_resumes() :
                            gather.say(idea_response, voice= 'alice')

                    elif intern_response['text'] == "{actionused}":
                        gather.say('hold on a second, I am collecting the data.', voice= 'alice')

                        for idea_response in actions_used_by_recruiter() :
                            gather.say(idea_response, voice= 'alice')

                    else:
                        gather.say(intern_response['text'], voice= 'alice')
            
            gather.pause(2)
            gather.say('Is there other question that I can answer?', voice= 'alice')


    else:
        message = assistant.message(
            watson_assistanceID,
            sessionID,
            input={'text': login()}).get_result()

        if (len(message['output']['generic']) > 0):
            for intern_response in message['output']['generic'] :
                if intern_response['response_type'] == 'text':
                    print(intern_response['text'])
                    gather.say(intern_response['text'], voice= 'alice')

            gather.pause(2)
            gather.say('Remember, you can ask about the grow in candidates latest months. Just ask: "Alice, let me know the candidates grow."', voice= 'alice')

    twilio_response.append(gather)

    return str(twilio_response)


@app.route("/authenticate")
def authenticate():

    return ''

if __name__ == '__main__':
    app.run(debug=True)


