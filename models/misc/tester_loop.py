# To locally test a given conversation. Firstly, convert the conversation in a suitable format using conv_generator, then execute this script and click ENTER when asked for. 

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json

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

def send_prompt(data, max_length = 100000, temperature = 0.3, ns = 0.3):
    
    with torch.amp.autocast('cuda'):
        response = pipe(
            data,
            max_length=max_length,
            temperature=temperature,
            do_sample=True,  
            top_p = ns,
            pad_token_id=tokenizer.pad_token_id,
        )
    
    generated_text = response[0]['generated_text']
    torch.cuda.empty_cache()  
    print("Generated Response:", generated_text)

if __name__ == "__main__":
    while True:
        print("ENTER to read next conversation")
        input()
        try:
            with open("conversation.json") as f:
                data = json.load(f)
                f.close()
                send_prompt(data)
                torch.cuda.empty_cache()
        except Exception as e:
            print(e)

