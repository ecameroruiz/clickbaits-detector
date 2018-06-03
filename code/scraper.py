import csv
import emoji
import gensim
import itertools as it
import json
import logging
import newspaper
import numpy as np
import os
import pandas as pd
import re
import requests
import sys
import time
import unicodedata
import warnings

from bs4 import BeautifulSoup
from gensim import parsing
from langdetect import detect
from newspaper import Article
from newspaper import Source
from os import makedirs
from os.path import exists
from os.path import join
from requests import get
from threading import Thread

# -*- coding: utf-8 -*-


#########################################################
# SCRAPER ATTRIBUTES
#########################################################

def get_clean_body(html):
    """Gets body within the article (paragraphs and titles)"""
    html_soup = BeautifulSoup(html, 'html.parser')
    type(html_soup)
    article = html_soup.find('article')

    if article != None:
        paragraphs = article.find_all('p')
        titles = article.find_all('h3')
        body = ""
        for paragraph in paragraphs:
            body += paragraph.text
        for title in titles:
            body += title.text

        clean_body = re.sub(r"\s+", " ", body)
        return clean_body

    else:
        return ""


def links_number(html):
    """Gets body within the article (paragraphs and titles)"""
    html_soup = BeautifulSoup(html, 'html.parser')
    type(html_soup)
    article = html_soup.find('article')
    content = html_soup.find("div", {"id": "content"})

    links = []

    if article != None:
        paragraphs = article.find_all('p')
        titles = article.find_all('h3')

        for paragraph in paragraphs:
            links.append(paragraph.find('a'))

        for title in titles:
            links.append(title.find('a'))

        valid_links = []
        for link in links:
            if link != None:
                valid_links.append(link)

        return len(valid_links)
    elif content != None:
        paragraphs = content.find_all('p')
        titles = content.find_all('h3')

        for paragraph in paragraphs:
            links.append(paragraph.find('a'))

        for title in titles:
            links.append(title.find('a'))

        valid_links = []
        for link in links:
            if link != None:
                valid_links.append(link)

        return len(valid_links)
    else:
        return 0


def images_number(html):
    """Gets number of images within the body of an article"""
    html_soup = BeautifulSoup(html, 'html.parser')
    type(html_soup)
    article = html_soup.find('article')
    content = html_soup.find("div", {"id": "content"})
    if article != None:
        return len(article.find_all('img'))
    elif content != None:
        return len(content.find_all('img'))
    else:
        return 0


def process_text(texto, language):
    """Prepares text for processing"""
    if language == 'es':
        texto = ''.join((c for c in unicodedata.normalize(
            'NFD', unicode(texto)) if unicodedata.category(c) != 'Mn'))
    text = texto.lower()
    text = gensim.parsing.preprocessing.strip_punctuation2(text)
    text = gensim.parsing.preprocessing.strip_numeric(text)
    text = gensim.corpora.textcorpus.strip_multiple_whitespaces(text)
    return text


def keywords(texto, language):
    """Counts occurrances of typical clickbait words and patterns in the article title"""

    if language == 'en':
        words_list = ['amazing', 'incredible', 'beauty', 'fitness', 'scandal', 'shocking', 'tips', 'lifehacks', 'relationship', 'love', 'cheat', 'we ll tell you', 'you need',
                      'breakup', 'broke up', 'you won t believe', 'what happens next', 'quiz', 'memes', 'will make you', 'crush', 'recipes', 'didn t know', 'creepy', 'can you guess',
                      'what character', 'tv moments', 'tv', 'tricks for', 'sexy', 'sexual', 'epic', 'hype', 'pregnant', 'husband', 'wife', 'boyfriend', 'here s why', 'here s how', 'here s everything',
                      'girlfriend', 'show off', 'controversial', 'reveal', 'new look', 'favourites', 'wedding', 'this happened', 'what happened', 'nude', 'naked', 'celeb', 'blow your mind',
                      'claims', 'lose weight', 'marriage', 'fashion', 'divorce', 'family', 'photos that', 'omg', 'ways to', 'iconic', 'famous', 'celebrity', 'hilarious', 'you never knew',
                      'trailer', 'will help you', 'promotional', 'porn', 'discount', 'romantic', 'tears', 'check out', 'Netflix', 'YouTube', 'Apple', 'social media', 'instagram', 'literally',
                      'twitter', 'snapchat', 'facebook', 'hashtag', 'trending', 'retweets', 'insta stories', 'trending topics', 'notifications', 'filters', 'selfies', 'surprise you',
                      'followers', 'followed', 'unfollowed', 'timeline', 'tweet', 'tweeted', 'newsfeed', 'meme', 'snap', 'tinder', 'scroll', 'click', 'fans', 'shared', 'viral', 'inbox', 'texting', 'influencer', 'internet',
                      'crazy', 'spoiler', 'subscribe', 'sensual', 'leave you', 'laughing', 'did you know', 'youtuber', 'outrage', 'upsetting', 'talent show', 'reality show', 'heartbreaking']

    else:
        words_list = ['increibles', 'razones', 'consejos', 'belleza', 'enamorado', 'ruptura', 'sorprendera', 'lo que paso despues', 'no te creeras', 'acierto', 'desternillante', 'conmueve',
                      'recomendaciones', 'presume', 'quiz', 'emotivo', 'emotiva', 'polemica', 'meme', 'memes', 'recetas', 'que personaje', 'trucos', 'no sabias', 'llanto', 'embarazada', 'sorprenden', 'sorprendentes', 'vestido',
                      'marido', 'esposa', 'novio', 'novia', 'novias', 'controversia', 'sexy', 'sexual', 'sensual', 'desvela', 'nuevo look', 'favoritos', 'boda', 'ataca', 'bronca', 'test', 'impactantes', 'filtro',
                      'desnuda', 'famoso', 'casado', 'adelgazar', 'matrimonio', 'divorcio', 'familia', 'corazon', 'adictivo', 'fitness', 'moda', 'ligar', 'temporada', 'spoiler', 'carta', 'reto', 'recuerdas', 'diviertete'
                      'futbol', 'fotos que', 'imagenes que', 'canciones', 'datos graficos', 'tendencias', 'ideas utiles', 'curiosidades', 'famosos', 'arrasa', 'trailer', 'dieta', 'tu personalidad', 'zasca', 'pudor',
                      'te ayudara', 'te hara', 'promocional', 'descuento', 'romantico', 'pareja', 'Netflix', 'YouTube', 'hashtag', 'retuitear', 'insta', 'indignacion', 'altercado', 'reaccion', 'viraliza', 'descubre como',
                      'insta stories', 'trending topics', 'notificaciones', 'filtros', 'selfies', 'redes sociales', 'red social', 'redes', 'follower', 'seguidores', 'timeline', 'mal gusto', 'venganza', 'furor',
                      'tweet', 'tuit', 'tuits', 'newsfeed', 'snap', 'porno', 'tinder', 'scroll', 'click', 'fans', 'compartido', 'viral', 'reproducciones', 'whatsapp', 'influencer', 'Apple', 'pilla', 'video', 'maquillaje',
                      'social media', 'instagram', 'twitter', 'snapchat', 'facebook', 'trending', 'retweet', 'notifications', 'filters', 'enloquece', 'paraliza', 'internet', 'gimnasio', 'brutal', 'erotico', 'destapa',
                      'red', 'internautas', 'asi puedes', 'imagenes que', 'asombrosos', 'enlace', 'talent show', 'reality show', 'rumores', 'sentimental', 'matrimonial', 'youtuber', 'emociona', 'emocionante']

    text = texto.decode('utf-8', 'ignore')

    symbols = ['!', '@', '#']
    symbols_number = 0
    for symbol in symbols:
        symbols_number += int(text.count(symbol))

    emojis_number = 0
    for character in text:
        if character in emoji.UNICODE_EMOJI:
            emojis_number += 1

    text = process_text(text, language)

    count = 0
    for word in words_list:
        if re.search(word.lower(), text):
            count += 1

    total_count = int(count) + int(symbols_number) + int(emojis_number)
    return total_count

#########################################################
# SCRAPER DOWNLOADER
########################################################


def scraper(self, language):
    """Scrap fata from URLs"""

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('../data/logs/scraper_log.txt')
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    DIR_INPUT = join('../data/articles/' + language)
    DIR_OUTPUT = join('../data/datasets/')
    if not os.path.exists(DIR_OUTPUT):
        makedirs(DIR_OUTPUT)

    start = time.time()
    logger.info('Request received for scraper; Language: ' + language)
    logger.info('Output Directory: ' + DIR_OUTPUT)

    fname_input = join(DIR_INPUT + 'clickbait_' + language)

    articles = []

    for root, dirs, filenames in os.walk(DIR_INPUT):
        for filename in filenames:
            with open(os.path.join(root, filename), 'r') as file:
                urls = [line.strip() for line in file]
                for url in urls:
                    try:
                        sys.tracebacklimit = 0
                        article = {}
                        content = Article(url)
                        content.download()
                        content.parse()
                        content.nlp()
                        html = content.html
                        try:
                            title = content.title.encode('utf-8', 'ignore')
                        except UnicodeError:
                            title = content.title
                        try:
                            body_newspaper = content.text.encode(
                                'utf-8', 'ignore')
                            body_newspaper = re.sub(
                                r"\s+", " ", body_newspaper)
                            body_bs = get_clean_body(
                                html).encode('utf-8', 'ignore')
                        except UnicodeError:
                            body_newspaper = content.text
                            body_newspaper = re.sub(
                                r"\s+", " ", body_newspaper)
                            body_bs = get_clean_body(html)

                        if len(body_newspaper.split()) > len(body_bs.split()):
                            body = body_newspaper
                        else:
                            body = body_bs

                        wordcount = len(body.split())
                        if wordcount > 0:
                            warnings.filterwarnings("ignore")
                            article.update({
                                'url': url,
                                'language': language,
                                'wordcount': wordcount,
                                'images_number': images_number(html),
                                'links_number': links_number(html),
                                'body_keywords': keywords(body, language),
                                'title_keywords': keywords(title, language)
                            })
                            if filename == 'clickbait.txt':
                                article['clickbait'] = True
                            else:
                                article['clickbait'] = False
                            articles.append(article)
                            logger.info(article)
                    except Exception as e:
                        logger.info('There was an error: ' + str(e))
                        continue

    fname_csv = join(DIR_OUTPUT + 'dataset_' + language + '.csv')

    df = pd.DataFrame(articles)
    df.to_csv(fname_csv)
    logger.info('Number of elements of ' + fname_csv + ' is: ' + str(len(df)))

    end = time.time()
    duration = end - start
    logger.info('Runtime with input: ' + language +
                ', ' + ', was => ' + str(duration))


def get_features(url):
    """Get article attributes"""

    try:
        sys.tracebacklimit = 0
        article = {}
        content = Article(url)
        content.download()
        content.parse()
        content.nlp()
        html = content.html

        try:
            title = content.title.encode('utf-8', 'ignore')
            language = detect(title)
        except UnicodeError:
            title = content.title
            language = detect(title)
            
        print '\nDetected Language => ' + language

        if language != 'es' and language != 'en':
            sys.exit("\nLenguaje no permitido\n")

        try:
            body_newspaper = content.text.encode('utf-8', 'ignore')
            body_newspaper = re.sub(r"\s+", " ", body_newspaper)
            body_bs = get_clean_body(html).encode('utf-8', 'ignore')
        except UnicodeError:
            body_newspaper = content.text
            body_newspaper = re.sub(r"\s+", " ", body_newspaper)
            body_bs = get_clean_body(html)

        if len(body_newspaper.split()) > len(body_bs.split()):
            body = body_newspaper
        else:
            body = body_bs

        wordcount = len(body.split())

        warnings.filterwarnings("ignore")

        if language == 'es':
            article['wordcount'] = wordcount
            article['body_keywords'] = keywords(body, language)
            article['images_number'] = images_number(html)

        else:
            article['wordcount'] = wordcount
            article['links_number'] = images_number(html)
            article['body_keywords'] = keywords(body, language)

        return article, language

    except Exception as e:
        sys.exit("\nSe ha producido un error procesando el articulo\n")


#########################################################
# MAIN
#########################################################

if __name__ == '__main__':
    thread1 = Thread(target=scraper, args=('', 'en'))
    thread2 = Thread(target=scraper, args=('', 'es'))

    try:
        warnings.filterwarnings("ignore")
        thread1.start()
        thread2.start()

    except Exception:
        print traceback.format_exc()
