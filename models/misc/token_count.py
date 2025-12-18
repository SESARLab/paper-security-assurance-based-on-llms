# A simple token counter using the Qwen's tokenizer. 

from transformers import AutoTokenizer
import json

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-14B-Instruct")

with open("conversation.json", 'r') as f:
    conv = json.load(f)

conversation_text = " ".join([entry["content"] for entry in conv])

tokens = tokenizer.tokenize(conversation_text)
token_count = len(tokens)

print(f"Total number of tokens in the conversation: {token_count}")