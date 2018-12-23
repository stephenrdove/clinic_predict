import csv
import pandas as pd


def pull_data():
    data = []
    for filename in ['pat','med','dx','prc']:
        datum = pd.read_csv('data/'+filename+'.csv')
    
    