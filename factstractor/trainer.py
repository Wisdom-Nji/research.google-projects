#!/bin/python

import spacy
import csv
import pickle
import sys
from sklearn import svm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

def get_training_data( csvfilename, col_training_data, col_training_data_labels ):
    csvfile = open( csvfilename, "r" )
    csvfile_reader = csv.DictReader( csvfile, delimiter=',' )

    line_counter = 0
    training_data = []
    training_data_labels = []

    for row in csvfile_reader:
        training_data.append( row[col_training_data] )
        training_data_labels.append( row[col_training_data_labels] )
        line_counter += 1

    print(f"$ len(training_data):{len(training_data)}\n$ len(training_data_labels):{len(training_data_labels)}")

    return {"data": training_data, "labels": training_data_labels}


def save_fit_data( fit_dump, filename ):
    writefile = open( filename, "wb+")
    pickle.dump( fit_dump, writefile )
    writefile.close()
    print(f">> Trained Data Saved: [{filename}]")


def train( labelled_dataset, nlp ):
    print(">> Vectorizing dataset...")
    # split the data before vectorizing it
    data = labelled_dataset["data"]
    data_label = labelled_dataset["labels"]

    arr_data = np.array( data ).reshape(-1, 1);
    arr_data_label = np.array( data_label )
    print(f">> Done converting\n>> Splitting data for split testing")

    # splitting data for evaluation
    data_train, data_evaluate, data_label_train, data_label_evaluate = train_test_split(arr_data, arr_data_label, stratify=data_label)
    print(f">> data_train_len: {len(data_train)}")
    
    '''
    print(f"intercept_: {model.intercept_}")
    print(f"coef_: {model.coef_}")
    print(f"model score - training: {model.score(data_train, data_evaluate)}")
    print(f"model score - test: {model.score(data_evaluate, data_label_evaluate)}")
    '''

    kernel = input(f">> Choose your kernel!\n1. linear(V)\n2. rbf(V)\n3. linear\n4. rbf\n(kernel)$_ ")
    verbose = True
    if not kernel:
        kernel = "1" 
        print(f">> Defaulting kernel to {kernel}")
    # clf_svm_wv = svm.SVC(kernel='linear')
    if kernel == "1":
        kernel = "linear"
        print(f">> Selected Kernel = {kernel} with verbose")
    elif kernel == "2":
        kernel = "rbf"
        print(f">> Selected Kernel = {kernel} with verbose")
    elif kernel == "3":
        kernel = "linear"
        verbose = False
        print(f">> Selected Kernel = {kernel} no verbose")
    elif kernel == "4":
        kernel = "rbf"
        verbose = False
        print(f">> Selected Kernel = {kernel} no verbose")

    # TODO: Flatten 2D array to 1D here before going further
    data = data_train.flatten()
    '''
    for text in data:
        text = str(text)
        print(f">>TYPEOF_TEXT: {type(text)}")
        print(f">>TEXT: {nlp(text)}")
    '''
    docs_dt = [nlp(str(text)) for text in data]

    # docs = [nlp(text) for text in labelled_dataset["data"]]
    dt_wv = [x.vector for x in docs_dt]

    # model = LinearRegression().fit( data_train, data_evaluate )

    clf_svm_wv = svm.SVC(kernel=kernel, verbose=verbose)
    clf_svm_wv.fit(dt_wv, data_label_train.flatten())
    print(f"\n>> Kernel: {kernel}\n>> Classes: { clf_svm_wv.classes_ }")

    # evaluation
    '''
    print(">> Done training, evaluating...")
    evaluate( clf_svm_wv, "data_gathering/data/training.csv")
    '''
    evaluate( clf_svm_wv, data_evaluate.flatten(), data_label_evaluate.flatten() )

    return clf_svm_wv

def evaluate( clf_svm_wv, data, label ):
    print("\n>> Evaluating Score...")
    score = {}
    counted_cases = {}
    for _class in clf_svm_wv.classes_:
        score[_class] = 0
        counted_cases[_class] = 0

    for i in range(len(data)):
        test_input = [str(data[i])]
        test_docs = [nlp(text) for text in test_input]
        test_input_vectors = [x.vector for x in test_docs]

        prediction = clf_svm_wv.predict( test_input_vectors )[0]
        if prediction == str(label[i]):
            score[prediction] += 1
        counted_cases[str(label[i])] += 1

    for _count in counted_cases:
        print(f"[counted|{_count}]: {counted_cases[_count]}")

    av_score_ranking = 0
    for _score in score:
        percentage = (score[_score]/counted_cases[_score]) * 100
        print(f"[score|{_score}]: {score[_score]} ... {round(percentage, 2)}%")
        av_score_ranking += percentage

    print(f"[=] Average score ranking >> {round(av_score_ranking/len(score.keys()), 2)}%")

if __name__ == "__main__":
    DATASET_FILENAME = "data_gathering/data/dataset.csv"

    if len(sys.argv) < 2:
        print(">> Usage: --predict <input>|--train")

    elif sys.argv[1] == "--train":
        nlp = spacy.load("en_core_web_lg")
        # nlp = spacy.load("en_core_web_md")
        print("(training)$_ ")

        # acquire data
        print(">> Getting training data....")
        labelled_dataset = get_training_data(DATASET_FILENAME, "text", "type")

        # train
        clf_svm_wv = train( labelled_dataset, nlp )

        # save file
        save_filename = "trained_savefiles/trained_facts_classifier.obj"
        try:
            save_filename = sys.argv[2]
        except IndexError:
            print(f">> Resulting save to default file: {save_filename}")
        else:
            print(f">> Saving to: {save_filename}")

        save_fit_data( clf_svm_wv, save_filename )
