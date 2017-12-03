#!/usr/bin/env python3

import argparse
import logging

import torch
from termcolor import colored

from drqa.reader import Predictorr

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s: [ %(message)s ]', '%m/%d/%Y %I:%M:%S %p')
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)


from stackoverflow import StackOverflowAPI as api
from preprocessing import get_text

# ------------------------------------------------------------------------------
# Commandline arguments & init
# ------------------------------------------------------------------------------


parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='./data/reader/multitask.mdl',
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

args.cuda = False #not args.no_cuda and torch.cuda.is_available()
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


def process(document, question, candidates=None, top_n=1):
    return predictor.predict(document, question, candidates, top_n)


def print_result(predictions, n_top=1):
    predictions.sort(key=lambda x: x['score'], reverse=True)

    for i, p in enumerate(predictions, 1):
        if i > n_top:
            return

        text = p['text_tokens']
        span = p['span']
        score = p['score']
        start = p['start']
        end = p['end']

        print("Answer {0}: {1}\n( score = {2}, positions = ({3}, {4}) ):".format(i, span, score, start, end))
        output = text.slice(None, start).untokenize() + " " +\
                  colored(text.slice(start, end).untokenize(), 'green', attrs=['bold']) + " " + \
                 text.slice(end).untokenize()

        print("Context:\n" + output + '\n')



def console(use_processing=True, n_question=10, n_answers=10, n_top=3):
    while True:
        print("Question: ")

        question_text = input()

        questions = api.search(question_text)
        questions = questions[:n_question]

        answers = api.answers([question.get("question_id") for question in questions])
        answers = answers[:n_answers]
        answers = [answer['body'] for answer in answers]

        if use_processing:
            answers = [get_text(answer, delete_code=False) for answer in answers]

        predictions = [process(answer, question_text, top_n=1) for answer in answers]

        print_result(predictions, n_top)



if __name__ == '__main__':
    use_processing = True
    n_question = 3
    n_answers = 3
    n_top = 3

    console(use_processing, n_question, n_answers, n_top)

