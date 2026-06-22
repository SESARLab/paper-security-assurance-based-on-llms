from typing import Dict, List
import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_probe_config(probe_config: Dict[str, str]) -> Dict[str, str]:
    host = probe_config['host']
    host = re.match(r'(\d+\.\d+\.\d+\.\d+|All).*', host).group(1)

    return { **probe_config, "host": host }


def jsonify_result(llm_response: str) -> List[Dict[str, str]]:
    llm_response = llm_response.strip()
    llm_response = llm_response.replace("\\n", '').replace("\\\"", '"')

    logging.debug('LLM response: %s', llm_response)

    json_result = json.loads(llm_response)

    return [clean_probe_config(probe_config) for probe_config in json_result]


if __name__ == "__main__":
    import json
    import os

    if len(os.sys.argv) != 2:
        print("Usage: python jsonify_results.py filename.py")
        print("This script converts the passed file to a full JSON file.")
        exit(1)

    filepath = os.sys.argv[1]

    filename = os.path.basename(filepath)
    folder = os.path.dirname(filepath)

    with open(filepath, "r") as read_file, open(f"{folder}/json_{filename}", "w") as write_file:
        data = json.loads(read_file.read())

        for i, item in enumerate(data):
            logging.info('Jsonifying item: %d', i)
            item["conf"] = jsonify_result(item["conf"])

        json.dump(data, write_file)
        logging.info('Total items jsonified: %d', len(data))