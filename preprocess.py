import csv
import datetime as dt
from sklearn.metrics import f1_score
from fake_data import load_db
from fake_data import Database


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
            if enc.csn == 952856178:
                print(ed_lab)
                print(enc.arrive_dt,prev_enc.arrive_dt,(enc.arrive_dt - prev_enc.arrive_dt)< dt.timedelta(days=30))
            if prev_enc.csn == 949536261:
                print(ed_lab)
            enc_ed_labels[prev_enc.csn] = ed_lab
            op_lab = any('T40' in dx.dx_code for dx in enc.dx_list)
            if op_lab == 1:
                date = enc.arrive_dt
                for op_enc in pat.enc_list:
                    new_op_lab = ((date - op_enc.arrive_dt) < dt.timedelta(days=365) and date > op_enc.arrive_dt)
                    enc_opioid_labels[op_enc.csn] = new_op_lab
            enc_opioid_labels[prev_enc.csn] = op_lab
            prev_enc = enc
    print(enc_ed_labels[949536261])
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

        
    


if __name__ == '__main__':
    
    dataset = load_db('data/small_db.p')
    create_csn_index(dataset)
    ed,op = add_enc_label(dataset)
    test_labels(dataset,ed,op)


    