"""
AWS IoT and Alexa for Business Demo
Author: Kevin Oleniczak
Date: 12/10/17
"""

from __future__ import print_function
import boto3
import json
from time import sleep
import numbers
import decimal
import uuid

lambda_client = boto3.client('lambda', region_name='us-west-2')

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "Windfarm Demo - " + title,
            'content': "Windfarm Demo - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def continue_dialog():
    session_attributes = {}
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_response(session_attributes, message)

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Amazon Web Services Windfarm Demo. " \
                    "You can check windfarm status and control certain turbine functions."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can check windfarm status and control certain turbine functions, " \
                    "say status or turbines."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for visiting the Windfarm today. " \
                    "Amazon web services is committed to running on 100 percent renewable energy sources."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}

def get_windfarm_status(intent, session):
    card_title = "Windfarm Status"
    session_attributes = {}
    reprompt_text = None

    inputMsg = {
      "duration_minutes": 5000,
      "windfarmId": "Windfarms_Core"
    }

    stmName = str(uuid.uuid4())
    client = boto3.client('stepfunctions', region_name='us-west-2')
    response = client.start_execution(
        stateMachineArn = 'arn:aws:states:us-west-2:588794348719:stateMachine:WindfarmGetStatus',
        name = stmName,
        input = json.dumps(inputMsg)
    )

    qryState = "TBD"
    while qryState != "SUCCEEDED":
        if qryState == "FAILED":
            break
        responseDesc = client.describe_execution(executionArn=response['executionArn'])
        qryState = responseDesc['status']
        print (qryState)
        sleep (1)

    if qryState == "SUCCEEDED":
        responseDesc = json.loads(responseDesc['output'])
        windfarmAvgWxWindSpeed = responseDesc[0]['avg_wind_speed']
        windfarmTurbineConnCnt = responseDesc[1]['turbine_connected_count']
        windfarmBrakeThreshold = responseDesc[2]['brake_threshold']
        windfarmWxWindSpeed = responseDesc[3]['latest_wind_speed']
    else:
        windfarmAvgWxWindSpeed = 0
        windfarmTurbineConnCnt = 'unknown'
        windfarmBrakeThreshold = 'unknown'
        windfarmWxWindSpeed = 0

    if windfarmTurbineConnCnt > 1:
        turbine_word = "turbines"
    else:
        turbine_word = "turbine"

    speech_output = "The windfarm is online with " + \
                    str(windfarmTurbineConnCnt) + \
                    " active " + turbine_word + ". The current wind speed is " + \
                    str(windfarmWxWindSpeed) + \
                    " mph with an average of " + \
                    str(windfarmAvgWxWindSpeed) + \
                    " miles per hour and the safety brake threshold is set to " + \
                    str(windfarmBrakeThreshold) + " rpm. Is there anything else I can help you with?"

    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def get_turbine_status(intent, session, dialog_state):
    """
    Gets the respective turbine status
    """
    card_title = "Turbine Status"
    session_attributes = {}
    should_end_session = False

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    elif dialog_state == "COMPLETED":
        if 'turbineNumber' in intent['slots']:
            #print ("slot info >> " + json.dumps(intent['slots']))
            myturbineNumber = intent['slots']['turbineNumber']['value']

            inputMsg = {
                "deviceId": "202481602013867",
                "turbine_number": myturbineNumber,
                "duration_minutes": 1
            }
            print(inputMsg)

            stmName = str(uuid.uuid4())
            client = boto3.client('stepfunctions', region_name='us-west-2')
            response = client.start_execution(
                stateMachineArn = 'arn:aws:states:us-west-2:588794348719:stateMachine:WindfarmGetTurbineStatus',
                name = stmName,
                input = json.dumps(inputMsg)
            )

            qryState = "TBD"
            while qryState != "SUCCEEDED":
                if qryState == "FAILED":
                    break
                responseDesc = client.describe_execution(executionArn=response['executionArn'])
                qryState = responseDesc['status']
                print (qryState)
                sleep (1)

            if qryState == "SUCCEEDED":
                responseDesc = json.loads(responseDesc['output'])

                avg_turbine_speed = responseDesc[0]['turbine_speed_trend']
                if avg_turbine_speed == 'unknown':
                    avg_turbine_speed = 0

                turbine_speed = responseDesc[1]['turbine_speed']
                if turbine_speed == 'unknown':
                    turbine_speed = 0

                turbine_connected = responseDesc[2]['connected']
                if turbine_connected == 'true':
                    turbine_connected = 'online'
                else:
                    turbine_connected = 'offline'

                turbine_brake_status = responseDesc[2]['brake_status']
            else:
                avg_turbine_speed = 0
                turbine_speed = 0

            speech_output = "The status for turbine " + \
                            str(myturbineNumber) + \
                            " is " + turbine_connected + \
                            " and the brake is " + turbine_brake_status + \
                            ". The recent average turbine speed is " + \
                            str(avg_turbine_speed) + \
                            " rpm and currently rotating at " + \
                            str(turbine_speed) + " rpm. Is there anything else I can help you with?"
            reprompt_text = "Let's get the turbine status, " \
                            "what turbine number?"
        else:
            speech_output = "I'm not sure which turbine your referring to. " \
                            "Please try again."
            reprompt_text = "I'm not sure which turbine your referring to. " \
                            "You can tell me the turbine number by saying, " \
                            "the number of the turbine you want to reset."
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    else:
        raise ValueError("Unknown dialog state")


def set_turbine_reset(intent, session, dialog_state):
    """
    Resets the respective turbine brake
    """
    card_title = "Reset Turbine Brake"
    session_attributes = {}
    should_end_session = False

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    elif dialog_state == "COMPLETED":
        if 'turbineNumber' in intent['slots']:
            #print ("slot info >> " + json.dumps(intent['slots']))
            myturbineNumber = intent['slots']['turbineNumber']['value']
            #set desired shadow state for the requested turbine
            invoke_response = lambda_client.invoke(FunctionName="WindfarmResetTurbine",
                                               InvocationType='RequestResponse'
                                               )
            #arn:aws:lambda:us-west-2:588794348719:function:WindfarmResetTurbine
            #should_end_session = True
            speech_output = "The brake for turbine " + \
                            str(myturbineNumber) + \
                            " has been reset. "
            reprompt_text = "Let's reset a turbine brake, " \
                            "what turbine number?"
        else:
            speech_output = "I'm not sure which turbine your referring to. " \
                            "Please try again."
            reprompt_text = "I'm not sure which turbine your referring to. " \
                            "You can tell me the turbine number by saying, " \
                            "the number of the turbine you want to reset."
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    else:
        raise ValueError("Unknown dialog state")


def set_turbine_brake(intent, session, dialog_state):
    """
    Resets the respective turbine brake
    """
    card_title = "Apply Turbine Brake"
    session_attributes = {}
    should_end_session = False

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    elif dialog_state == "COMPLETED":

        if 'turbineNumber' in intent['slots']:
            #print ("slot info >> " + json.dumps(intent['slots']))
            myturbineNumber = intent['slots']['turbineNumber']['value']
            print ("set brake >> myturbineNumber " + str(myturbineNumber))
            #set desired shadow state for the requested turbine
            invoke_response = lambda_client.invoke(FunctionName="WindfarmSetTurbineBrake",
                                               InvocationType='RequestResponse'
                                               )
            #arn:aws:lambda:us-west-2:588794348719:function:WindfarmSetTurbineBrake
            should_end_session = True
            speech_output = "The brake for turbine " + \
                            str(myturbineNumber) + \
                            " has been set. "
            reprompt_text = "Let's set a turbine brake, " \
                            "what turbine number?"
            #should_end_session = True
        else:
            speech_output = "I'm not sure which turbine your referring to. " \
                            "Please try again."
            reprompt_text = "I'm not sure which turbine your referring to. " \
                            "You can tell me the turbine number by saying, " \
                            "the number of the turbine you want to control."
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    else:
        return ValueError("Unknown dialog state")


def do_turbine(intent, session, dialog_state):
    """
     the respective turbine
    """
    card_title = "Turbines"
    session_attributes = {}
    should_end_session = False

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    elif dialog_state == "COMPLETED":
        if 'action' in intent['slots']:
            action = intent['slots']['action']['value']
            print ("Action >> " + action)
            if action == "status":
                return get_turbine_status(intent, session, dialog_state)
            elif action == "apply brake":
                return set_turbine_brake(intent, session, dialog_state)
            elif action == "reset brake":
                return set_turbine_reset(intent, session, dialog_state)
            else:
                raise ValueError("Unknown action")
        else:
            raise ValueError("Unknown action")
    else:
        raise ValueError("Unknown dialog state")

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    dialog_state = intent_request['dialogState']
    print ("dialog_state == " + dialog_state)

    # Dispatch to your skill's intent handlers
    if intent_name == "Status":
        return get_windfarm_status(intent, session)
    elif intent_name == "Turbines":
        return do_turbine(intent, session, dialog_state)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
      "amzn1.ask.skill.7a1a609b-2a37-44ad-b768-d8c059d0f3c5"):
        raise ValueError("Invalid Application ID")
    print(json.dumps(event))

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
