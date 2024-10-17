import os
import json

# Use the current directory for json files
folder_path = "dbs/supreme_infos_raw"
# Specify the output file name

# Specify the range of years to filter specific files
first_year = 1981
last_year = 1990

output_file = f'supreme_info_{first_year}_to_{last_year}.json'

# List to hold combined data
combined_data = []

# Loop through all files in the current directory
for filename in os.listdir(folder_path):
    # Check if the file is a .json file and contains a year within the specified range
    if filename.endswith('.json') and any(str(year) in filename for year in range(first_year, last_year + 1)) and filename != output_file:
        file_path = os.path.join(folder_path, filename)
        # Open and read the content of the current file
        with open(file_path, 'r', encoding='utf-8') as infile:
            content = json.load(infile)
            # Append the content to the combined data list
            combined_data.extend(content)

# Create or overwrite the output file
with open(output_file, 'w', encoding='utf-8') as outfile:
    json.dump(combined_data, outfile, ensure_ascii=False, indent=4)

print(f"All selected JSON files have been combined into '{output_file}'")