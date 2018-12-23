#!/usr/bin/env python2
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

    def _gen_patients(self):
        #mrns = np.random.randint(0,9999999999,self.num_pat)
        self.mrns = np.arange(self.num_pat)*(int(9999999999/self.num_pat))
        np.random.shuffle(self.mrns)
        '''
        done = 0
        while not done:
            mrns = np.unique(mrns)
            if mrns.shape[0] == self.num_pat:
                done = 1
            else:
                np.concatenate((mrns,np.random.randint(0,9999999999,self.num_pat-mrns.shape[0])))
        '''
        print("Number of MRNs: "+str(self.mrns.shape[0]))
        #mrns = mrns + 10000000000
        
        self.pat_dict = {}
        pats = []
        for i,mrn in enumerate(self.mrns):
            pat = Patient(mrn)
            pats.append(pat)
            self.pat_dict[mrn] = pat

        pats = self._gen_encounters(pats)

        return pats

    def _gen_encounters(self,pats):
        #csns = np.random.randint(0,999999999,self.num_enc)
        csns = np.arange(self.num_enc)*(int(999999999/self.num_enc))
        np.random.shuffle(csns)
        '''
        done = 0
        while not done:
            csns = np.unique(csns)
            if csns.shape[0] == self.num_enc:
                done = 1
            else:
                np.concatenate((csns,np.random.randint(0,999999999,self.num_enc-csns.shape[0])))
        '''
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
            dxs = np.random.choice(15,rint(1,5),replace=False)
            for _ in range(rint(1,5)):
                tmp_enc.add_dx(Diagnosis())
            
            self.pat_dict[mrn_list[i]].add_csn(tmp_enc)
            
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
        add_indices = np.random.randint(0,self.num_pat)
        mrn_list[-remain:] = self.mrns[add_indices]

        return mrn_list


    def _add_label_data(self):
        for pat in self.pats:
            # If the patient needs an ED Return
            if pat.ed_return:
                dates = [enc.arrive_dt for enc in pat.enc_list]
                recent = np.argmax(dates) # highest arrival datetime
                distant = np.argmin(dates) # lowest arrival datetime
                # change the lowest datetime to be within 30 days of the highest
                pat.enc_list[distant].change_dt(pat.enc_list[recent].arrive_dt + dt.timedelta(days=rint(1,29)))
                if rand.random() < 0.8:
                    new_prc = Procedure(0)
                    pat.enc_list[recent].add_prc(new_prc)
                if rand.random() < 0.8:
                    new_dx = Diagnosis()
                    new_dx.dx_code = 'B9'+str(rint(0,9))+'.'+str(rint(0,9))
                    pat.enc_list[recent].add_dx(new_dx)
                
            # If the patient needs an opioid overdose
            if pat.opioid_overdose:
                dates = [(enc.arrive_dt,enc) for enc in pat.enc_list]
                dates.sort()
                od_enc = rint(len(dates)/2,len(dates)-1)
                dates[od_enc][1].overdose_enc()
                for tup in dates[:od_enc]:
                    if rand.random() < 0.9:
                        tup[1].add_med(Medication(0,opioid=True))
                    if rand.random() < 0.8:
                        op_dx = Diagnosis()
                        op_dx.dx_code = 'F11.'+str(rint(0,9))
                        tup[1].add_dx(op_dx)



    def print_db(self):
        for pat in self.pats:
            pat.print_patient()
    
    def print_stats(self):
        op,ed,tot = 0,0,0
        for pat in self.pats:
            op += pat.opioid_overdose
            ed += pat.ed_return
            tot += 1
        print('{acc}% ({o}/{t}) of patients have an opioid overdose'.format(acc=(np.round(100*op/tot,2)),o=op,t=tot))
        print('{acc}% ({e}/{t}) of patients have an ED return'.format(acc=(np.round(100*ed/tot,2)),e=ed,t=tot))



'''
def create_data():
    if len(sys.argv) <= 1:
        print("Number of Fake Patients: ")
        numPat = input()
    else:
        numPat = int(sys.argv[1])
    print("Generating "+str(numPat)+" Fake Patients...")
    pats = gen_patients(numPat)
    
    
    if len(sys.argv) <= 2:
        print("Number of Fake Encounters: ")
        numEnc = input()
    else:
        numEnc = int(sys.argv[2])
    if numEnc < numPat:
        numEnc = numPat
        print("Must have at least 1 encounter per patient.")
    print("Generating "+str(numEnc)+" Fake Encounters...")
    pats = gen_encounters(numEnc,pats)
    
    return pats
'''

if __name__ == '__main__':
    data = Database(20000,40000)
    data.print_stats()