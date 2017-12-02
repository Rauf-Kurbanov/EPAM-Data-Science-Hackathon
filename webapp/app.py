import prettytable

from flask_socketio import SocketIO
from flask import Flask, render_template, make_response, request, Response
import json
import configparser
from collections import OrderedDict
import logging

from drqa import pipeline

app = Flask('Make StackOverflow Great Again!')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s: [ %(message)s ]', '%m/%d/%Y %I:%M:%S %p')
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)

logger.info('Initializing pipeline...')
DrQA = pipeline.DrQA(
    cuda=True,
    fixed_candidates=None,
    reader_model=None,
    ranker_config={'options': {'tfidf_path': None}},
    db_config={'options': {'db_path': None}},
    tokenizer='spacy' #args.tokenizer
)


def process(question, candidates=None, top_n=1, n_docs=5):

    predictions = DrQA.process(
        question, candidates, top_n, n_docs, return_context=True
    )
    table = prettytable.PrettyTable(
        ['Rank', 'Answer', 'Doc', 'Answer Score', 'Doc Score']
    )
    for i, p in enumerate(predictions, 1):
        table.add_row([i, p['span'], p['doc_id'],
                       '%.5g' % p['span_score'],
                       '%.5g' % p['doc_score']])
    # print('Top Predictions:')
    # print(table)
    # print('\nContexts:')
    dicts = {}
    for p, name in zip(predictions, ['first', 'second', 'third']):
        text = p['context']['text']
        start = p['context']['start']
        end = p['context']['end']
        # output = (text[:start] +
        #           colored(text[start: end], 'green', attrs=['bold']) +
        #           text[end:])
        mock =  {'first': text[:start],
                         'second': text[start: end],
                         'third': text[end:]}
        dicts[name] = mock

    return dicts


@app.route('/')
def hello_world():
    return render_template('index.html')


def get_paragraphs(q):
    mock = process(q, top_n=3)
    print(mock)

    result = OrderedDict()

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
