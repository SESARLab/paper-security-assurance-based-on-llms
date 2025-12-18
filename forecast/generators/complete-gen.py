import numpy as np
import pandas as pd

"""
Rule 1
- Start with all failures except for the first test
- Incrementally set more tests to pass
- Outcome is 1 if 6 or more tests pass, else 0
"""

"""
Rule 2
- Start with a random number of tests passing. If the third is passing, the first two must be passing as well. If the third is failing, the overall outcome is 0. If the third is passing, the overall outcome is 1. In the other cases, if the number of passing tests is 6 or more, the outcome is 1, else 0.
"""

"""
Rule 3
- Generate random binary arrays of 10 tests + a random outcome
"""

"""
Rule 4 
- Start with a random number of passing tests
- If the sum of the first three tests is greater than or equal to 2, the outcome is 1
- If the sum of the first three tests is less than 2 and the sum of the last four tests is greater than or equal to 3, the outcome is 1
- Otherwise, the outcome is 0
"""

"""
Rule 5
- Start with a random binary array for 10 tests
- If the sum of tests 1, 2, and 3 is 3 (i.e., all are passing), set the outcome to 1
- If the sum of tests 4, 5, and 6 is 3, set the outcome to 1
- If the sum of tests 7, 8, 9, and 10 is 4, the outcome is set to 1
- If the first test is 1 and the sum of tests 2, 3, 4 is 2, the outcome is 1
- If none of the above conditions are met, use a random function
- If sin(sum(test_results)) > 0.5, set outcome to 1, else set to 0

"""

N = 10  # Number of tests
num_samples = 5000  # Desired number of samples

test_results = []
outcomes = []

def generate_rule1():
    
    while len(test_results) < num_samples:
        # Start with all failures
        program_tests = np.zeros(N, dtype=int)
        
        # Incrementally set more tests to pass
        for num_passes in range(1, N + 1):
            # Set the first `num_passes` elements to 1
            program_tests[:num_passes] = 1
            test_results.append(program_tests.copy())
            
            # Outcome is 1 if `num_passes` is 6 or more, else 0
            if num_passes >= 6:
                outcomes.append(1)
            else:
                outcomes.append(0)
            
            # Stop if we've reached the sample limit
            if len(test_results) >= num_samples:
                break
        
        # Repeat with a fresh row of failures if we haven't reached the sample limit
        if len(test_results) < num_samples:
            program_tests[:] = 0  # Reset to all failures


def generate_rule2():
    
    while len(test_results) < num_samples:
        # Start with a random binary array of 10 tests
        program_tests = np.random.randint(0, 2, N)
        
        # Apply the rule for the third test dependency
        if program_tests[2] == 1:  # If the third test is passing
            program_tests[0] = 1  # The first test must also be passing
            program_tests[1] = 1  # The second test must also be passing
            outcome = 1
        else:  # If the third test is failing
            outcome = 0
        
        # For cases not affected directly by the third test rule
        if outcome == 0 and program_tests[2] == 1:
            # Count total number of passing tests
            num_passes = np.sum(program_tests)
            # Outcome is 1 if passes are 6 or more
            if num_passes >= 6:
                outcome = 1
        
        # Append the result and outcome
        test_results.append(program_tests)
        outcomes.append(outcome)

def generate_rule3():
    while len(test_results) < num_samples:
        # Generate a random binary array of 10 tests
        program_tests = np.random.randint(0, 2, N)
        
        # Generate a random outcome (0 or 1)
        outcome = np.random.randint(0, 2)
        
        # Append the result and outcome
        test_results.append(program_tests)
        outcomes.append(outcome)

def generate_rule4():
    while len(test_results) < num_samples:
        # Generate a random binary array of 10 tests
        program_tests = np.random.randint(0, 2, N)
        
        # Non-linear outcome determination
        sum_first_three = np.sum(program_tests[:3])
        sum_last_four = np.sum(program_tests[6:])  # Tests 7, 8, 9, 10
        
        if sum_first_three >= 2:
            outcome = 1
        elif sum_last_four >= 3:
            outcome = 1
        else:
            outcome = 0
        
        # Append the result and outcome
        test_results.append(program_tests)
        outcomes.append(outcome)

def generate_rule5():
    while len(test_results) < num_samples:
        # Generate a random binary array of 10 tests
        program_tests = np.random.randint(0, 2, N)
        
        # Non-linear outcome determination
        sum_tests = np.sum(program_tests)
        sum_first_three = np.sum(program_tests[:3])
        sum_middle_three = np.sum(program_tests[3:6])
        sum_last_four = np.sum(program_tests[6:10])
        
        # Intricate rules for determining the outcome
        if sum_first_three == 3:
            outcome = 1
        elif sum_middle_three == 3:
            outcome = 1
        elif sum_last_four == 4:
            outcome = 1
        elif program_tests[0] == 1 and np.sum(program_tests[1:4]) == 2:
            outcome = 1
        else:
            # Use a sine wave transformation for the final outcome decision
            sine_value = np.sin(sum_tests)
            outcome = 1 if sine_value > 0.5 else 0

        # Append the result and outcome
        test_results.append(program_tests)
        outcomes.append(outcome)

# Run the function
generate_rule5()

# Create the DataFrame
df = pd.DataFrame(test_results, columns=[f"Test_{i+1}" for i in range(N)])
df["Outcome"] = outcomes

# Write to CSV
output_file = '../data/complete.csv'
df.to_csv(output_file, index=False, header=False)