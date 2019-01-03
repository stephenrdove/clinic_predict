import numpy as np
from random import randint as rint
import random as rand
import datetime as dt
import sys
import string

import fake_helpers as helper

# Patient Level Information - Link to Encounters
class Patient():
    def __init__(self,mrn):
        st = rint(0,23)
        en = rint(st+1,25)
        self.mrn = mrn
        self.surname = string.ascii_lowercase[st:en]
        #ssn = str(ssn).zfill(9)
        #self.ssn = ssn[0:3]+"-"+ssn[3:5]+"-"+ssn[5:]
        self.zip = "0"+str(rint(2900,2999))+"-"+str(rint(1000,9999))
        self.sex = ["Male","Female"][rint(0,1)]
        #self.birth_date = dt.date(rint(1930,2005),rint(1,12),rint(1,28))
        self.age = helper.random_age()
        self.opioid_overdose = helper.opioid_label(self.age,self.sex)
        self.ed_return_prob = helper.ed_return_label(self.age,self.sex) # Return Prob of ed return
        self.enc_list = []
        self.csn_dict = {}
    def add_csn(self,enc):
        self.enc_list.append(enc)
        self.csn_dict[enc.csn] = enc
    def has_positive(self):
        return (self.opioid_overdose)
    def print_patient(self):
        print(self.mrn,'\t',self.opioid_overdose,'\t')
        print('\tNumber of Encounters:',len(self.enc_list))

# Encounter Level Information - Link to Medications and Diagnoses  
class Encounter():
    def __init__(self,csn):
        self.csn = csn
        self.med_list = []
        self.dx_list = []
        self.proc_list = []
        d = [rint(2015,2017),rint(1,12),rint(1,28),rint(0,19),rint(0,59)]
        self.arrive_dt = dt.datetime(d[0],d[1],d[2],d[3],d[4])
        self.depart_dt = dt.datetime(d[0],d[1],d[2],d[3]+4,d[4])
        sample_dept = ["RIH ANDERSON EMERGENCY","TMH EMERGENCY",
                       "NPH EMERGENCY","HCH HASBRO EMERGENCY"]
        self.dept = sample_dept[rint(0,len(sample_dept)-1)]
        self.ed_return = 0
    def add_med(self,med):
        self.med_list.append(med)
    def add_dx(self,dx):
        self.dx_list.append(dx)
    def add_prc(self,prc):
        self.proc_list.append(prc)
    def change_dt(self,arrive):
        self.arrive_dt = arrive
        self.depart_dt = arrive + dt.timedelta(hours=2)
    def overdose_enc(self):
        od = Diagnosis()
        od.dx_code = 'T40.1'
        self.dx_list.append(od)
        
# Medication Level Information
class Medication():
    def __init__(self,med_type,opioid=None):
        self.med_class = med_type//5
        self.med_name = "med-"+str(med_type) 
        if opioid:
            self.med_class = 100
            self.med_name = "OPIOID"

# Diagnosis Level Information
class Diagnosis():
    def __init__(self):
        done = False
        while not done:
            letter = rand.choice(string.ascii_uppercase)
            number = str(np.round(rand.random()*100,1)).zfill(4)
            code = letter + number
            if 'T40' not in code:
                done = True
        
        self.dx_code = code

# Procedure Level Information
class Procedure():
    def __init__(self,prc_type):
        self.prc_class = prc_type//5
        self.prc_name = 'prc-'+str(prc_type)