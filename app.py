import sys
import argparse
import configparser
import json
import logging
from collections import OrderedDict

import torch
from flask import Flask, render_template, request
from flask_socketio import SocketIO


from drqa.reader import Predictorr

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s: [ %(message)s ]', '%m/%d/%Y %I:%M:%S %p')
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)


from stackoverflow import StackOverflowAPI as api
from preprocessing import Extractor

# ------------------------------------------------------------------------------
# Commandline arguments & init
# ------------------------------------------------------------------------------


parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='data/reader/multitask.mdl',
                    help='Path to model to use')
parser.add_argument('--tokenizer', type=str, default='spacy',
                    help=("String option specifying tokenizer type to use "
                          "(e.g. 'corenlp')"))
parser.add_argument('--no-cuda', action='store_true',
                    help='Use CPU only')
parser.add_argument('--gpu', type=int, default=-1,
                    help='Specify GPU device id to use')
parser.add_argument('--no-normalize', action='store_true',
                    help='Do not softmax normalize output scores.')
args = parser.parse_args()

args.cuda = not args.no_cuda and torch.cuda.is_available()
if args.cuda:
    torch.cuda.set_device(args.gpu)
    logger.info('CUDA enabled (GPU %d)' % args.gpu)
else:
    logger.info('Running on CPU only.')

predictor = Predictorr(args.model, args.tokenizer, num_workers=0,
                       normalize=False)
if args.cuda:
    predictor.cuda()


# ------------------------------------------------------------------------------
# Drop in to interactive mode
# ------------------------------------------------------------------------------


def process_doc(document, question, candidates=None, top_n=1):
    return predictor.predict(document, question, candidates, top_n)


app = Flask('Make StackOverflow Great Again!')


# DrQA = pipeline.DrQA(
#     cuda=True,
#     fixed_candidates=None,
#     reader_model=None,
#     ranker_config={'options': {'tfidf_path': None}},
#     db_config={'options': {'db_path': None}},
#     tokenizer='spacy' #args.tokenizer
# )


def process(question, n_question=10, n_answers=10, use_processing=True, candidates=None, top_n=1, n_docs=5):
    questions = api.search(question)
    questions = questions[:n_question]

    answers = api.answers([question.get("question_id") for question in questions])
    answers = answers[:n_answers]
    answers = [answer['body'] for answer in answers]

    if use_processing:
        processed_answers = [Extractor(answer).text for answer in answers]

    predictions = [process_doc(answer, question, top_n=1) for answer in processed_answers]

    print(predictions)

    data = list(zip(predictions, answers))

    # ROCKET SCIENCE
    data = filter(lambda it: len(it[0]['span']) > 5 and len(it[1]) < 512, data)
    # data.sort(key=lambda x: x[0]['score'], reverse=True)

    def to_chars(word, fw, lw):
        ls = list(map(len, word.split()))
        pos = sum(ls[:fw]) + fw
        len_ = sum(ls[fw: lw]) + (lw - fw - 1)
        return pos, len_

    res = []
    for p, a in data:
        try:
            e = Extractor(a)
            print('Preprocessed text: ', repr(e.text))
            print('Positions:', p['start'], p['end'])
            pos, len_ = to_chars(e.text, p['start'], p['end'])
            print('Answer: ', repr(e.text[pos: pos + len_]))
            highlighted = e.highlight(a, *to_chars(e.text, p['start'], p['end']))
            print('Original:', a)
            print('Highlighted:', repr(highlighted))
            res.append(highlighted)
        except Exception as e:
            logger.error(str(e))

    return res

    # return list(map(lambda x: x[1], data[:top_n]))

    # table = prettytable.PrettyTable(
    #     ['Rank', 'Answer', 'Doc', 'Answer Score', 'Doc Score']
    # )

    # for i, p in enumerate(predictions, 1):
    #     table.add_row([i, p['span'], p['doc_id'],
    #                    '%.5g' % p['span_score'],
    #                    '%.5g' % p['doc_score']])
    # # print('Top Predictions:')
    # # print(table)
    # # print('\nContexts:')
    # dicts = {}
    # for p, name in zip(predictions, ['first', 'second', 'third']):
    #     text = p['context']['text']
    #     start = p['context']['start']
    #     end = p['context']['end']
    #     # output = (text[:start] +
    #     #           colored(text[start: end], 'green', attrs=['bold']) +
    #     #           text[end:])
    #     mock =  {'first': text[:start],
    #                      'second': text[start: end],
    #                      'third': text[end:]}
    #     dicts[name] = mock
    #
    # return dicts


@app.route('/')
def hello_world():
    return render_template('index.html')


def get_paragraphs(q):
    return process(q, n_question=5, n_answers=30, use_processing=True, top_n=5)

    #
    # result = OrderedDict()
    #
    # for key in mock:
    #     result[key] = mock[key]
    #
    # return result


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
