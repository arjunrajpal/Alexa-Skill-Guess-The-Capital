from flask import Flask
from flask_ask import Ask, statement, question, session
from bs4 import BeautifulSoup
import requests
import json
import random

app = Flask(__name__)
ask = Ask(app, '/play')

country_capital_list = []
with open('country_capital_list.json') as f:
    country_capital_list = json.load(f)

@app.route('/')
def hello_world():
    return "Ready"


def get_country_capitals():
    url = "https://geographyfieldwork.com/WorldCapitalCities.htm"

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) '
                         'Chrome/23.0.1271.64 Safari/537.11'}

    req = requests.get(url, headers=hdr, verify=True)

    res = req.text

    soup = BeautifulSoup(res, 'html.parser')

    table = soup.find('table', attrs={'class', 'sortable'})

    trs = table.find_all('tr')

    country_capital_list = []

    for i in range(1, len(trs)-1):
        tds = trs[i].find_all('td')
        country = tds[0].text
        capital = tds[1].text

        country_capital_list.append({'country': country, 'capital': capital})

    with open('country_capital_list.json', 'w') as f:
        json.dump(country_capital_list, f)

    return country_capital_list


@ask.launch
def launched():
    session.attributes['count'] = 0
    session.attributes['score'] = 0
    random.shuffle(country_capital_list)
    return question("Hi, would you like to play Guess the capital ?")


@ask.intent('YES')
def play():
    country = country_capital_list[session.attributes['count']]['country']
    capital = country_capital_list[session.attributes['count']]['capital']

    session.attributes['count'] += 1
    session.attributes['country'] = country
    session.attributes['correct-answer'] = capital

    question_string = ""
    if session.attributes['count'] == 1:
        question_string = "Ok then, Let's start ! What's the capital of " + country + '?'
    else:
        question_string = "What's the capital of " + country + "?"

    return question(question_string)


@ask.intent('ANSWER')
def play_continue(capital):
    if session.attributes['count'] != 0 and (capital.lower() == session.attributes['correct-answer'].lower() or capital.replace(".", "").lower() == session.attributes['correct-answer'].lower()):
        session.attributes['score'] += 1

        question_string = 'Correct answer!'

        if session.attributes['score'] == 201:
            return statement('<speak><prosody pitch="high">Congratulations !!! You have won ! </prosody>Well done ! Thank you for playing Guess the capital. Have a nice day !</speak>')
        elif session.attributes['score'] % 5 ==0:
            question_string += ' You are doing great ! Your current score is ' + str(session.attributes['score']) + '.'

        question_string += ' Shall we continue ?'

    elif session.attributes['count'] == 0:
        question_string = 'Sorry, your answer was wrong, correct answer is ' + session.attributes['correct-answer'] + \
                          '. Want to play again ?'

    else:
        question_string = 'Sorry, your answer was wrong, correct answer is ' + session.attributes['correct-answer'] + \
                          '. Your final score is ' + str(session.attributes['score']) + '. Want to play again ?'
        session.attributes['count'] = 0
        session.attributes['score'] = 0
        random.shuffle(country_capital_list)

    return question(question_string)


@ask.intent('NO')
def no():
    return statement('Thank you for playing Guess the capital. Have a nice day !')


@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement('Thank you for playing Guess the capital. Have a nice day !')


@ask.intent('AMAZON.HelpIntent')
def help():
    return question('This skill asks you the capitals of different countries in the world. Reply with a Yes to play '
                    'the game and No to exit the skill. Would you like to start?')


@ask.intent('AMAZON.StopIntent')
def stop():
    return statement('Thank you for playing Guess the capital. Have a nice day !')


@ask.intent('AMAZON.FallbackIntent')
def fallback():
    return question("Sorry didn't quite get it, please speak again !")


if __name__ == '__main__':
    app.run(debug=True, port=5000)

