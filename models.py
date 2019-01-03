import numpy as np 
from sklearn.ensemble import RandomForestClassifier

def static_clf(X,y):
    clf = RandomForestClassifier()
    clf.fit(X,y)
    return clf


def dynamic_clf(X,y,test_X):
    pass
    