import numpy as np
from collections import defaultdict
from flask_socketio import SocketIO
from flask import Flask, render_template, make_response, request, Response
import json
import configparser
import random
from collections import OrderedDict


app = Flask('Make StackOverflow Great Again!')


@app.route('/')
def hello_world():
    return render_template('index.html')


def get_paragraphs(q):
    mock = {'first:': {'text': 'mother was washing window frame',
                       'indices': ((0, 6), (19, 25))
                       },
            'second': {'text': 'mother was washing window frame 2',
                       'indices': ((7, 10), (11, 18))
                       },
            'third': {'text': 'mother was asdgasad  window frame 2',
                      'indices': ((7, 10), (11, 18))
                       },
            'fourth': {'text': 'mother was waag e window frame 2',
                       'indices': ((7, 10), (11, 18))
                       },
            'fifth': {'text': 'asdg agasgd mother was washing window frame 2',
                      'indices': ((7, 10), (11, 18))
                      }
            }

    keys = list(mock.keys())
    random.shuffle(keys)

    keys = random.sample(keys, 3)

    result = OrderedDict()

    for key in keys:
        result[key] = mock[key]

    return result


@app.route('/process_query', methods=['POST', 'GET'])
def process_query():
    q = request.args.get("text")
    result = get_paragraphs(q)
    return json.dumps(result)


def start_app(config):
    port = config['SERVER_INFO'].getint('PORT')
    ip = config['SERVER_INFO'].get('IP')
    
    socketio = SocketIO(app)
    socketio.run(app)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    start_app(config)
