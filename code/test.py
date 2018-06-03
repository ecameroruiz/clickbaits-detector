import csv
import gensim
import itertools as it
import json
import logging
import nltk
import numpy as np
import os
import pandas as pd
import pdb
import re
import re
import requests
import sys
import time
import unittest
import warnings

from bs4 import BeautifulSoup
from classifier import classifier
from comparator import split_dataset
from gensim import parsing
from os import makedirs
from os.path import exists
from os.path import join
from requests import get

#########################################################
# CRAWLER TEST
#########################################################


def crawler_test(language):
    """Testea modulo crawler"""
    DIR_INPUT = join('../data/articles/' + language)

    for root, dirs, filenames in os.walk(DIR_INPUT):
        for filename in filenames:
            with open(os.path.join(root, filename), 'r') as file:
                urls = [line.strip() for line in file]
                for url in urls:
                    if filename == 'clickbait.txt' and language == 'es':
                        assert 'lanetanoticias' in url or 'lasexta' in url or 'hola' in url or 'quemedices' in url or 'elle' in url or 'diezminutos' in url or 'cosmopolitan' in url or 'marca' in url or 'semana' in url, 'ERROR: URL no permitida ' + \
                            str(url) + ' en ' + filename + \
                            '; Idioma: ' + language
                    if filename == 'clickbait.txt' and language == 'en':
                        assert 'buzzfeed' in url or 'mtv' in url or 'mirror' in url or 'archive' in url or 'redd' in url or 'unv' in url or 'deslide' in url or 'msn' in url or 'imgur' in url or 'webcache' in url, 'ERROR: URL no permitida ' + \
                            str(url) + ' en ' + filename + \
                            '; Idioma: ' + language
                    if filename == 'trustworthy.txt' and language == 'es':
                        assert 'elmundo' in url or 'abc' in url or 'eleconomista' in url or 'elpais' in url or 'lavozdigital' in url, 'ERROR: URL no permitida ' + \
                            str(url) + ' en ' + filename + \
                            '; Idioma: ' + language
                        assert 'deporte' not in url and 'comparte' not in url and 'estilo' not in url and 'television' not in url and 'galery' not in url and 'viajar' not in url and 'futbol' not in url and 'famosos' not in url, 'ERROR: Palabra no permitida en ' + \
                            str(url) + '; archivo ' + \
                            filename + '; Idioma: ' + language
                    if filename == 'trustworthy.txt' and language == 'en':
                        assert 'theguardian' in url or 'nytimes' in url, 'URL no permitida ' + \
                            str(url) + ' en ' + filename + \
                            '; Idioma: ' + language
                        assert 'football' not in url and 'sport' not in url and 'style' not in url and 'video' not in url, 'ERROR: Palabra no permitida en ' + \
                            str(url) + '; archivo ' + \
                            filename + '; Idioma: ' + language


#########################################################
# SCRAPER TEST
########################################################

def scraper_test(language):
    """Testea modulo scraper"""
    DIR_INPUT = join('../data/datasets/')
    filename = join(DIR_INPUT + 'dataset_' + language + '.csv')

    df = pd.read_csv(filename)
    assert all(df['wordcount'] > 0), 'ERROR: Hay articulos vacios'

    articles = df.T.to_dict().values()

    for article in articles:
        if article['clickbait'] == True and language == 'es':
            assert 'lanetanoticias' in article['url'] or 'lasexta' in article['url'] or 'hola' in article['url'] or 'quemedices' in article['url'] or 'elle' in article['url'] or 'diezminutos' in article[
                'url'] or 'cosmopolitan' in article['url'] or 'marca' in article['url'] or 'semana' in article['url'], 'ERROR: URL no permitida ' + str(article['url']) + ' en ' + filename + '; Idioma: ' + language
        if article['clickbait'] == True and language == 'en':
            assert 'buzzfeed' in article['url'] or 'mtv' in article['url'] or 'mirror' in article['url'] or 'archive' in article['url'] or 'redd' in article['url'] or 'unv' in article['url'] or 'deslide' in article[
                'url'] or 'msn' in article['url'] or 'imgur' in article['url'] or 'webcache' in article['url'], 'ERROR: URL no permitida ' + str(article['url']) + ' en ' + filename + '; Idioma: ' + language
        if article['clickbait'] == False and language == 'es':
            assert 'elmundo' in article['url'] or 'abc' in article['url'] or 'eleconomista' in article['url'] or 'elpais' in article[
                'url'] or 'lavozdigital' in article['url'], 'ERROR: URL no permitida ' + str(article['url']) + ' en ' + filename + '; Idioma: ' + language
        if article['clickbait'] == False and language == 'en':
            assert 'theguardian' in article['url'] or 'nytimes' in article[
                'url'], 'URL no permitida ' + str(article['url']) + ' en ' + filename + '; Idioma: ' + language


#########################################################
# COMPARATOR TEST
#######################################################

def comparator_test(language):
    """Testea modulo comparator"""
    DIR_INPUT = join('../data/tables/' + language)
    dataset = pd.read_csv('../data/datasets/dataset_' + language + '.csv')

    all_headers = ['wordcount', 'images_number',
                   'links_number', 'title_keywords', 'body_keywords']

    all_the_features = []
    for r in range(1, len(all_headers) + 1):
        for subset in it.combinations(all_headers, r):
            all_the_features.append(list(subset))

    tables_number = -1
    for root, dirs, filenames in os.walk(DIR_INPUT):
        for filename in filenames:
            if 'DS_Store' not in filename:
                tables_number += 1

    assert len(all_the_features) - \
        1 == tables_number, 'ERROR: Numero incorrecto de tablas'


#########################################################
# CLASSIFIER TEST
#######################################################

def classifier_test(language):
    """Testea aplicacion classifier"""
    clickbait_article_en = {
        'url': 'https://www.buzzfeed.com/ellievhall/royal-wedding-prince-harry-meghan-markle?utm_term=.tkKBRgAg71#.voy896g6my',
        'links_number': 25,
        'wordcount': 2543,
        'body_keywords': 27,
        'clickbait': True
    }

    clickbait_article_es = {
        'url': 'http://www.lasexta.com/noticias/virales/video-que-desata-polemica-redes-club-premium-medicamento-enfermedadespijas_2015102957245b1d6584a81fd8829e43.html',
        'images_number': 3,
        'wordcount': 487,
        'body_keywords': 23,
        'clickbait': True
    }

    not_clickbait_article_en = {
        'url': 'https://www.theguardian.com/uk-news/2018/apr/12/caribbean-nations-demand-solution-to-illegal-immigrants-anomaly',
        'links_number': 1,
        'wordcount': 1163,
        'body_keywords': 0,
        'clickbait': False
    }

    not_clickbait_article_es = {
        'url': 'http://www.elmundo.es/madrid/2018/04/11/5ace5d01ca4741e7138b45e0.html',
        'images_number': 2,
        'wordcount': 640,
        'body_keywords': 1,
        'clickbait': False
    }

    if language == 'en':
        assert clickbait_article_en['clickbait'] == classifier(
            clickbait_article_en['url']), 'ERROR: Prediccion incorrecta'
        assert not_clickbait_article_en['clickbait'] == classifier(
            not_clickbait_article_en['url']), 'ERROR: Prediccion incorrecta'
    if language == 'es':
        assert clickbait_article_es['clickbait'] == classifier(
            clickbait_article_es['url']), 'ERROR: Prediccion incorrecta'
        assert not_clickbait_article_es['clickbait'] == classifier(
            not_clickbait_article_es['url']), 'ERROR: Prediccion incorrecta'


#########################################################
# MAIN
#########################################################

if __name__ == '__main__':

    try:
        warnings.filterwarnings("ignore")
        if crawler_test('en') == None:
            print 'crawler_test(en) passed'
        if crawler_test('es') == None:
            print 'crawler_test(es) passed'
        if scraper_test('en') == None:
            print 'scraper_test(en) passed'
        if scraper_test('es') == None:
            print 'scraper_test(es) passed'
        if comparator_test('es') == None:
            print 'comparator_test(es) passed'
        if comparator_test('en') == None:
            print 'comparator_test(en) passed'
        if classifier_test('es') == None:
            print 'classifier_test(es) passed'
        if classifier_test('en') == None:
            print 'classifier_test(en) passed'

    except Exception as e:
        print str(e)
