import os, re
from dotenv import load_dotenv 

load_dotenv()

# return the probes selection object to upload to the DB
def prepare_selection():
    selection = {"probes":[]}
 
    TMP_PATH = os.getenv("TMP_PATH")
    TARGET_NAMESPACES = os.getenv("TARGET_NAMESPACES", "").split(",")
        
    def process_folder(folder_path):
        if not os.path.isdir(folder_path):
            return
        
        readme_path = next((os.path.join(folder_path, f) for f in os.listdir(folder_path)
                            if f.lower() == "readme.md"), None)
        
        if readme_path and os.path.isfile(readme_path):
            with open(readme_path, "r", encoding="utf-8") as readme_file:
                content = readme_file.read()
        
            # Match the description between title and ##
            match = re.search(r"#\s+.*?\n\n?(.*?)(?=\n#|\Z)", content, re.DOTALL)
            if match:
                description = match.group(1).strip()
                probe_name = os.path.basename(folder_path)
                
                selection['probes'].append({
                    "name": probe_name,
                    "feature": description
                })
    
    for namespace in TARGET_NAMESPACES:
        namespace_path = os.path.join(TMP_PATH, namespace.strip())
        
        if not os.path.exists(namespace_path):
            print(f"Namespace path {namespace_path} does not exist.")
            continue
        
        for folder in os.listdir(namespace_path):
            folder_path = os.path.join(namespace_path, folder)
            process_folder(folder_path)

    return selection


# Given the namespace and the probe name, an object for DB upload is prepared from local files
def prepare_probe_to_upload(probes_list, namespace, probe_name):
    TMP_PATH = os.getenv("TMP_PATH")
    namespace_path = os.path.join(TMP_PATH, namespace.strip())
    probe_path = os.path.join(namespace_path, probe_name)
    probe = {"probeName": probe_name}

    # Find the probe in probes_list
    probe_metadata = next((p for p in probes_list if p["name"] == probe_name and p["namespace"] == namespace), None)
    
    if not probe_metadata:
        print(f"Probe {probe_name} not found in the provided probes_list.")
        return None

    probe["lastModifiedDate"] = probe_metadata.get("last_activity_at")

    if not os.path.isdir(probe_path):
        print(f"Probe path {probe_path} does not exist or is not a directory.")
        return None

    readme_path = os.path.join(probe_path, "readme.md")
    probe = add_field_from_file(readme_path, "readmeContent", probe)

    schema_path = os.path.join(probe_path, "probe", "schema.json")
    probe = add_field_from_file(schema_path, "schemaContent", probe)

    test_path = os.path.join(probe_path, "probe", "test.json")
    probe = add_field_from_file(test_path, "testContent", probe)

    return probe


# add a field to an object reading a file's content
def add_field_from_file(file_path, field_name, obj):
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                obj[field_name] = file.read()
        except Exception as e:
            print(f"Error reading test.json for probe {probe_name}: {e}")
            obj[field_name] = None
    else:
        obj[field_name] = None
    return obj



def get_probe_description_from_file(namespace, name):
    
    TMP_PATH = os.getenv("TMP_PATH")

    if not os.path.isdir(TMP_PATH):
            return
    
    readme_path = os.path.join(TMP_PATH, namespace, name, "readme.md")
    if readme_path and os.path.isfile(readme_path):
        with open(readme_path, "r", encoding="utf-8") as readme_file:
            content = readme_file.read()
        
        # Match the description between title and ##
        match = re.search(r"#\s+.*?\n\n?(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return ""

