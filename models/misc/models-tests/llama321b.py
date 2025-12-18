# Use a pipeline as a high-level helper
from transformers import pipeline

messages = [
    {"role": "user", "content": "Hello"},
]
pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-1B-Instruct")
pipe(messages)