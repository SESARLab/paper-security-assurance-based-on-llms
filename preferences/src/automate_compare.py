import subprocess

prompts = ["prompt_2", "prompt_3", "prompt_4", "prompt_5", "prompt_5c", "T"]

start_from = "prompt_5"
start_index = prompts.index(start_from)

# Generate all unique (non-self) pairs starting from the `start_from` prompt
all_pairs = [
    (a, b) for i, a in enumerate(prompts[start_index:], start=start_index)
    for j, b in enumerate(prompts)
    if a != b
]

# Execute comparisons
for first, second in all_pairs:
    output_file = f"{first}_{second}.json"
    print(f"Running comparison: {first} vs {second} -> {output_file}")
    try:
        subprocess.run(["python", "compare_gpt.py", first, second], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed on {first} vs {second}: {e}")
