import os
import re
import json

def clean_text(text):
    text = text.replace('\n', '')  # Remove \n
    text = text.replace('<br/>', '')  # Remove <br/>
    text = re.sub(r'\s{2,}', ' ', text)  # Replace two or more spaces with a single space

    return text

def process_json_files(input_path, output_path):
    for root, _, files in os.walk(input_path):
        for file in files:
            if file.endswith('.json'):
                input_file_path = os.path.join(root, file)
                with open(input_file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        print(f"Skipping file due to JSON decoding error: {input_file_path}")
                        continue

                # Recursively clean the JSON content
                cleaned_data = clean_json(data)

                # Save to output path
                relative_path = os.path.relpath(root, input_path)
                output_dir = os.path.join(output_path, relative_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                output_file_path = os.path.join(output_dir, file.replace('.json', '_cleaned.json'))
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

# Recursively clean text in JSON content
def clean_json(data):
    if isinstance(data, dict):
        return {key: clean_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_json(element) for element in data]
    elif isinstance(data, str):
        return clean_text(data)
    else:
        return data

def main():
    input_path = "dbs/supreme_infos_raw"  # Specify your input path here
    output_path = "dbs/supreme_infos_cleaned"  # Define the output path

    process_json_files(input_path, output_path)

if __name__ == "__main__":
    main()
