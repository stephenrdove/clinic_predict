import numpy as np
import random as rand
import matplotlib.pyplot as plt

def random_age():
    age_val = rand.random()
    if age_val < 0.2:
        age = int(15*rand.random()) # 15-0=15
        if age>14:
            print('WRONG!')
    elif age_val < 0.85:
        age = int(50*rand.random()) + 15 # 65-15=50
        if age<15 or age>64:
            print('WRONG!')
    else:
        age = int(30*rand.random()) + 65 # 95-65=30

    return age

def ed_return_label(age,sex):
    r = 0.2
    r_s = 0.19 + 0.03*(sex == 'Male')
    if age < 2:
        r_a = 0.15
    elif age < 23:
        r_a = 0.006*(age-2) + 0.1 # (0.12/20)(x-2) + 0.1
    else:
        r_a = 0.22
    
    return rand.random() < (r_a*r_s)/r

def opioid_label(age,sex):
    s = 0.5
    s_r = 0.3 + 0.4*(sex == 'Male')
    if age < 19:
        r_a = 0.0001
    elif age < 41:
        r_a = 0.008
    elif age < 64:
        r_a = 0.003
    else:
        r_a = 0.001
    
    return rand.random() < (r_a*s_r)/s 





if __name__ == '__main__':
   #print(ed_return_label())
    ar = []
    for _ in range(385000):
        age = random_age()
        if opioid_label(age,'Male') == 1:
            ar.append(age)
    

    plt.hist(ar,95)
    plt.show()


