import pandas as pd
import json

# Load the ODS file and read only "Sheet1"
df = pd.read_excel("../../control_lists/AgID.ods", engine="odf", sheet_name="Sheet1")

# Drop unwanted columns
df = df.drop(columns=["FNSC", "Min", "Std", "Alto"])

# Convert to JSON
json_data = df.to_dict(orient="records")

# Save to output.json
with open("output_controlli.json", "w") as json_file:
    json.dump(json_data, json_file, indent=4)

print("Sheet1 with selected columns saved to output.json!")
