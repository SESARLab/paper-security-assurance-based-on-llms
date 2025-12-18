from openai import OpenAI
import os
os.environ['OPENAI_API_KEY'] = ""

client = OpenAI()

#batch_input_file = client.files.create(
#    file=open("batch_2_5c.json", "rb"),
#    purpose="batch"
#)

#print(batch_input_file)

#batch_input_file_id = batch_input_file.id
#client.batches.create(
#    input_file_id=batch_input_file_id,
#    endpoint="/v1/chat/completions",
#    completion_window="24h",
#    metadata={
#        "description": "nightly eval job"
#    }
#)

print(client.batches.list(limit=10))
client.batches.cancel("batch_6811fd9340d08190aa1b7680fe612762")

client.batches.cancel("batch_6811fbf03a6c8190b67bbb8ef890b722")

#const batch = client.batches.retrieve("batch_abc123")
#print(batch)