import csv
import gensim
import itertools as it
import json
import logging
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
from os import makedirs
from os.path import exists
from os.path import join
from requests import get
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import NuSVC
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from threading import Thread

best_results = []

#########################################################
# COMPARATOR
#########################################################


def split_dataset(dataset, split_percentage, feature_headers, target_header):
    """Splits the dataset into training and testing data, chooses features and target headers"""

    X_train, X_test, y_train, y_test = train_test_split(
        dataset[feature_headers], dataset[target_header], train_size=split_percentage)

    print "Train_x Shape ::", X_train.shape
    print "Train_y Shape ::", y_train.shape
    print "Test_x Shape ::", X_test.shape
    print "Test_y Shape ::", y_test.shape

    return X_train, X_test, y_train, y_test


def classifiers(dataset, feature_headers, target, cross_val_split_number, language, split_percentage):
    """Compares the accuracy of different classifiers"""

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('../data/logs/comparator_log.txt')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    warnings.filterwarnings("ignore")
    X_train, X_test, y_train, y_test = split_dataset(
        dataset, split_percentage, feature_headers, target)

    classifiers = [
        KNeighborsClassifier(3),
        SVC(kernel="rbf", C=0.025, probability=True),
        NuSVC(probability=True),
        DecisionTreeClassifier(),
        RandomForestClassifier(),
        GaussianNB(),
    ]

    cols = ["Classifier", "Accuracy", "Clf", "Features"]
    results = pd.DataFrame(columns=cols)
    print str(feature_headers)
    logger.info(str(feature_headers) + ' ' + language)

    for clf in classifiers:
        clf.fit(X_train, y_train)
        name = clf.__class__.__name__
        predictions = clf.predict(X_test)
        scores = cross_val_score(clf, dataset[feature_headers], dataset[
                                 target], cv=cross_val_split_number)
        print scores
        logger.info(str(name) + ' ' + language + ' ' + str(scores))
        result_entry = pd.DataFrame(
            [[name, scores.mean() * 100, clf, feature_headers]], columns=cols)
        results = results.append(result_entry)

    with open('../data/tables/' + language + '/' + str(feature_headers) + '.csv', 'a+') as results_file:
        results.to_csv(results_file, columns=["Classifier", "Accuracy"])

    highest_accuracy = results["Accuracy"].max()

    for index, row in results.iterrows():
        if row["Accuracy"] == highest_accuracy:
            best_results.append({
                'score': row["Accuracy"],
                'classifier': row["Classifier"],
                'feature_headers': row["Features"],
                'clf': row['Clf']
            })

    return logger


def comparator(self, language):
    """Run comparator"""
    INPUT_PATH = join('../data/datasets/')
    filename = join(INPUT_PATH + 'dataset_' + language + '.csv')
    target = ["clickbait"]
    split_percentage = 0.7
    cross_val_split_number = 5

    start = time.time()

    dataset = pd.read_csv(filename)

    all_headers = ['wordcount', 'images_number',
                   'links_number', 'title_keywords', 'body_keywords']

    all_the_features = []
    for r in range(1, len(all_headers) + 1):
        for subset in it.combinations(all_headers, r):
            all_the_features.append(list(subset))

    for features_list in all_the_features:
        feature_headers = features_list
        logger = classifiers(dataset, feature_headers, target,
                             cross_val_split_number, language, split_percentage)

    highest_score = max(list((object['score'] for object in best_results)))

    for result in best_results:
        if result['score'] == highest_score:
            best_classifier = result

    logger.info('Best Classifier ' + '(' + language + ')' +
                ' :: ' + str(best_classifier))
    print "Best Classifier :: " + str(best_classifier)

    joblib.dump(best_classifier[
                'clf'], '../data/classifiers/classifier2_' + language + '.pkl')

    end = time.time()
    duration = end - start

    logger.info('Runtime: ' + str(duration))
    print 'Runtime: ' + str(duration)


#########################################################
# MAIN
#########################################################

if __name__ == '__main__':
    thread1 = Thread(target=comparator, args=('', 'en'))
    thread2 = Thread(target=comparator, args=('', 'es'))

    try:
        thread1.start()
        thread2.start()

    except Exception:
        print traceback.format_exc()
