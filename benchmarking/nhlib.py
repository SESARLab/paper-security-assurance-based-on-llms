#Nighthawk main library
import os
from dotenv import load_dotenv 
import gitlab_client as gc, mongo_client as mc, utils
import requests, json

load_dotenv()

# Generation of prompts (taking templates from DB)

def get_selection_prompt(query):
    client = mc.connect_to_probedb()
    db = client[os.getenv('MONGO_DB')]
    # Fetch the selection prompt content
    selection_prompt = mc.get_document(db['prompts'], {"name": "selection"}, multiple=False)
    if selection_prompt:
        prompt_content = selection_prompt['content']
    else:
        raise ValueError("Selection prompt not found in the database.")

    # Fetch the probes for selection
    selection_data = mc.get_document(db['selection'])
    if selection_data:
        probes = selection_data.get('probes', '')
    else:
        raise ValueError("Selection data not found in the database.")

    prompt = f"""{prompt_content}

{probes}

{query}"""
    # here model query
    res = prompt

    client.close()

    return res


def get_confgen_prompt(probe, query):
    client = mc.connect_to_probedb()
    db = client[os.getenv('MONGO_DB')]

    # Fetch the confgen prompt content
    confgen_prompt = mc.get_document(db['prompts'], {"name": "confgen"}, multiple=False)
    if confgen_prompt:
        prompt_content = confgen_prompt['content']
    else:
        raise ValueError("Confgen prompt not found in the database.")

    # Fetch the probe info for selection
    probe_data = mc.get_document(db['probes'], {"probeName": probe}, multiple=False)
    if not probe_data:
        raise ValueError("Probe data not found in the database.")

    prompt = f"""{prompt_content}
{probe_data['readmeContent']}

{probe_data['schemaContent']}

{probe_data['testContent']}

{query}"""
    # here model query
    res = prompt

    client.close()

    return res