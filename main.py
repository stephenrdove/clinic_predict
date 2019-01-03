import numpy as np 
import pandas as pd 
from models import static_clf, dynamic_clf
from sklearn.metrics import f1_score

def load_data(filepath,mode='static',label='ed'):
    data = pd.read_csv(filepath)
    data = data.sample(frac=1)
    # data.reset_index(drop=True) <-- this will reset shuffle

    X = [datum.split(' ') for datum in data[mode]]
    y = [label for label in data[label]]

    return X, y

def static_test(X,y,test_X):
    clf = static_clf(X,y)
    static_probs = clf.predict_proba(test_X)
    return static_probs

def dynamic_test(X,y,test_X):
    dynamic_probs = dynamic_clf(X,y,text_X)
    return dynamic_probs

def model_probs(stat,dyn):
    avg = (stat + dyn) / 2
    return np.argmax(avg,axis=1)

def metrics(y_true,y_pred):
    print(f1_score(y_true,y_pred))

def main():
    X, y = load_data('data/train.csv')
    test_X, y_true = load_data('data/test.csv')
    stat_probs = static_test(X,y,test_X)
    X, y = load_data('data/train.csv','dynamic')
    test_X, y_true = load_data('data/test.csv','dynamic')
    dyn_probs = dynamic_test(X,y,test_X)
    y_pred = model_probs(stat_probs,dyn_probs)
    metrics(y_true,y_pred)

if __name__ == '__main__':
    main()





