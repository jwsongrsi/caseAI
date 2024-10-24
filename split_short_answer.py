import os
import json
import re
from collections import OrderedDict

# Define input and output directories
input_folder = 'dbs/training/supreme_pansi_quiz'
output_folder = 'dbs/training/supreme_pansi_quiz/short_answer_splitted'

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Function to process each JSON object
def process_json_object(data):
    # Extract "판시사항" and process it
    pansi_sahang = data.get("판시사항", "")
    
    subjective_answers = []
    # Extract text inside "(= ...)" and remove it from the original text
    match = re.findall(r'\(=(.*?)\)', pansi_sahang)
    if match:
        subjective_answers = [text.strip() for text in match]
    
    # Remove the "(= ...)" part from the original "판시사항"
    cleaned_pansi_sahang = re.sub(r'\(=.*?\)', '', pansi_sahang).strip()
    
    # Create a new OrderedDict to control the field order
    new_data = OrderedDict()
    
    pansi_gyeolron = data.pop("판시결론", [])

    # Keep all original keys and values, but insert 판시결론_객관식 and 판시결론_주관식 after "판시사항"
    for key, value in data.items():
        if key == "판시사항":
            new_data[key] = cleaned_pansi_sahang  # Add the cleaned "판시사항"
            # Insert the two new keys right after "판시사항"
            new_data["판시결론_객관식"] = pansi_gyeolron  # Move 판시결론 to 판시결론_객관식
            new_data["판시결론_주관식"] = subjective_answers
        else:
            new_data[key] = value

    return new_data

# Process all JSON files in the input directory
for filename in os.listdir(input_folder):
    if filename.endswith('.json'):
        input_file_path = os.path.join(input_folder, filename)
        output_file_path = os.path.join(output_folder, filename)
        
        # Load the JSON data (which is a list of JSON objects)
        with open(input_file_path, 'r', encoding='utf-8') as file:
            data_list = json.load(file)
        
        # Process each JSON object in the list
        modified_data_list = [process_json_object(data) for data in data_list]
        
        # Write the modified list of JSON objects to the output file
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            json.dump(modified_data_list, output_file, ensure_ascii=False, indent=4)

print("Processing complete. Files saved to:", output_folder)
