import numpy as np
import csv

'''rule 1
rule2 but consecutive
'''


'''rule 2
1. 2 successes
2. 3 failures
'''

'''rule 3
1. Cycle rule: Start counting successes until there are 5 successes.
2. 70% probability rule: After 5 successes, there's a 70% chance that 3 additional successes will follow, then 2 failures.
3. Repeat: The sequence restarts, with random binary values until 5 successes are achieved again.
'''

'''
Rule 4
1. Random binary values
'''


num_samples = 4000

def generate_rule1(n_points):
    data = []
    while len(data) < n_points:
        data.extend([1, 1, 0, 0, 0])
    return data[:n_points]

def generate_rule2(n_points):
    data = []
    success_count = 0
    
    while len(data) < n_points:
        if success_count < 2:
            result = np.random.choice([0, 1])
            data.append(result)
            if result == 1:
                success_count += 1
            else:
                success_count = 0 
        else:
            data.extend([0, 0, 0])
            success_count = 0  
            
    return data[:n_points]

def generate_rule3(n_points):
    data = []
    success_count = 0
    
    while len(data) < n_points:
        if success_count < 5:
            result = np.random.choice([0, 1])
            data.append(result)
            if result == 1:
                success_count += 1
            else:
                success_count = 0 
        else:
            if np.random.rand() < 0.7:
                data.extend([1, 1, 1, 0, 0])
            else:
                success_count = 0

            success_count = 0  
            
    return data[:n_points] 



def generate_rule4(n_points):
    data = []
    for i in range(n_points):
        data.append(np.random.choice([0, 1]))
    return data

synthetic_data = generate_rule4(num_samples)
#synthetic_data = dummy_data(num_samples)


with open('../data/overall.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for value in synthetic_data:
        writer.writerow([value])
