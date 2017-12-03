import re
import copy
import warnings
import pandas as pd

from tqdm import tqdm
from lazy import lazy
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from IPython.core.display import HTML
from sklearn.base import BaseEstimator, TransformerMixin


# Switch warning off for `bs4`.
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')


class Extractor:
    def __init__(self, raw_text, delete_code=True, code_replacer='CODE',
                 delete_r=True, treshold=0.9):
        self.raw_text = raw_text
        self.delete_code = delete_code
        self.code_replacer = code_replacer
        self.delete_r = delete_r
        self.treshold = treshold

    @lazy
    def text(self):
        text = self._replace_unescape(self.raw_text)
        self._soup = BeautifulSoup(text, 'lxml')

        self._codes = []
        new_soup = copy.copy(self._soup)
        self._change_code(new_soup)

        text = str(new_soup.get_text())
        return text.replace('\r', '') if self.delete_r else text

    def highlight(self, text, pos, len_):
        # `Split('CODE')`
        answer = self.text[pos: pos + len_]
        # full, parts = [], []
        # for pans in answer.split():
        #     if pans != self.code_replacer:
        #         parts.append(pans)
        #     else:
        #         if len(parts):
        #             full.append(' '.join(parts))
        #             parts = []
        # if len(parts):
        #     full.append(' '.join(parts))
        #     parts = []
        #
        full = [text.strip() for text in answer.split(self.code_replacer) if any(word.isalpha() for word in text.split())]
        print('Full: ', full)

        for p_tag in self._soup.find_all('pre'):
            if len(p_tag.find_all('code')):
                p_tag.attrs['class'] = 'lang-java prettyprint prettyprinted'

        if len(full):
            pattern = re.compile(r'\b(' + '|'.join(full) + r')\b')
            return re.sub(pattern, r"<span style='background-color:yellow;'>\1</span>", text)
        else:
            return text

    def _change_code(self, tag):
        for child in tag.findChildren():
            if child.name == 'code':
                code = child.text
                self._codes.append(code)
                if self.delete_code: child.replaceWith(self.code_replacer)

    @staticmethod
    def _replace_unescape(text, unescape_dict={'&lt;': '<', '&gt;': '>', '&amp;': '&'}):
        def round_(text):
            for k, v in unescape_dict.items():
                text = text.replace(k, v)
            return text

        old_text, text = text, round_(text)
        while old_text != text:
            old_text, text = text, round_(text)

        return text

class Preprocessor(BaseEstimator):
    def __init__(self):
        pass

    def transform(self, X):
        return [Extractor(x).text for x in X]
