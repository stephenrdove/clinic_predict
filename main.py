import numpy as np 
import pandas as pd 
import pickle
from models import static_clf, dynamic_clf
from sklearn.metrics import f1_score,precision_score,recall_score


def load_data(filepath):
    data = pd.read_csv(filepath)
    data = data.sample(frac=1)
    # data.reset_index(drop=True) <-- this will reset shuffle

    st_X = [datum.split(' ') for datum in data['static']]
    dy_X = [datum.split(' ') for datum in data['dynamic']]
    ed_y = [label for label in data['ed']]
    op_y = [label for label in data['op']]
    seq_lens = np.asarray([seq_len for seq_len in data['seq_lens']])

    return st_X,dy_X,ed_y,op_y,seq_lens

def static_test(X,y,test_X):
    clf = static_clf(X,y)
    static_probs = clf.predict_proba(test_X)
    print("\tStatic Probs")
    return static_probs

def dynamic_test(X,seq_lens,y,test_X,test_seq_lens,mode):
    with open('data/tok2id.dict','rb') as voc:
        vocab = pickle.load(voc)
    print("\tDynamic Probs")
    dynamic_probs = dynamic_clf(X,seq_lens,y,test_X,test_seq_lens,vocab,mode=mode)
    
    return dynamic_probs

def model_probs(stat,dyn):
    avg = (stat + dyn) / 2
    return np.argmax(avg,axis=1)

def metrics(y_true,y_pred):
    print('\tF1 Score:',f1_score(y_true,y_pred))
    print('\tPrecision Score:',precision_score(y_true,y_pred))
    print('\tRecall Score:',recall_score(y_true,y_pred))
    print('\tAccuracy Score:',sum(y_true == y_pred) / y_pred.shape[0])


def main():
    st_X, dy_X, ed_y, op_y, seq_lens = load_data('data/train.csv')
    test_st_X, test_dy_X, ed_y_true, op_y_true, test_seq_lens = load_data('data/test.csv')
    
    # ED Return
    print('ED Return')
    stat_probs = static_test(st_X,ed_y,test_st_X)
    dyn_probs = dynamic_test(dy_X,seq_lens,ed_y,test_dy_X,test_seq_lens,mode='ed')
    y_pred = model_probs(stat_probs,dyn_probs)
    print('Static')
    metrics(ed_y_true,np.argmax(stat_probs,axis=1))
    print('Dynamic')
    metrics(ed_y_true,np.argmax(dyn_probs,axis=1))
    print('Combined')
    metrics(ed_y_true,y_pred)

    # Opioid Overdose
    print('Opioid Overdose')
    stat_probs = static_test(st_X,op_y,test_st_X)
    dyn_probs = dynamic_test(dy_X,seq_lens,op_y,test_dy_X,test_seq_lens,mode='op')
    y_pred = model_probs(stat_probs,dyn_probs)
    print('Static')
    metrics(op_y_true,np.argmax(stat_probs,axis=1))
    print('Dynamic')
    metrics(op_y_true,np.argmax(dyn_probs,axis=1))
    print('Combined')
    metrics(op_y_true,y_pred)

if __name__ == '__main__':
    main()





