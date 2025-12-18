import subprocess
import itertools

PROMPT_TYPES = ["prompt_2", "prompt_3", "prompt_4", "prompt_5", "prompt_5c"]
INPUT_FILE = "100-m-m.ods"

def run_generator(prompt_type):
    print(f"\n=== Running generator for {prompt_type} ===")
    subprocess.run(["python", "generator.py", "--prompt_type", prompt_type, "--input_file", INPUT_FILE], check=True)

def main():
    for prompt in PROMPT_TYPES:
        run_generator(prompt)

if __name__ == "__main__":
    main()
