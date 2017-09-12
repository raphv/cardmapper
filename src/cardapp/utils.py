# -*- coding: utf-8 -*-

import re
from html import unescape
from bleach.sanitizer import Cleaner
from html5lib.filters.base import Filter

PARAGRAPH_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'li']
STYLE_TAGS = ['strong', 'em']

class ProcessDescription(Filter):

    def __iter__(self):
        for token in Filter.__iter__(self):
            if token['type'] == 'StartTag':
                continue
            if token['type'] in ['EndTag','EmptyTag']:
                token = {'type': 'Characters', 'data': '\n'}
            yield token

description_cleaner = Cleaner(
    tags = PARAGRAPH_TAGS + ['br'],
    filters = [ProcessDescription],
    strip = True
)

newline_re = re.compile('\n{2,}')

def process_description(txt):
    return unescape(
        newline_re.sub(
            '\n',
            description_cleaner.clean(txt)
        ).strip()
    )

class ProcessShortDescription(Filter):

    max_length = 200

    def __iter__(self):
        current_length = 0
        reached_max_length = False
        nesting_level = 0
        for token in Filter.__iter__(self):
            if reached_max_length and nesting_level == 0:
                return
            if token['type'] in ['StartTag','EndTag'] and token['name'] in PARAGRAPH_TAGS:
                token['name'] = 'p'
            if token['type'] == 'EndTag':
                nesting_level -= 1
            if token['type'] == 'StartTag':
                nesting_level += 1
            if token['type'] in ['Characters', 'SpaceCharacters']:
                if reached_max_length:
                    continue
                total_length = current_length + len(token['data'])
                if total_length > self.max_length:
                    reached_max_length = True
                    token['data'] = token['data'][:self.max_length-current_length] + '...'
                    token['type'] = 'Characters'
                current_length = total_length
            yield token


short_description_cleaner = Cleaner(
    tags = PARAGRAPH_TAGS + STYLE_TAGS,
    filters = [ProcessShortDescription],
    strip = True
)

def process_short_description(txt):
    return short_description_cleaner.clean(txt)
