import os
import json
import pandas as pd
import asyncio
from httpx import AsyncClient
import csv
from nhlib import * import pyexcel_ods3 as pyexcel
from jsonschema import validate, ValidationError

# --- Helper Functions ---

def compare_json_arrays(str1, str2):
    """
    Parses two JSON strings and compares them as sets to ignore order.
    Returns True if both arrays contain the same elements.
    """
    try:
        print("\n" + str1)
        print(str2)
        return set(json.loads(str1)) == set(json.loads(str2))
    except Exception as e:
        print(f"Error comparing JSON arrays: {e}")
        return False

def write_results(output_file, results, total_score):
    """Writes benchmark results and the final total score to a CSV file."""
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['query', 'expected', 'actual', 'result', 'score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
        
        # Append total score row at the end
        writer.writerow({
            'query': 'TOTAL',
            'expected': '',
            'actual': '',
            'result': '',
            'score': total_score
        })
        print(f"Benchmark complete. Results saved to {output_file}")

# --- Benchmark Logic ---

async def run_selection_benchmark(input_file="manual.ods", output_file="qwen2.5coder14BInstruct_selection.csv"):
    """
    Tests if the LLM can correctly select the right tools/probes for a given query.
    Scoring is automatic (Pass/Fail) based on matching expected JSON output.
    """
    print(f"Starting selection benchmark using {input_file}")
    
    # Load dataset from ODS file into Pandas DataFrame
    try:
        data = pyexcel.get_data(input_file)
        sheet_name = list(data.keys())[0]
        df = pd.DataFrame(data[sheet_name][1:], columns=data[sheet_name][0])
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    results = []
    total_score = 0
    
    async with AsyncClient(timeout=None) as client:
        llm_url = os.getenv('LLM_URL')
        
        for index, row in df.iterrows():
            query = row['queries']
            expected_truth = row['truth']
            
            # Stop if required data is missing
            if query == None or expected_truth == None:
                break
            try:
                # Generate prompt and query LLM
                selection_prompt = get_selection_prompt(query)
                response = await client.post(
                    llm_url,
                    json={'prompt': selection_prompt}
                )
                
                response_data = response.json()
                model_answer = response_data['response'][1]['content']
                
                # Normalize quotes in ground truth string
                expected_truth = expected_truth.replace('”', '"').replace('“', '"')
                
                # Compare model answer with expected truth
                if compare_json_arrays(model_answer, expected_truth):
                    score = 1
                    result = "PASS"
                else:
                    score = 0
                    result = "FAIL"
                
                total_score += score
                
                results.append({
                    'query': query,
                    'expected': expected_truth,
                    'actual': model_answer,
                    'result': result,
                    'score': score
                })
                
                print(f"Query {index+1}: {result} (Score: {score})")
                
            except Exception as e:
                print(f"Error processing query {index+1}: {e}")
                results.append({
                    'query': query,
                    'expected': expected_truth,
                    'actual': "ERROR",
                    'result': "ERROR",
                    'score': 0
                })
    
    write_results(output_file, results, total_score)
    print(f"Total Score: {total_score} out of {len(results)} queries")
    return total_score, len(results)

async def run_generation_benchmark(input_file, output_file):
    """
    Tests if the LLM can generate valid JSON configurations for specific probes.
    Validates against MongoDB schemas and requires manual human scoring via console.
    """
    print(f"Starting generation benchmark using {input_file}")
    
    try:
        data = pyexcel.get_data(input_file)
        sheet_name = list(data.keys())[0]
        df = pd.DataFrame(data[sheet_name][1:], columns=data[sheet_name][0])
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    results = []
    total_score = 0
    
    # Connect to MongoDB to retrieve probe schemas
    client = mc.connect_to_probedb()
    db = client[os.getenv('MONGO_DB')]

    async with AsyncClient(timeout=None) as client:
        llm_url = os.getenv('LLM_URL')
        
        for index, row in df.iterrows():
            query = row['queries']
            probes = row['truth']

            if query == None or probes == None:
                break
            
            # Parse list of probes to test for this query
            probes = probes.replace('”', '"').replace('“', '"')
            probes = json.loads(probes)
            
            for probe in probes:
                try:
                    # Generate prompt and query LLM
                    confgen_prompt = get_confgen_prompt(probe, query)
                    response = await client.post(
                        llm_url,
                        json={'prompt': confgen_prompt}
                    )
                    
                    response_data = response.json()
                    model_answer = response_data['response'][1]['content']
                    # Strip markdown code blocks if present
                    model_answer = model_answer.replace("```json", "").replace("```", "").strip() 

                    print(query)
                    print(probe)
                    print(model_answer)
                
                    # Fetch validation schema from DB
                    schema = mc.get_document(db['probes'], {"probeName": probe}, multiple=False)
                    schema_content = schema.get('schemaContent', {})
                    
                    try:
                        # Validate JSON against schema
                        if schema_content != None:
                            validate(json.loads(model_answer), json.loads(schema_content))
                        else:
                            print("There was no schema in the DB!")
                        
                        # Request manual scoring from user
                        print("0 - sbagliata\n1 - parzialmente corretta\n2 - corretta")
                        score = int(input()) - 1 
                    except ValidationError as e:
                        print("Wrong schema")
                        score = -2 # Heavy penalty for invalid schema
                    
                    total_score += score
                    
                    results.append({
                        'query': query,
                        'expected': "",
                        'actual': model_answer,
                        'result': "",
                        'score': score
                    })
                    
                except Exception as e:
                    print(f"Error processing query {index+1}: {e}")
                    results.append({
                        'query': query,
                        'expected': "",
                        'actual': "ERROR",
                        'result': "ERROR",
                        'score': 0
                    })

    write_results(output_file, results, total_score)
    print(f"Total Score: {total_score} out of {len(results)} queries")
    return total_score, len(results)

if __name__ == "__main__":
    # Run selection benchmark (automatic scoring)
    asyncio.run(run_selection_benchmark("./datasets/7-m-m.ods", "llama3.18BInstruct_selection.csv"))
    
    # Run generation benchmark (requires manual scoring and MongoDB)
    #asyncio.run(run_generation_benchmark("./datasets/7-m-m.ods", "./results/llama3.18BInstruct_generation.csv"))