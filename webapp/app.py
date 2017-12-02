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
    mock = {'first': {'first': 'mother was washing window frame ',
                       'second': 'blablabla',
                       'third': ' bye bye'
                       },
            'second': {'first': 'mother ',
                       'second': 'was',
                       'third': ' washing window frame'
                       },
            'third': {'first': 'mother was  ',
                       'second': 'washing',
                       'third': ' window frame'
                       }
            }

    result = OrderedDict()

    for i in range(100):
        mock[str(i)] = mock['first']

    for key in mock:
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
