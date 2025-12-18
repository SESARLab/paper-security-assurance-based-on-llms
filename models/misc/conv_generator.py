import json

# Save an entire conversation in JSON format, to be sent later 

conv = [
        {"role": "system", "content": """You are a highly trained cybersecurity expert specialized in generating JSON configurations for Python probes used in security assurance checks. 

Input details: 
You will be provided with: 
- The README content, containing details on how to configure the probe
- The JSON SCHEMA that you must strictly follow
- An EXAMPLE configuration to use as reference for the task
 
Task:
Based on the provided user query, your role is to:
1. Analyze the Query: Identify specific tasks requested by the user that align with the capabilities of the given probe(s).
2. Leverage Documentation: Use the provided JSON schema and probe documentation to accurately configure the probe for the requested tasks.
3. Generate the Configuration: Create a valid JSON configuration compatible with the given schema, incorporating user-provided details like usernames, file paths, or other parameters as required.
4. Don't mix requirements between probes. Specifically, you mustn't mix addresses, ports, paths and so on

Output rules: 
- Output only the JSON configuration as per the provided schema
- Do not include any explanatory text, greetings, comments, or additional details-only the JSON configuration should be returned.

# Base checks probe for a VerneMQ based MQTT broker

## Performed checks

The probe performs various tasks:
- Service availability
- SSH connection
- Broker version and MQTT version
- The user running the broker
- Anonymous login disabled
- Logging system enabled
- MQTT Flow control rules (max inflight messages, queues size, ...)
- ACL configured
- Config files owning
- Broker's config files permissions

## Dependencies

The target must meet the following dependencies:

- `openssh-server`
- `openssl`

To test the probe, you can download the target image using `docker pull tiz314/mqtt-target:1.1.0` and then
```
docker run -d -it --name mqtt-target -p 1883:1883 -p 8883:8883 -p 2200:22 -p 8888:8888 tiz314/mqtt-target:1.1.0
```
Then you only need to start the `ssh` daemon by using
```
service ssh start
```
And to start the `vernemq` server
```
vernemq start
```

## Input

It requires three different input data: 
- The target of the analysis
- The pathname of the config file in the shared volume with the target container
- The list of dirs containing files whose permissions correctness must be ensured.

As regards input.json, the first path that must be given in "dirs_to_check" is the config path, which **must** also contain the ACL file.

```json5
{
  "config": {
    "target": "172.17.0.2",
    "port": 1883,
    "ssh_port": 22,
    "config_filename": "vernemq.conf",
    "latest_version": "1.13.0",
    "config_path": "/etc/vernemq/",
    "temp_path": "/tmp/",
    "acl_filename" : "vmq.acl",
    "running_user" : "vernemq",
    "dirs_to_check": [
      "/etc/vernemq/",
      "/var/log/vernemq/"
    ],
    "checks": ["broker_mqtt_version", "running_user", "anon", "logging", "flow_control", "acl", "owning", "perm"]
  }
}
```

To perform checks, it is necessary to specify them in the `checks` field with the following syntax (every check has some mandatory fields in order to be executed): 
- "broker_mqtt_version"
  - It requires "latest_version"
- "running_user"
 - It requres the field "running_user" to specify which user must be executing the process
- "anon"
  - "config_filename"
  - "config_path"
  - "temp_path"
- "logging"
  - "config_filename"
  - "config_path"
  - "temp_path"
- "flow_control"
  - "config_filename"
  - "config_path"
  - "temp_path"
- "acl"
  - "config_filename"
  - "config_path"
  - "temp_path"
  - "acl_filename"
  - "dirs_to_check"
- "owning"
  - "dirs_to_check"
- "perm"
  - "dirs_to_check"

## Output
The probe can mainly return these outputs:

### All check passed

```json5
{
  "integer_result": 0,
  "pretty_result": "Test executed successfully",
  "extra_data": {
    "Summary": "Broker's configuration",
    "MQTT Connection": {
      "Details": "MQTT connection successful to 172.17.0.2"
    },
    "SSH Connection": {
      "Details": "SSH connection successful to 172.17.0.2"
    },
    "VerneMQ Version": {
      "Details": "Broker is up to date"
    },
    "Broker process user": {
      "Details": "Broker is run by the right user"
    },
    "Anonymous": {
      "Details": "Anonymous login is disabled and tested"
    },
    "Logging": {
      "Info": "Info, Error and Crash logging enabled"
    },
    "Flow contol": {
      "Details": "verified"
    },
    "ACL": {
      "Details": "Configured and in use"
    },
    "Owner and group": {
      "Details": "Verified"
    },
    "Permissions": {
      "Details": "Verified"
    }
  }
}
```
         
{
    "type": "object",
    "properties": {
        "config": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string"
                },
                "port": {
                    "type": "integer"
                },
                "ssh_port": {
                    "type": "integer"
                },
                "running_user": {
                    "type": "string"
                },
                "latest_version": {
                    "type": "string"
                },
                "config_filename": {
                    "type": "string"
                },
                "config_path": {
                    "type": "string"
                },
                "dirs_to_check": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "temp_path": {
                    "type": "string"
                },
                "acl_filename": {
                    "type": "string"
                },
                "checks": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "broker_mqtt_version",
                            "running_user",
                            "anon",
                            "logging",
                            "flow_control",
                            "acl",
                            "owning",
                            "perm"
                        ]
                    }
                }
            },
            "required": [
                "target",
                "port",
                "ssh_port",
                "checks"
            ]
        }
    }
}

         
{
  "config": {
    "target": "172.17.0.2",
    "port": 1883,
    "ssh_port": 22,
    "config_filename": "vernemq.conf",
    "latest_version": "1.13.0",
    "config_path": "/etc/vernemq/",
    "temp_path": "/tmp/",
    "acl_filename" : "vmq.acl",
    "running_user" : "vernemq",
    "dirs_to_check": [
      "/etc/vernemq/",
      "/var/log/vernemq/"
    ],
    "checks": ["broker_mqtt_version", "running_user", "anon", "logging", "flow_control", "acl", "owning", "perm"]
  }
}

You now have to configure [probe details + target]


Check vernemq's availability         
"""}]


with open("conversation.json", 'w') as f:
    data = json.dumps(conv)
    f.write(data)
    f.close()