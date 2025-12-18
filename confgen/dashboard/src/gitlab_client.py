import requests, os
from dotenv import load_dotenv 
import subprocess
from urllib.parse import quote

load_dotenv()

def get_probes_list():

    GITLAB_URL = os.getenv('GITLAB_URL')
    ACCESS_TOKEN = os.getenv('GITLAB_TOKEN')
    TARGET_NAMESPACES = os.getenv('TARGET_NAMESPACES')

    api_url = f"https://{GITLAB_URL}/api/v4/projects"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    params = {
        "per_page": 100,  
        "page": 1         
    }

    probes = []

    while True:
        response = requests.get(api_url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        data = response.json()

        if not data:  
            break

        for repo in data:
            namespace = repo.get("namespace", {}).get("path", "")
            if namespace in TARGET_NAMESPACES:

                probes.append({
                    "name": repo.get("name"),
                    "id": repo.get("id"),
                    "namespace": namespace,
                    "last_activity_at": repo.get("last_activity_at")
                })

        params["page"] += 1  # Move to the next page

    return probes

def clone_repo(namespace, repo_name):
    """
    Clone a Git repository, replacing spaces with hyphens in namespace and repo name.
    
    Args:
        namespace (str): Repository namespace/group
        repo_name (str): Repository name
    """
    # Replace spaces with hyphens
    namespace_clean = namespace.replace(' ', '-')
    repo_name_clean = repo_name.replace(' ', '-')
    
    repo_url = f"https://oauth2:{os.getenv('GITLAB_TOKEN')}@{os.getenv('GITLAB_URL')}/{namespace_clean}/{repo_name_clean}.git"
    clone_dir = os.path.join(os.getenv('TMP_PATH'), namespace, repo_name)
    
    if not os.path.exists(clone_dir):
        try:
            print(f"Cloning repository {namespace}/{repo_name} into {clone_dir}...")
            result = subprocess.run(
                ["git", "clone", repo_url, clone_dir],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"Successfully cloned {namespace}/{repo_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning {namespace}/{repo_name}: {e}")
            print(f"stderr: {e.stderr.decode()}")
    else:
        print(f"Repository {namespace}/{repo_name} already exists in {clone_dir}")

def pull_repo(namespace, repo_name):
    clone_dir = os.path.join(os.getenv('TMP_PATH'), f"{namespace}/{repo_name}")
    
    if os.path.exists(clone_dir):
        try:
            print(f"Pulling latest changes for {namespace}/{repo_name} in {clone_dir}...")
            result = subprocess.run(
                ["git", "-C", clone_dir, "pull"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"Successfully updated {namespace}/{repo_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error pulling {namespace}/{repo_name}: {e}")
            print(f"stderr: {e.stderr.decode()}")
    else:
        print(f"Repository {namespace}/{repo_name} does not exist locally. Please clone it first.")



# Clone all the available probes from probes_list in TMP_PATH
def clone_probes():
    repos = get_probes_list()
    if repos:
        print(f"Found {len(repos)} repositories:")
        for repo in repos:
            print(f"- {repo['name']} (ID: {repo['id']}, Namespace: {repo['namespace']}, Last Modified: {repo['last_activity_at']})")
            clone_repo(repo['namespace'], repo['name'])
    else:
        print("No repositories found or error occurred.")