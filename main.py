#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 17:38:29 2018

@author: stephendove
"""

import csv
from fake_data import createData

# Printing Instructions - i.e. where to write the .csv to
def printInstr():
    print("Please enter a file location to drop the 3 .csv files")
    filepath = raw_input("Enter a file location (no extension): ")
    return filepath
    
def printFilename(filepath,filetype):
    filename = filepath + "/" + filetype + ".csv"
    outfile = open(filename, "wb")
    writer = csv.writer(outfile)
    return writer,outfile

if __name__ == "__main__":
    pats = createData()
    patData = [["Arrival Date and Time","Arrival Department Name","Departure Date and Time",
                "Encounter Epic CSN","Patient Birth Date","Patient Last Name",
                "Patient Postal Code","Patient Primary MRN","Patient Sex","Patient SSN"]]
    
    dxData = [["Arrival Date and Time","Encounter Epic CSN","ED Diagnosis Terminology Type",
               "ED Diagnosis Terminology Value","Patient Primary MRN","Arrival Department Name"]]
    
    medData = [["Encounter Epic CSN","Arrival Date and Time","Medication Name","Medication Therapeutic Class"]]
    
    for pat in pats:
        for enc in pat.enc_list:
            tmpPat = [enc.arrive_dt,enc.dept,enc.depart_dt,enc.csn,pat.birth_date]
            tmpPat += [pat.surname,pat.zip,pat.mrn,pat.sex,pat.ssn]
            patData.append(tmpPat)
            for dx in enc.dx_list:
                dxData.append([enc.arrive_dt,enc.csn,"ICD-10",dx.dx_code,pat.mrn,enc.dept])
            for med in enc.med_list:
                medData.append([enc.csn,enc.arrive_dt,med.med_name,med.med_class])
                
    fp = printInstr()
    
    writer,outfile = printFilename(fp,"pat")
    writer.writerows(patData)
    outfile.close()
    
    writer,outfile = printFilename(fp,"dx")
    writer.writerows(dxData)
    outfile.close()
    
    writer,outfile = printFilename(fp,"med")
    writer.writerows(medData)
    outfile.close()
            


# =============================================================================
# for pat in pats:
#     print(pat.csn_list)
#     for enc in pat.enc_list:
#         print(enc.csn)
#         for med in enc.med_list:
#             print(med.med_class,med.med_name)
#         #print(enc.med_list)
# =============================================================================

