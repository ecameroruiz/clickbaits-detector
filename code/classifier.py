import gensim
import itertools as it
import json
import logging
import numpy as np
import os
import pandas as pd
import re
import sys
import time
import warnings

from bs4 import BeautifulSoup
from langdetect import detect
from scraper import get_features
from sklearn.externals import joblib

#########################################################
# CLICKBAIT DETECTOR
#########################################################

print '\n' + "*" * 100
url = raw_input("\nEnter Article URL: ")
print '\n' + "*" * 100

def classifier(url):
	"""Clickbait detector application"""
	article_properties, language = get_features(url)
	clf = joblib.load('../data/classifiers/classifier_' + language + '.pkl')
	df = pd.DataFrame([article_properties])
	probabilities = clf.predict_proba(df)

	# print str(article_properties)

	# print '\nConfidence Score => ' + str(float(probabilities[0][1])*100) + '%'

	if float(probabilities[0][1]) > 0.7:
	    print '\nPrediction => CLICKBAIT\n'
	    prediction = True
	else:
	    print '\nPrediction => NOT CLICKBAIT\n'
	    prediction = False

	return prediction

#########################################################
# MAIN
#########################################################

if __name__ == '__main__':
    classifier(url)

