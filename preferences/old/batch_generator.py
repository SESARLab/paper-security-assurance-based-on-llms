import json
import pandas as pd
import sys

def main():
    input_file = "100-m-m.ods"

    if len(sys.argv) != 4:
        print("Usage: python create_batch_jsonl.py <first_prompt> <second_prompt> <output_file>")
        sys.exit(1)

    first_name = sys.argv[1]
    second_name = sys.argv[2]
    output_file = sys.argv[3]

    df = pd.read_excel(input_file, engine="odf")
    inputs = df["Input"].dropna().astype(str).tolist()[:10]  # Limit to first 30

    # Load first prompt outputs
    if first_name == "T":
        outputs_first = df["Output"].dropna().astype(str).tolist()[:10]
        if len(outputs_first) != len(inputs):
            raise ValueError("Mismatch between number of Input and Output entries.")
        first_inputs = outputs_first
    else:
        with open(f"100-m-m_{first_name}_results.json", "r") as f:
            first_data = json.load(f)
        first_inputs = [json.dumps(item["conf"]) for item in first_data[:10]]

    # Load second prompt outputs
    if second_name == "T":
        outputs_second = df["Output"].dropna().astype(str).tolist()[:10]
        if len(outputs_second) != len(inputs):
            raise ValueError("Mismatch between number of Input and Output entries.")
        second_inputs = outputs_second
    else:
        with open(f"100-m-m_{second_name}_results.json", "r") as f:
            second_data = json.load(f)
        second_inputs = [json.dumps(item["conf"]) for item in second_data[:10]]

    if len(inputs) != len(first_inputs) or len(inputs) != len(second_inputs):
        raise ValueError("Mismatch between input and response lengths.")

    with open(output_file, "w") as f:
        for i, (query, first, second) in enumerate(zip(inputs, first_inputs, second_inputs)):
            context = """Evaluate the two responses to a given query by analyzing and comparing them based on relevance, coherence, helpfulness, and overall quality. 

You are tasked to:
- Use the given prompt and responses as input data.
- Conduct a detailed assessment of each response.
- Make a decision on which response is superior, or if both are equivalent, based upon specific evaluation criteria.

# Evaluation Criteria

1. **Relevance**: Ensure responses support features directly related to the query's requirements.
2. **Efficiency**: Prefer responses offering broader or more comprehensive functionality that fulfill multiple aspects of the query.
3. **Conciseness**: Avoid redundancy; choose responses that provide necessary and precise information without superfluous details.

# Steps

1. **Analyze Each Response**:
   - Thoroughly read and understand each response.
   - Determine the level of relevance to the query.
   - Check coherence to ensure logical flow and clarity.
   - Assess helpfulness by how well it answers the query.

2. **Compare Responses**:
   - Directly compare the relevance and efficiency of each response.
   - Identify any redundant or unnecessary parts in both responses.
   - Evaluate the overall quality in context to the prompt.

3. **Decision-Making**:
   - Conclude which response is more effective based on the criteria.
   - Use a step-by-step rationale to describe how the decision was reached.

# Output Format

- Provide a detailed explanation of your reasoning process.
- Append `####`
- Then use the following to indicate your choice:
  - `0` if you prefer the first response
  - `1` if the two responses are equivalent
  - `2` if you prefer the second response

# Notes

- Always think step-by-step and ensure your reasoning is clear and justifiable.
- Make sure not to overlook any criteria while making the judgment.

Prompt: 
You are a highly trained cybersecurity expert tasked with selecting the most suitable probes to perform specific security assurance checks based on a given query. Your role is to carefully analyze the query, determine the required tasks, and match these requirements to the capabilities of the provided probes. Follow the instructions below with precision. 

Task:
- Evaluate the query to identify the features required to complete the requested security assurance checks.
- Match the required features with the probes provided in the list.
- Select the most suitable probes based on the following criteria:
    - Relevance: The probe must support features directly related to the query's requirements.
    - Efficiency: Prefer probes with broader or more comprehensive functionality that fulfill multiple aspects of the query when applicable.
    - Conciseness: Avoid redundant selections; choose only the necessary probes to accomplish the task
- Think step by step and describe the reasoning process

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
]\n""" + query + "\nFirst response:\n" + first + "\nSecond reponse:\n" + second

            json_obj = {
                "custom_id": f"request-{i+1}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": context}
                    ],
                    "max_tokens": 1000
                }
            }

            f.write(json.dumps(json_obj) + "\n")

    print(f"Batch file of 30 rows saved to {output_file}")

if __name__ == "__main__":
    main()
