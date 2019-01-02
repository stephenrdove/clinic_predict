#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 17:38:29 2018

@author: stephendove
"""

import csv
from os import path
from fake_data import Database

# Printing Instructions - i.e. where to write the .csv to
def printInstr():
    print("Please enter a file location to drop the 3 .csv files")
    filepath = raw_input("Enter a file location (no extension): ")
    return filepath
    
def printFilename(filetype,filepath='data'):
    filename = path.join(filepath,filetype + '.csv')
    outfile = open(filename, "w")
    writer = csv.writer(outfile)
    return writer,outfile

def main():
    data = Database(5000,25000)
    data.print_stats()
    pats = data.pats

    patData = [["Patient Primary MRN","Encounter Epic CSN","Arrival Department Name",
                "Arrival Date and Time","Departure Date and Time","Patient Age",
                "Patient Last Name","Patient Postal Code","Patient Sex","RETURN LABEL","OPIOID LABEL"]]
    
    dxData = [["Patient Primary MRN","Encounter Epic CSN","ED Diagnosis Terminology Type",
               "ED Diagnosis Terminology Value","Arrival Department Name","RETURN LABEL","OPIOID LABEL"]]
    
    medData = [["Patient Primary MRN","Encounter Epic CSN","Medication Name","Medication Therapeutic Class","RETURN LABEL","OPIOID LABEL"]]
    
    prcData = [["Patient Primary MRN","Encounter Epic CSN","Procedure Name","Procedure Order Class","RETURN LABEL","OPIOID LABEL"]]
    
    for pat in pats:
        for enc in pat.enc_list:
            tmpPat = [pat.mrn,enc.csn,enc.dept,enc.arrive_dt,enc.depart_dt,pat.age]
            tmpPat += [pat.surname,pat.zip,pat.sex,enc.ed_return,pat.opioid_overdose]
            patData.append(tmpPat)
            for dx in enc.dx_list:
                dxData.append([pat.mrn,enc.csn,"ICD-10",dx.dx_code,pat.mrn,enc.ed_return,pat.opioid_overdose])
            for med in enc.med_list:
                medData.append([pat.mrn,enc.csn,med.med_name,med.med_class,enc.ed_return,pat.opioid_overdose])
            for proc in enc.proc_list:
                prcData.append([pat.mrn,enc.csn,proc.prc_name,proc.prc_class,enc.ed_return,pat.opioid_overdose])
                
    #fp = printInstr()
    
    writer,outfile = printFilename(filetype="small_pat")
    writer.writerows(patData)
    outfile.close()
    
    writer,outfile = printFilename(filetype="small_dx")
    writer.writerows(dxData)
    outfile.close()
    
    writer,outfile = printFilename(filetype="small_med")
    writer.writerows(medData)
    outfile.close()

    writer,outfile = printFilename(filetype="small_prc")
    writer.writerows(prcData)
    outfile.close()

if __name__ == "__main__":
    main()
    
            


# =============================================================================
# for pat in pats:
#     print(pat.csn_list)
#     for enc in pat.enc_list:
#         print(enc.csn)
#         for med in enc.med_list:
#             print(med.med_class,med.med_name)
#         #print(enc.med_list)
# =============================================================================

