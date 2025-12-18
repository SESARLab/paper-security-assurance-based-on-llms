import json
import re
import torch
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import argparse

model_id = "Qwen/Qwen2.5-Coder-14B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16, 
    device_map="auto", 
    low_cpu_mem_usage=True,
)

model.config.pad_token_id = tokenizer.pad_token_id

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.float16,
    device_map="auto",
)

context = """You are a highly trained cybersecurity expert tasked with selecting the most suitable probes to perform specific security assurance checks based on a given query. Your role is to carefully analyze the query, determine the required tasks, and match these requirements to the capabilities of the provided probes. Follow the instructions below with precision.

"""

input_details = """Input details:
1. Probes List: A JSON array where each entry represents a probe, structured as follows:
[{"name": "<probe_name>", "features": "<probe_features>", "type": "<single/all>"}, ...]
The "name" field is the unique identifier for the probe.
The "features" field describes the probe's capabilities, including specific tools, supported protocols, and intended use cases
If the "type" field is equal to "All", the target must be "All" and the probe must the returned only once. 

2. Network inventory

3. Query: A description specifying the security assurance checks to be performed. This may include tasks such as vulnerability scanning, compliance auditing, intrusion detection, or other related functions

"""

task = """Task:
- Evaluate the query to identify the features required to complete the requested security assurance checks.
- Match the required features with the probes provided in the list.
- Select the most suitable probes based on the following criteria:
    - Relevance: The probe must support features directly related to the query's requirements.
    - Efficiency: Prefer probes with broader or more comprehensive functionality that fulfill multiple aspects of the query when applicable.
    - Conciseness: Avoid redundant selections; choose only the necessary probes to accomplish the task

"""

task_cot = """Task:
- Evaluate the query to identify the features required to complete the requested security assurance checks.
- Match the required features with the probes provided in the list.
- Select the most suitable probes based on the following criteria:
    - Relevance: The probe must support features directly related to the query's requirements.
    - Efficiency: Prefer probes with broader or more comprehensive functionality that fulfill multiple aspects of the query when applicable.
    - Conciseness: Avoid redundant selections; choose only the necessary probes to accomplish the task
- Think step by step and describe the reasoning process
- The output must be justifiable by the reasoning section

"""

output = """Rules for output:
- A JSON array listing the names of the selected probes, structured as follows:
[{"host": "hostname/IP - servicename", "probe": <probename>}, {"host": "hostname/IP - servicename", "probe": <probename>}, ...]
- You must avoid the ```json ``` notation

"""

output_cot = """Rules for output:
- The reasoning process
- Append a #### Delimiter
- Then, a JSON array listing the names of the selected probes, structured as follows:
[{"host": "hostname/IP - servicename", "probe": <probename>}, {"host": "hostname/IP - servicename", "probe": <probename>}, ...]
- After ####, you should only include the JSON formatted output as instructed
- You must avoid the ```json ``` notation

"""

catalogue = """All the available probes catalogue:
[
  {"name": "fairness-ssh", "features": "Uses a dataset to test an ssh installation", "last_activity_at": "2025-02-05T13:48:56.266Z", "type": "single"},
  {"name": "ai-robustness-evasion-fake", "features": "Testing evasion techniques for a ML based application", "last_activity_at": "2025-01-24T10:26:40.097Z", "type": "single"},
  {"name": "ai-integrity-behavior-simple", "features": "Testing integrity for a ML based application", "last_activity_at": "2025-01-24T20:14:08.389Z", "type": "single"},
  {"name": "ai-robustness-poisoning", "features": "Testing a ML based application with poisoning", "last_activity_at": "2025-01-24T10:12:11.136Z", "type": "single"},
  {"name": "ai-robustness-evasion", "features": "Testing a ML based application with evasion", "last_activity_at": "2025-01-24T20:16:37.727Z", "type": "single"},
  {"name": "vernemq-acl", "features": "Checks user permissions specified in the ACL file used by the VerneMQ broker.", "last_activity_at": "2024-10-14T13:20:13.359Z", "type": "single"},
  {"name": "vernemq-tls-server", "features": "Verifies TLS configuration for the MQTT broker.", "last_activity_at": "2024-10-14T13:23:25.226Z", "type": "single"},
  {"name": "vernemq-fuzzing", "features": "Performs fuzzing tests for unexpected behavior in VerneMQ MQTT services.", "last_activity_at": "2024-10-14T13:22:52.888Z", "type": "single"},
  {"name": "vernemq-cve", "features": "Verifies vulnerabilities related to CVE-2021-34432.", "last_activity_at": "2024-10-14T13:22:27.363Z", "type": "single"},
  {"name": "vernemq-base-probe", "features": "Performs various checks on a VerneMQ MQTT broker such as service availability, broker and MQTT protocol version, process owner, anonymous login status, broker logging system, MQTT flow control rules, if the ACL is in use or not, who owns the config files and config files permissions.", "last_activity_at": "2024-10-14T13:21:59.029Z", "type": "single"},
  {"name": "aide-oneshot-new", "features": "Checks a specific folder for changes based on the first scan.", "last_activity_at": "2024-07-15T14:19:15.670Z", "type": "single"},
  {"name": "heartbleed-new", "features": "Checks if the target is vulnerable to Heartbleed.", "last_activity_at": "2024-05-27T21:28:04.814Z", "type": "single"},
  {"name": "metasploit-new", "features": "A probe that performs penetration testing using Metasploit.", "last_activity_at": "2024-07-25T08:43:08.114Z", "type": "single"},
  {"name": "openvas-new", "features": "A probe to use OpenVAS for vulnerability scanning.", "last_activity_at": "2025-02-03T16:59:16.472Z", "type": "single"},
  {"name": "assurance-engine-basic-probe", "features": "A basic probe for interaction with the Assurance Engine.", "last_activity_at": "2024-05-07T16:52:45.054Z", "type": "single"},
  {"name": "Git CI basic probe", "features": "A basic Git CI probe to interact with Git CI pipelines.", "last_activity_at": "2025-01-24T22:54:48.662Z", "type": "single"},
  {"name": "Basic Git Probe", "features": "A basic Git probe, checking the status of a given repo.", "last_activity_at": "2024-03-05T09:53:34.176Z", "type": "single"},
  {"name": "Git CI Test Injection", "features": "A basic CI-based probe.", "last_activity_at": "2024-02-21T22:23:47.672Z", "type": "single"},
  {"name": "ML metric checker", "features": "Checks ML model performance metrics.", "last_activity_at": "2024-05-20T17:14:45.076Z", "type": "single"},
  {"name": "ML Assessment", "features": "ML assessment probe.", "last_activity_at": "2024-03-04T01:26:20.652Z", "type": "single"},
  {"name": "curl", "features": "Testing probe using curl.", "last_activity_at": "2024-03-04T01:25:04.257Z", "type": "single"},
  {"name": "apache-cis", "features": "Implementation of the CIS benchmark for Apache HTTP Server.", "last_activity_at": "2019-07-26T18:07:42.291Z", "type": "single"},
  {"name": "web-vuln-scan", "features": "Scans web technologies for vulnerabilities.", "last_activity_at": "2021-05-14T08:09:51.761Z", "type": "single"},
  {"name": "lightweight-vuln-scan", "features": "Checks open ports and related vulnerabilities.", "last_activity_at": "2021-05-14T08:09:51.701Z", "type": "single"},
  {"name": "inventory-verification", "features": "Verifies discovered hosts against an expected list.", "last_activity_at": "2021-05-14T08:09:51.634Z", "type": "all"},
  {"name": "observatory", "features": "Checks a website's security configuration using Mozilla guidelines.", "last_activity_at": "2024-10-08T11:40:29.934Z", "type": "single"},
  {"name": "ping", "features": "Launches a ping on a given target.", "last_activity_at": "2023-07-04T13:00:11.922Z", "type": "single"},
  {"name": "disk-free", "features": "Checks disk usage of a system.", "last_activity_at": "2021-05-14T08:09:51.245Z", "type": "single"},
  {"name": "find", "features": "Executes the find command on a given target.", "last_activity_at": "2021-01-18T02:39:57.828Z", "type": "single"},
  {"name": "sslyze", "features": "Checks TLS/SSL configuration for security misconfigurations.", "last_activity_at": "2025-02-07T12:25:26.436Z", "type": "single"},
  {"name": "ssh-scan", "features": "Assesses SSH configuration based on Mozilla guidelines.", "last_activity_at": "2023-05-21T08:36:04.502Z", "type": "single"},
  {"name": "portlist", "features": "Checks open TCP and UDP ports against a whitelist.", "last_activity_at": "2023-04-07T14:17:51.172Z", "type": "single"},
  {"name": "wp-scan", "features": "Scans WordPress sites for vulnerabilities.", "last_activity_at": "2020-01-30T13:45:27.829Z", "type": "single"},
  {"name": "openscap", "features": "Executes OpenSCAP for security compliance.", "last_activity_at": "2022-05-03T09:36:38.160Z", "type": "single"},
  {"name": "infowebsite", "features": "Tries to extract as much information as it can from a website, including CMS, libraries, and so on. A driver for [https://www.wappalyzer.com/](https://www.wappalyzer.com/). Since `wappalyzer` is written in JS, the driver requires `NodeJS` as well.\n\nWarning:\n\n- `wappalyzer` is written in NodeJS and it does not offer a *stable* CLI, therefore we need to write our own wrapper and *freeze* the version of `wappalyzer` since API may change (as I have experimented).', 'last_activity_at': '2024-12-03T12:35:17.493Z", "type":"single"},
  {"name": "joomla-checker-1", "features": "A control that uses [https://github.com/rastating/joomlavs](https://github.com/rastating/joomlavs) to scan for `Joomla` vulnerabilities.', 'last_activity_at': '2019-06-07T08:50:45.236Z", "type":"single"},
  {"name": "Prometheus Rules", "features": "Probe for executing Prometheus rules on MoonCloud", "last_activity_at": "2019-06-07T08:50:45.236Z", "type":"single"},
  {"name": "unimiwebsite", "features": "A probe to check the availability of a page on unimi website. Since the unimi website sometimes it's quite strange (for example it prints an error page but it returns a `200 OK`), we need a specific probe to check the availability.", "last_activity_at": "2019-07-23T12:09:16.690Z", "type": "single"},
  {"name": "Prometheus Raw", "features": "Collect raw metrics from a Prometheus target and apply hard-threshold bounds", "last_activity_at": "2019-07-23T12:09:16.690Z", "type": "single"},
  {"name": "pfsense-audit", "features": "Checks for common misconfigurations in pfsense", "last_activity_at": "2019-07-23T12:09:16.690Z", "type": "single"},
  {"name": "pfsense-waf", "features": "Checks WAF rules against known attack patterns", "last_activity_at": "2019-07-23T12:09:16.690Z", "type": "single"},
  {"name": "nginx-conf", "features": "Checks for given configurations against the nginx conf file", "last_activity_at": "2019-07-23T12:09:16.690Z", "type": "single"},
  {"name": "mosquitto-base-probe", "features": "Performs various checks on a Mosquito MQTT broker such as service availability, broker and MQTT protocol version, process owner, anonymous login status, broker logging system, MQTT flow control rules, if the ACL is in use or not, who owns the config files and config files permissions.", "last_activity_at": "2019-07-23T12:09:16.690Z", "type": "single"},
  {"name": "mysql-conf", "features": "Checks MySQL configuration file", "last_activity_at": "2019-07-23T12:09:16.690Z", "type": "single"},
  {"name": "postgressql-conf", "features": "Checks PostgresSQL configuration file", "last_activity_at": "2019-07-23T12:09:16.690Z", "type": "single"}
]

"""

prompt_1 = catalogue
prompt_2 = output + catalogue
prompt_3 = context + output + catalogue
prompt_4 = context + input_details + output + catalogue
prompt_5 = context + input_details + task + output + catalogue
prompt_5c = context + input_details + task_cot + output_cot + catalogue

PROMPTS = {
    "prompt_2": prompt_2,
    "prompt_3": prompt_3,
    "prompt_4": prompt_4,
    "prompt_5": prompt_5,
    "prompt_5c": prompt_5c
}

def send_prompt(prompt, input_text, max_length=10000, temperature=0.3, top_p=0.3):
    data = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": input_text}
    ]

    with torch.amp.autocast('cuda'):
        response = pipe(
            data,
            max_length=max_length,
            temperature=temperature,
            do_sample=True,
            top_p=top_p,
            pad_token_id=tokenizer.pad_token_id,
        )

    torch.cuda.empty_cache()
    return response[0]['generated_text']

def extract_json_like_block(text):
    try:
        if "###" in text:
            return text.rsplit("###", 1)[-1].strip()
        return None
    except Exception as e:
        print(f"Error extracting block after last ####: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt_type", type=str, choices=PROMPTS.keys(), required=True)
    parser.add_argument("--input_file", type=str, default="100-m-m.ods")
    args = parser.parse_args()

    prompt = PROMPTS[args.prompt_type]
    input_file = args.input_file
    output_file = input_file.replace(".ods", f"_{args.prompt_type}_results.json")

    df = pd.read_excel(input_file, engine="odf")
    if 'Input' not in df.columns:
        print("Error: 'Input' column not found.")
        return

    results = []
    for idx, row in df.iterrows():
        input_text = row['Input']
        print(f"Processing row {idx + 1}: {input_text[:50]}...")
        try:
            response = send_prompt(prompt, input_text)
            response_extracted = extract_json_like_block(json.dumps(response))
            if response_extracted is None:
                results.append({"conf": response[2]['content']})
            else:
                results.append({"conf": response_extracted})
        except Exception as e:
            print(f"Error processing row {idx + 1}: {e}")
            results.append({"conf": None})

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved results to '{output_file}'")


if __name__ == "__main__":
    main()
