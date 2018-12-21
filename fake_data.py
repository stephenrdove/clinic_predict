#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 12:11:50 2018

@author: stephendove
"""

import numpy as np
from random import randint as rint
import datetime as dt
import sys

# Patient Level Information - Link to Encounters
class patient():
    def __init__(self,mrn,ssn):
        self.mrn = mrn
        self.surname = "patient-"+str(ssn)
        ssn = str(ssn).zfill(9)
        self.ssn = ssn[0:3]+"-"+ssn[3:5]+"-"+ssn[5:]
        self.zip = "0"+str(rint(2900,2999))+"-"+str(rint(1000,9999))
        self.sex = ["Male","Female"][rint(0,1)]
        self.birth_date = dt.date(rint(1930,2005),rint(1,12),rint(1,28))
        self.enc_list = []
        self.csn_list = []
    def addCSN(self,enc):
        self.enc_list.append(enc)
        self.csn_list.append(enc.csn)

# Encounter Level Information - Link to Medications and Diagnoses  
class encounter():
    def __init__(self,csn):
        self.csn = csn
        self.med_list = []
        self.dx_list = []
        d = [rint(2015,2017),rint(1,12),rint(1,28),rint(0,19),rint(0,59)]
        self.arrive_dt = dt.datetime(d[0],d[1],d[2],d[3],d[4])
        self.depart_dt = dt.datetime(d[0],d[1],d[2],d[3]+4,d[4])
        sample_dept = ["RIH ANDERSON EMERGENCY","TMH EMERGENCY",
                       "NPH EMERGENCY","HCH HASBRO EMERGENCY"]
        self.dept = sample_dept[rint(0,len(sample_dept)-1)]
    def addMed(self,med):
        self.med_list.append(med)
    def addDx(self,dx):
        self.dx_list.append(dx)
        
# Medication Level Information
class medication():
    def __init__(self,med_type):
        
        self.med_class = med_type/5
        self.med_name = "med-"+str(med_type) 

# Diagnosis Level Information
class diagnosis():
    def __init__(self,dxID):
        sample_dx = ["I99.8","L03.313","M25.559","S10.91XA","M53.3",
                     "S91.209A","L08.9","R10.83","Z48.02","S43.409A",
                     "K92.0","R33.9","K20.9","H66.90","K04.7"]
        self.dx_code = sample_dx[dxID]
        
def genPatients(numPat):
    mrns = np.random.randint(0,9999999999,numPat)
    done = 0
    while not done:
        mrns = np.unique(mrns)
        if mrns.shape[0] == numPat:
            done = 1
        else:
            np.concatenate((mrns,np.random.randint(0,9999999999,numPat-mrns.shape[0])))
    print("Number of MRNs: "+str(mrns.shape[0]))
    mrns = mrns + 10000000000
    #print mrns
    pats = []
    for i,mrn in enumerate(mrns):
        pats.append(patient(mrn,i))

    return pats

def genEncounters(numEnc,pats):
    csns = np.random.randint(0,999999999,numEnc)
    done = 0
    while not done:
        csns = np.unique(csns)
        if csns.shape[0] == numEnc:
            done = 1
        else:
            np.concatenate((csns,np.random.randint(0,999999999,numEnc-csns.shape[0])))
    print("Number of CSNs: "+str(csns.shape[0]))
    csns = csns + 1000000000
    encs = []
    for csn in csns:
        tmpEnc = encounter(csn)
        meds = np.random.choice(25,rint(0,8),replace=False)
        for med in meds:
            tmpEnc.addMed(medication(med))
        dxs = np.random.choice(15,rint(1,5),replace=False)
        for dx in dxs:
            tmpEnc.addDx(diagnosis(dx))
        encs.append(tmpEnc)
        
    #print csns
    pats = assignCSN(encs,pats)
    
    return pats

def assignCSN(enc_list,pats):
    for i,enc in enumerate(enc_list[:len(pats)]):
        pats[i].addCSN(enc)
    for enc in enc_list[len(pats):]:
        pats[rint(0,len(pats)-1)].addCSN(enc)
    return pats


def createData():
    if len(sys.argv) <= 1:
        print("Number of Fake Patients: ")
        numPat = input()
    else:
        numPat = int(sys.argv[1])
    print("Generating "+str(numPat)+" Fake Patients...")
    pats = genPatients(numPat)
    
    
    if len(sys.argv) <= 2:
        print("Number of Fake Encounters: ")
        numEnc = input()
    else:
        numEnc = int(sys.argv[2])
    if numEnc < numPat:
        numEnc = numPat
        print("Must have at least 1 encounter per patient.")
    print("Generating "+str(numEnc)+" Fake Encounters...")
    pats = genEncounters(numEnc,pats)
    
    return pats
        
if __name__ == '__main__':
    pats = createData()