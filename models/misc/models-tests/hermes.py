import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import flash_attn
import time

tokenizer = AutoTokenizer.from_pretrained("NousResearch/DeepHermes-3-Llama-3-8B-Preview")

model = AutoModelForCausalLM.from_pretrained(
    "NousResearch/DeepHermes-3-Llama-3-8B-Preview",
    torch_dtype=torch.float16,
    device_map="auto",
    attn_implementation="flash_attention_2",
)

messages = [
    {
        "role": "system",
        "content": "You are a deep thinking AI, you may use extremely long chains of thought to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct solution prior to answering. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem."
    },
    {
        "role": "user",
        "content": "What is y if y=2*2-4+(3*2)"
    }
]

input_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors='pt').to("cuda")
generated_ids = model.generate(input_ids, max_new_tokens=2500, temperature=0.8, repetition_penalty=1.1, do_sample=True, eos_token_id=tokenizer.eos_token_id)
print(f"Generated Tokens: {generated_ids.shape[-1:]}")
response = tokenizer.decode(generated_ids[0], skip_special_tokens=True, clean_up_tokenization_space=True)
print(f"Response: {response}")