# Use a pipeline as a high-level helper
from transformers import pipeline

messages = [
    {"role": "user", "content": """You are a highly trained cybersecurity expert tasked with selecting the most suitable probes to perform specific security assurance checks based on a given query. Your role is to carefully analyze the query, determine the required tasks, and match these requirements to the capabilities of the provided probes. Follow the instructions below with precision. 

Input details:
1. Probes List: A JSON array where each entry represents a probe, structured as follows:
[{"name": "<probe_name>", "features": "<probe_features>"}, ...]
The "name" field is the unique identifier for the probe.
The "features" field describes the probe's capabilities, including specific tools, supported protocols, and intended use cases

2. Query: A description specifying the security assurance checks to be performed. This may include tasks such as vulnerability scanning, compliance auditing, intrusion detection, or other related functions

Task:
- Evaluate the query to identify the features required to complete the requested security assurance checks.
- Match the required features with the probes provided in the list.
- Select the most suitable probes based on the following criteria:
    - Relevance: The probe must support features directly related to the query's requirements.
    - Efficiency: Prefer probes with broader or more comprehensive functionality that fulfill multiple aspects of the query when applicable.
    - Conciseness: Avoid redundant selections; choose only the necessary probes to accomplish the task

Rules for output:
- Your output must only be a JSON array listing the names of the selected probes, structured as follows:
["<probe1>", "<probe2>", ...]
- The array should list probe names in the order of their relevance to the query.
- Do not include any explanations, greetings, or additional text-only the JSON array is allowed as output

[
    {
        "name":"mqtt-base",
        "features": "The probe performs various tasks: Service availability, SSH connection, Broker version and MQTT version, Defines the user running the broker, checks anonymous login disabled, logging system enabled, MQTT flow control rules (max inflight messages, queues size), ACL configured, Config files owning, Broker-s config files permissions"
    },
    {
        "name": "mqtt-acl",
        "features": "The probe checks user permissions specified in the ACL file used by the VerneMQ broker. You can specify via the probe JSON input what user you want to check on what topic. If any of the given checks fail, the probe returns an error."
    },
    {
        "name": "mqtt-cve",
        "features":"The probe verifies the following CVEs: CVE-2021-34432"
    },
    {
        "name": "mqtt-fuzzing",
        "features": "The probe performs tests for some unexpected behaviours by sending tailored packets and then testing for the availability of the service by implementing fuzzing techniques"
    },
    {
        "name": "mqtt-tls-server",
        "features": "The probe has the goal of verifying the probe TLS configuration, checking that TLS is enabled, all the TLS-related files have the right permissions and that the certificates are valid"
    }
]


I want to verify what happens if i send a CONNECT packet to the MQTT broker using an invalid identifier. Moreover, i want to be sure that the service is being run using a non sudo user"""},
]

pipe = pipeline("text-generation", model="meta-llama/Llama-3.1-8B-Instruct")

response = pipe(messages, temperature=0.2, pad_token_id=128001)
print(response[0]['generated_text'])