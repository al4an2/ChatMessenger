import time
from collections import defaultdict
from datetime import datetime

import requests
from flask import Flask, request, abort

app = Flask(__name__)
db = [
    {
        'name': 'Nick',
        'text': 'Hello!',
        'time': time.time()
    },
    {
        'name': 'Ivan',
        'text': 'Hello, Nick!',
        'time': time.time()
    },
    {
        'name': 'Ivan',
        'text': 'Hello, Nick!',
        'time': time.time()
    },
    {
        'name': 'Ivan',
        'text': 'Hello, Nick!',
        'time': time.time()
    },
]
API_WEATHER_KEY = "9b9540e892d346919e67a01ade1c25ee"  # API_KEY for weatherbit.io
FLAG_WEATHER = defaultdict()  # defaultdict for users with current weather requests.


@app.route("/")
def hello():
    return "Hello, Messenger!"


@app.route("/status")
def status():
    users = len(set(x['name'] for x in db))
    return {
        'status': True,
        'name': "al4an's Messenger",  # имя мессенджера
        'time': datetime.fromtimestamp(time.time()),  # текущее время на сервере
        'messages': len(db),
        'users': users
    }


@app.route("/send", methods=['POST'])
def send_message():
    """
    Base function of messenger

    Takes json requests:
    'name': str
    'text': str

    :return
    'ok': True -> if status code 200
    adds to db messages from users and Bot.

    :var
    data -> json dict for user's requst
    bot_actions -> bot_actions is a list of commands for bot actions
    """
    data = request.json
    if not isinstance(data, dict):
        return abort(400)
    if 'name' not in data or 'text' not in data:
        return abort(400)

    name = data['name']
    text = data['text']

    if not isinstance(name, str) or not isinstance(text, str):
        return abort(400)
    if name == '' or text == '':
        return abort(400)

    db.append({
        'name': name,
        'text': text,
        'time': time.time()
    })

    #  Bot's possible action
    bot_actions = ['/help', '/h', '/помощь',
                   '/number', '/n', '/numbers',
                   '/date', '/d',
                   '/w', '/weather', '/погода']
    if name in FLAG_WEATHER:  # Check if there was already a weather request
        db.append({
            'name': "al4an's bot",
            'text': bot_weather(text[1:]),
            'time': time.time()
        })
        FLAG_WEATHER.pop(name)
    if text in bot_actions:
        response = bot(text)
        db.append({
            'name': "al4an's bot",
            'text': response,
            'time': time.time()
        })
        if response.startswith('What city do you need?'):
            FLAG_WEATHER[name] = True

    return {'ok': True}


@app.route("/messages")
def get_messages():
    try:
        after = float(request.args['after'])
    except:
        return abort(400)

    messages = []
    for message in db:
        if message['time'] > after:
            messages.append(message)

    return {'messages': messages[:50]}


def bot(mission):
    """Main bot command function"""

    #  help command
    if mission in ['/help', '/h', '/помощь']:
        response = '/help:\n' \
                   'You can call next Bot functions:\n' \
                   '/help or /h or /помощь for this help\n\n' \
                   '/number or /n or /numbers for random interesting facts about numbers\n\n' \
                   '/date or /d for random interesting facts about date\n\n' \
                   '/w, /weather, /погода or weather information for any city'
        return response

    #  random number info command
    elif mission in ['/number', '/n', '/numbers']:
        response = requests.get('http://numbersapi.com/random/trivia?json')
        return response.json()['text']

    #  random date info command
    elif mission in ['/date', '/d']:
        response = requests.get('http://numbersapi.com/random/date?json')
        return response.json()['text']

    #  weather city question
    elif mission in ['/w', '/weather', '/погода']:
        response = 'What city do you need? (English only, "/city_name" format)'
        return response


def bot_weather(city):
    """For weather information request"""

    query = f'https://api.weatherbit.io/v2.0/current?city={city}&key={API_WEATHER_KEY}'
    try:
        response = requests.get(query).json()['data']
        print(response)
        temp = response[0]['temp']
        print(temp)
        description = response[0]['weather']['description']
        wind_speed = response[0]['wind_spd']
        wind_cdir = response[0]['wind_cdir_full']
        return f'Now in {city} - the temperature is {temp} degrees.\n' \
               f'The weather can be described as {description}.\n' \
               f'Wind force - {wind_speed} meters per second. The wind is {wind_cdir}.'
    except Exception:  # There is better to specify specific exceptions
        return 'There is no data for this city or it was written incorrectly.'


app.run()
