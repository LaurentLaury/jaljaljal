import threading
import urllib

import numpy as np
import pandas as pd
from konlpy.tag import Twitter
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO

def clean_str(text):
    pattern = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)' # E-mail제거
    text = re.sub(pattern=pattern, repl='', string=text)
    pattern = '(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+' # URL제거
    text = re.sub(pattern=pattern, repl='', string=text)
    pattern = '([ㄱ-ㅎㅏ-ㅣ]+)'  # 한글 자음, 모음 제거
    text = re.sub(pattern=pattern, repl='', string=text)
    pattern = '<[^>]*>'         # HTML 태그 제거
    text = re.sub(pattern=pattern, repl='', string=text)
    pattern = '[^\w\s]'         # 특수기호제거
    text = re.sub(pattern=pattern, repl=' ', string=text)
    pattern = '\n'
    text = re.sub(pattern=pattern, repl=' ', string=text)
    return text

def get_text(place):
    review_data = pd.read_csv('review_text.csv', encoding='utf-8-sig')
    content_list = list(review_data["리뷰"].loc[review_data['장소']==place])
    content_to_str = content_list[0]
    clean_text = clean_str(content_to_str)

    twitter = Twitter()
    twitter_nouns = twitter.nouns(clean_text)
    text = ' '.join(twitter_nouns)
    return text