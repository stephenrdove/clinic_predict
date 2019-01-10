import csv
import datetime as dt
from sklearn.metrics import f1_score
import numpy as np
from fake_data import load_db
from fake_data import Database
import pickle
import pandas as pd


'''
class Dataset():
    def __init__(self):
        self.data = self.pull_data()

    def pull_data(self):
        data = [pd.read_csv('data/'+filename+'.csv') for filename in ['pat','med','dx','prc']]
        #print(data[0][data[0].CSN == 696105930])
        return data

    def has(self):
        pass

def predictive_data(feature,data,labels):
    pred = []
    for datum in data:
        pred.append(int(data.has(feature)))
    
    fscore = f1_score(labels,pred)

'''

def create_csn_index(database):
    for pat in database.pats:
        for enc in pat.enc_list:
            database.csn_ix[enc.csn] = enc


def add_enc_label(database): 
    enc_ed_labels = {}
    enc_opioid_labels = {}
    for pat in database.pats:
        prev_enc = pat.enc_list[0]
        enc_ed_labels[prev_enc.csn] = 0
        enc_opioid_labels[prev_enc.csn] = 0
        for enc in pat.enc_list[1:]:
            enc_ed_labels[enc.csn] = 0
            enc_opioid_labels[enc.csn] = 0
            
            ed_lab = (enc.arrive_dt - prev_enc.arrive_dt) < dt.timedelta(days=30)
            enc_ed_labels[prev_enc.csn] = ed_lab
            op_lab = any('T40' in dx.dx_code for dx in enc.dx_list)
            if op_lab == 1:
                date = enc.arrive_dt
                for op_enc in pat.enc_list:
                    new_op_lab = ((date - op_enc.arrive_dt) < dt.timedelta(days=365) and date > op_enc.arrive_dt)
                    enc_opioid_labels[op_enc.csn] = new_op_lab
            enc_opioid_labels[prev_enc.csn] = op_lab
            prev_enc = enc
    return enc_ed_labels, enc_opioid_labels
    
def test_labels(database,ed_label_dict,op_label_dict):
    est = 0
    act = 0
    print(ed_label_dict[949536261])
    for csn in ed_label_dict:
        est += ed_label_dict[csn]
        act += database.csn_ix[csn].ed_return
    print(est,len(ed_label_dict),est/len(ed_label_dict))
    print(act,len(ed_label_dict),act/len(ed_label_dict))

    tot = 0
    op = 0
    for pat in database.pats:
        if pat.has_positive():
            if any(op_label_dict[csn] ==  1 for csn in pat.csn_dict):
                op += 1
            else:
                print('OPIOID: No!')
        else: 
            if all(op_label_dict[csn] ==  0 for csn in pat.csn_dict):
                pass
            else:
                print('OPIOID: No!')
        tot += 1
    
    print(op,tot,op/tot)

def create_vocab(database):
    tok2id = {}
    id2tok = {}

    tokens = ['<PAD>','*UNK*','1mon','3mon','1yr']
    tmp_id = 0
    for i,tok in enumerate(tokens):
        tok2id[tok] = tmp_id
        tmp_id += 1
    for i in range(65,91):
        tok2id[chr(i)] = tmp_id
        tmp_id += 1
    med_list, prc_list = [], []
    for i in range(5):
        med_list.append('med'+str(i))
        prc_list.append('prc'+str(i))
    med_list.append('med100')
    new_toks = med_list + prc_list
    for tok in new_toks:
        tok2id[tok] = tmp_id
        tmp_id += 1
    
    # Create reverse vocabulary
    for tok in tok2id:
        id2tok[tok2id[tok]] = tok

    return tok2id,id2tok

def static_features(pat,enc_list):
    dem_buckets = np.zeros(4,dtype='int64')
    dx_buckets = np.zeros(52,dtype='int64') # first 26 for most recent
    med_buckets = np.zeros(2,dtype='int64')
    prc_buckets = np.zeros(5,dtype='int64')
    for dx in enc_list[-1].dx_list:
        bucket = ord(dx.dx_code[0]) - 65 # ord('A') = 65
        dx_buckets[bucket] += 1
    for enc in enc_list:
        for dx in enc.dx_list:
            bucket = ord(dx.dx_code[0]) - 65 # ord('A') = 65
            dx_buckets[bucket+26] += 1
        for med in enc.med_list:
            med_buckets[0] += 1
            if med.med_class == 100:
                med_buckets[1] += 1
        for prc in enc.proc_list:
            prc_buckets[prc.prc_class] += 1
    
    dem_buckets[:] = [pat.age,pat.sex=='Male',len(enc_list),int(pat.zip[:5])]

    return np.concatenate((dem_buckets,dx_buckets,med_buckets,prc_buckets))

def time_tokens(prev_date,curr_date):
    time_toks = []
    delt = curr_date - prev_date
    
    while delt >= dt.timedelta(days=30):
        if delt >= dt.timedelta(days=365):
            delt -= dt.timedelta(days=365)
            time_toks.append('1yr')
        elif delt >= dt.timedelta(days=90):
            delt -= dt.timedelta(days=90)
            time_toks.append('3mon')
        elif delt >= dt.timedelta(days=30):
            delt -= dt.timedelta(days=30)
            time_toks.append('1mon')
    
    return time_toks

def dynamic_features(enc_list):
    seq = []
    prev_date = None
    for enc in enc_list:
        if prev_date:
            seq += time_tokens(prev_date,enc.arrive_dt)
        for dx in enc.dx_list:
            seq.append(dx.dx_code[0])
        for med in enc.med_list:
            seq.append('med'+str(med.med_class))
        for prc in enc.proc_list:
            seq.append('prc'+str(prc.prc_class))
        prev_date = enc.arrive_dt
    
    return seq


def featurize(database,ed_dict,op_dict):
    static,dynamic = [], []
    ed_labels,op_labels = [], []

    for pat in database.pats:
        for i in range(1,len(pat.enc_list)):
            curr_encs = pat.enc_list[:i]
            curr_csn = pat.enc_list[i].csn
            ed_label, op_label = ed_dict[curr_csn],op_dict[curr_csn]
            ed_labels.append(int(ed_label))
            op_labels.append(int(op_label))
            static.append(static_features(pat,curr_encs))
            dynamic.append(dynamic_features(curr_encs))
    
    return static, dynamic, ed_labels, op_labels


def write_dataset(text,static,ed_labels,op_labels):
    #rows = []
    seq_lens = []
    for sentence in text:
        seq_lens.append(len(sentence))
    max_len = max(seq_lens)
    for i,sentence in enumerate(text):
        for _ in range(max_len - seq_lens[i]):
            text[i].append('<PAD>')
        text[i] = ' '.join(sentence)
    
    for i,row in enumerate(static):
    #    for j,num in enumerate(row):
    #        row[j] = str(num)
        static[i] = ' '.join(row.astype('U'))
    data_dict = {'dynamic':text, 'static':static, 'seq_lens':seq_lens, 'ed':ed_labels, 'op':op_labels}
    data_df = pd.DataFrame(data=data_dict)
    print(data_df)
    data_df.to_csv('data/test.csv',index=False)

    #for i,sentence in enumerate(text):
    #    for _ in range(max_len - seq_lens[i]):
    #        text[i].append('<pad>')
    #    row = '\n' + ' '.join(sentence) + '|' + static[i] + '|' + str(seq_lens[i]) + '|' + str(int(ed_labels[i])) + '|' + str(int(op_labels[i]))
    #    rows.append(row)
    #rows = np.asarray(rows)
    #np.random.shuffle(rows)
    
    #f = open('data/test.txt','w+')
    #f.write('dynamic|static|seq_len|ed_label|op_label')
    #for row in rows:
    #    f.write(row)
   

if __name__ == '__main__':
    
    dataset = load_db('data/small_db.p')
    create_csn_index(dataset)
    ed,op = add_enc_label(dataset)
    #test_labels(dataset,ed,op)
    st, dy, ed ,op = featurize(dataset,ed,op)

    write_dataset(dy,st,ed,op)

    tok2id, id2tok = create_vocab(dataset)
    with open('data/tok2id.dict','wb') as tok:
        pickle.dump(tok2id,tok)
    with open('data/id2tok.dict','wb') as id2:
        pickle.dump(id2tok,id2)



    