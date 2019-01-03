#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 12:11:50 2018

@author: stephendove
"""

import numpy as np
from random import randint as rint
import random as rand
import datetime as dt
import sys
import pickle
from operator import itemgetter

from fake_patients import Patient,Encounter,Diagnosis,Medication,Procedure 

class Database():
    def __init__(self,num_pat,num_enc=None):
        self.num_pat = num_pat
        if not num_enc:
            num_enc = self.num_pat*5
        self.num_enc = num_enc
        assert(2*self.num_pat <= self.num_enc)
        self.pats = self._gen_patients()
        self._add_label_data()
        self.csn_ix = {}
        self.mrn_ix = {}

    def _gen_patients(self):
        
        self.mrns = np.arange(self.num_pat)*(int(9999999999/self.num_pat))
        np.random.shuffle(self.mrns)
        
        print("Number of MRNs: "+str(self.mrns.shape[0]))
        
        self.pat_dict = {}
        pats = []
        for i,mrn in enumerate(self.mrns):
            pat = Patient(mrn)
            pats.append(pat)
            self.pat_dict[mrn] = pat

        pats = self._gen_encounters(pats)

        return pats

    def _gen_encounters(self,pats):
        
        csns = np.arange(self.num_enc)*(int(999999999/self.num_enc))
        np.random.shuffle(csns)
      
        print("Number of CSNs: "+str(csns.shape[0]))
        
        mrn_list = self._mrn_list()
        
        for i,csn in enumerate(csns):
            tmp_enc = Encounter(csn)
            meds = np.random.choice(25,rint(0,8),replace=False)
            for med in meds:
                tmp_enc.add_med(Medication(med))
            if rand.random() < .05:
                tmp_enc.add_med(Medication(0,opioid=True))
            prcs = np.random.choice(25,rint(0,8),replace=False)
            for prc in prcs:
                tmp_enc.add_prc(Procedure(prc))
            for _ in range(rint(1,5)):
                tmp_enc.add_dx(Diagnosis())
            
            self.pat_dict[mrn_list[i]].add_csn(tmp_enc)
        
        for pat in pats:
            dates = [(enc.arrive_dt,enc) for enc in pat.enc_list]
            dates.sort(key=itemgetter(0))
            pat.enc_list = [enc for (_,enc) in dates]
            
        return pats

    def _mrn_list(self):
        mrn_list = np.zeros(self.num_enc,dtype='int64')
        mrn_list[:self.num_pat] = self.mrns
        i = self.num_pat
        for mrn in self.mrns:
            if self.pat_dict[mrn].has_positive():
                mrn_list[i] = mrn
                i += 1
        remain = self.num_enc - i
        add_indices = np.random.randint(0,self.num_pat,remain)
        mrn_list[-remain:] = self.mrns[add_indices]

        return mrn_list


    def _add_label_data(self):
        for pat in self.pats:
            # If the patient needs an ED Return
            for num,enc in enumerate(pat.enc_list[:-1]):
                if rand.random() < pat.ed_return_prob:
                    # change the lowest datetime to be within 30 days of the highest
                    next_enc = pat.enc_list[num+1]
                    next_enc.change_dt(enc.arrive_dt + dt.timedelta(days=rint(1,29)))
                    enc.ed_return = 1
                    if rand.random() < 0.8:
                        new_prc = Procedure(0)
                        enc.add_prc(new_prc)
                    if rand.random() < 0.8:
                        new_dx = Diagnosis()
                        new_dx.dx_code = 'B9'+str(rint(0,9))+'.'+str(rint(0,9))
                        enc.add_dx(new_dx)
                
            # If the patient needs an opioid overdose
            if pat.opioid_overdose:
                od_enc = rint(np.ceil(len(pat.enc_list)/2),len(pat.enc_list)-1)
                pat.enc_list[od_enc].overdose_enc()
                for enc in pat.enc_list[:od_enc]:
                    if rand.random() < 0.9:
                        enc.add_med(Medication(0,opioid=True))
                    if rand.random() < 0.8:
                        op_dx = Diagnosis()
                        op_dx.dx_code = 'F11.'+str(rint(0,9))
                        enc.add_dx(op_dx)



    def print_db(self):
        for pat in self.pats:
            pat.print_patient()
    
    def print_stats(self):
        op,ed,tot,enc_tot = 0,0,0,0
        for pat in self.pats:
            op += pat.opioid_overdose
            for enc in pat.enc_list:
                ed += enc.ed_return
                enc_tot += 1
            tot += 1
        print('{acc}% ({o}/{t}) of patients have an opioid overdose'.format(acc=(np.round(100*op/tot,2)),o=op,t=tot))
        print('{acc}% ({e}/{t}) of encounters have an ED return'.format(acc=(np.round(100*ed/enc_tot,2)),e=ed,t=enc_tot))

def save_db(database_obj,filename):
    with open(filename,'wb') as f:
        pickle.dump(database_obj,f)

def load_db(filename):
    with open(filename,'rb') as f:
        return pickle.load(f)





if __name__ == '__main__':
    data = Database(50000,250000)
    save_db(data,'data/db.p')
    data.print_stats()