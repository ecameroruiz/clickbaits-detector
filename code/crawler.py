import json
import logging
import newspaper
import os
import requests
import sys
import time
import warnings

from bs4 import BeautifulSoup
from newspaper import Article
from newspaper import Source
from os import makedirs
from os.path import exists
from os.path import join
from threading import Thread
from time import sleep

#########################################################
# CRAWLER
#########################################################


def google_news(self, args):
	"""Get articles from Google News API"""

	PAGES = 100
	MY_API_KEY = '34f29f257c95419a926baeb9ffd99e4b'
	API_ENDPOINT = 'https://newsapi.org/v2/everything'

	trustworthy_sources_es = ['el-mundo']
	trustworthy_sources_en = ['the-guardian-uk', 'the-new-york-times']
	clikbait_sources_en = ['buzzfeed', 'mtv-news']

	def get_urls(language, source, category):
		"""Save URLs"""

		my_params = {
			'sources': source,
			'apiKey': MY_API_KEY,
		    'language': language,
		    'pageSize': "100"
		}

		resp = requests.get(API_ENDPOINT, my_params)
		data = resp.json()
		outFile = open('../data/articles/' + language +
		               '/' + category + '.txt', 'a+')
		links = []
		for i in range(1, PAGES):
			try:
				my_params['page'] = str(i)
				resp = requests.get(API_ENDPOINT, my_params)
				data = resp.json()
				for article in data['articles']:
					if language == 'en' and source in trustworthy_sources_en:
						if 'football' not in str(article['url']) and 'sport' not in str(article['url']) and 'style' not in str(article['url']) and 'video' not in str(article['url']):
							outFile = open('../data/articles/' + language +
							               '/' + category + '.txt', 'a+')
							print >>outFile, article['url']

					elif language == 'es' and source in trustworthy_sources_es:
						if 'deporte' not in str(article['url']) and 'comparte' not in str(article['url']) and 'estilo' not in str(article['url']) and 'television' not in str(article['url']) and 'galery' not in str(article['url']) and 'viajar' not in str(article['url']) and 'futbol' not in str(article['url']) and 'famosos' not in str(article['url']):
							outFile = open('../data/articles/' + language +
							               '/' + category + '.txt', 'a+')
							print >>outFile, article['url']
					else:
						outFile = open('../data/articles/' + language +
						               '/' + category + '.txt', 'a+')
						print >>outFile, article['url']
			except:
				if resp.status_code == 429:
					time.sleep(21600)
					continue
				else:
					pass

	# Run script

	for source in trustworthy_sources_es:
	    get_urls('es', source, 'trustworthy')

	for source in clikbait_sources_en:
	    get_urls('en', source, 'clickbait')

	for source in trustworthy_sources_en:
	    get_urls('en', source, 'trustworthy')


def newspapers(self, args):
	"""Get articles using Newspaper Library"""
	clikbait_sources_en = ['https://www.mirror.co.uk']
	trustworthy_sources_es = ['https://abc.es/',
	    'http://eleconomista.es/', 'https://elpais.com/']
	clikbait_sources_es = ['https://www.hola.com',
	    'http://quemedices.diezminutos.es']

	def get_urls(language, source, category):
		"""Save URLs"""
		try:
			paper = newspaper.build(source, memoize_articles=False)
			for article in paper.articles:
				try:
					if category == 'trustworthy':
						if 'deporte' not in str(article.url) and 'comparte' not in str(article.url) and 'estilo' not in str(article.url) and 'television' not in str(article.url) and 'galery' not in str(article.url) and 'viajar' not in str(article.url) and 'gente' not in str(article.url):
							outFile = open('../data/articles/' + language +
							               '/' + category + '.txt', 'a+')
							print >> outFile, article.url
					else:
						outFile = open('../data/articles/' + language +
						               '/' + category + '.txt', 'a+')
						print >> outFile, article.url

				except:
					continue
		except:
			pass

	# Run script

	for source in clikbait_sources_es:
	    get_urls('es', source, 'clickbait')

	for source in trustworthy_sources_es:
	    get_urls('es', source, 'trustworthy')

	for source in clikbait_sources_en:
	    get_urls('en', source, 'clickbait')


def raw_crawling(self, args):
	"""Get articles from different sources by scraping its web pages"""

	PAGES = 500
	file_output_en = '../data/articles/en/clickbait.txt'
	file_output_es = '../data/articles/es/clickbait.txt'

	def LNN():
		"""Save URLs"""
		base_url = 'https://www.lanetanoticias.com/viral/'
		for i in range(1, PAGES):
			try:
				resp = requests.get(base_url + 'page/' + str(i))
				soup = BeautifulSoup(resp.text, 'html.parser')
				type(soup)
				news = soup.find("div", {
				                 "class": "widget-content feed-widget-content widget-content-LANETANOTICIAS-archive-blog-rolls"})

				divs = []

				for title in news:
				    divs.append(title.find_all('h3'))

				links = []

				outFile = open(file_output_es, 'a+')
				for div in divs:
				    for a in div:
				        print >> outFile, a.next_element['href']

			except:
				continue

	def LSN():
		"""Save URLs"""
		domain = 'http://www.lasexta.com/noticias/virales/'
		base_url = 'http://www.lasexta.com/noticias/virales'

		for i in range(1, PAGES):
			try:
				resp = requests.get(base_url + '-' + str(i) + '/')
				soup = BeautifulSoup(resp.text, 'html.parser')
				type(soup)
				body = soup.find("ul", {"class": "listado-noticias"})

				links = []
				for a in body.find_all('a', href=True):
					if domain in str(a['href']):
						outFile = open(file_output_es, 'a+')
						print >> outFile, a['href']
			except:
				continue

	def reddit():
		"""Save URLs"""
		base_url = 'http://reddit.com/r/savedyouaclick/new/.json'
		links = []

		for i in range(0, int(PAGES)):  # 25 posts per page
		    try:
		        resp = requests.get(base_url, headers={'user-agent': 'Mozilla/5.0'})
		        data = resp.json()
		        for post in data['data']['children']:
		            if 'archive.is' not in post['data']['url'] and 'streamable' not in post['data']['url']:
		                outFile = open(file_output_en, 'a+')
		            	print >>outFile, post['data']['url']
		        next_page_url = str(base_url) + '?&after=' + data['data']['after']
		        next_page = requests.get(next_page_url, headers={
		                                 'user-agent': 'Mozilla/5.0'})
		        data = next_page.json()
		    except:
		        continue

	# Run script

	LNN()
	LSN()
	reddit()


#########################################################
# MAIN
#########################################################

if __name__ == '__main__':
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler('../data/logs/crawler_log.txt')
	fh.setLevel(logging.DEBUG)
	logger.addHandler(fh)

	thread1 = Thread(target=raw_crawling, args=('', ''))
	thread2 = Thread(target=newspapers, args=('', ''))
	thread3 = Thread(target=google_news, args=('', ''))

	try:
		warnings.filterwarnings("ignore")
	    thread1.start() 
	    thread2.start()
		thread3.start()

	except Exception:
	    logger.debug(str(traceback.format_exc()))


