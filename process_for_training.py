import re
import os
import copy
import json
from tqdm import tqdm
from datetime import datetime
from collections import OrderedDict
from functions import *
import pprint

def split_info_brackets(data, keys_to_split):
    # Create a dictionary to store the split JSONs by section number
    split_data = {}
    
    # We need to process each key in keys_to_split
    for key in keys_to_split:
        if key in data and data[key]:
            # Check if the value contains any section markers like [1], [2], etc.
            if re.search(r'\[\d+\]', data[key]):
                parts = re.split(r'(\[\d+\])', data[key])  # Split by section markers like [1], [2], etc.

                # Remove empty elements in the list
                parts = [part for part in parts if part.strip()]

                # Now combine the section markers with the corresponding content
                current_key = None
                for part in parts:
                    if re.match(r'\[\d+\]', part):  # If the part is a section marker (e.g., [1])
                        current_key = part
                        if current_key not in split_data:
                            split_data[current_key] = copy.deepcopy(data)  # Deep copy the original data
                            # Initialize keys_to_split in this section
                            for k in keys_to_split:
                                split_data[current_key][k] = ""
                    elif current_key:
                        # Ensure current_key is not None before appending content
                        split_data[current_key][key] += part.lstrip()  # Append content to the current section
                    else:
                        print(f"Warning: No valid section marker found before this content: {part}")
                        선고일자 = data["선고일자"]
                        #print(f"선고일자: {선고일자}")
            else:
                # If no section markers are found in this key
                # For each existing section, we can copy the key as is
                if split_data:
                    for section in split_data:
                        split_data[section][key] = data[key]
                else:
                    # No sections have been created yet
                    split_data["original"] = copy.deepcopy(data)
        else:
            # Key is not in data or data[key] is empty
            continue  # Skip to the next key
    return split_data

def splitted_info_cleaner (split_data):
    ### 참조조문, 참조판례 Clean ###
    for section, section_data in split_data.items():
        if "참조조문" in section_data and section_data["참조조문"]:
            section_data["참조조문"] = re.sub(r'\s*/\s*$', '', section_data["참조조문"])  # Remove trailing slashes and spaces

            # 조문들 풀네임으로 리스트화 
            section_data["참조조문"] = enlist_rule_fullname(section_data["참조조문"]) 
            
        if "참조판례" in section_data and section_data["참조판례"]:
            section_data["참조판례"] = re.sub(r'\s*/\s*$', '', section_data["참조판례"])  # Remove trailing slashes and spaces

    ### 판시사항의 지시대명사(조항 등) 구체화 ### (위 조항, 위 규정 등)
    for section, section_data in split_data.items():
        default_provisions = section_data.get("참조조문", [])

        if not default_provisions:
            default_provisions = ["알 수 없는 조문"]  # Default value if no provisions are available

        # Apply the replacement function only to the "판시사항" key if there is a slash(/)
        if "판시사항" in section_data and section_data["판시사항"] and "/" in section_data["판시사항"]:
            text = section_data["판시사항"]
            new_text = replace_pronouns_rules(text, default_provisions)          
            section_data["판시사항"] = new_text

    ### 사건명 구분 이후 나열 ### 
    for section, section_data in split_data.items():
        if "사건명" in section_data and section_data["사건명"]: 
            case_name = section_data.get("사건명", "")
            
            case_name_cleaned = re.sub(r'\[.*?\]', '', case_name) # 부연설명 삭제 
            case_name_list = case_name_cleaned.split("·")
            case_name_list = [name.strip() for name in case_name_list if name.strip()]

            section_data["사건명"] = case_name_list

    """
    ### 죄명 (위 죄 등) 구체화 ###
    for section, section_data in split_data.items():
        default_crimes = section_data.get("사건명", [])

        if not default_crimes:
            default_crimes = ["알 수 없는 사건명"] 

        if "판시사항" in section_data and section_data["판시사항"] and "/" in section_data["판시사항"]:
            text = section_data["판시사항"]
            new_text = replace_pronouns_crimes(text, default_crimes)
            section_data["판시사항"] = new_text
    """

    return list(split_data.values())

def split_info_slashes(data, keys_to_split):
    # Create a list to store the split JSONs by slash-separated sections
    split_data = []
    
    # Iterate over each data entry
    for entry in data:
        # Iterate over the keys that need to be split (e.g., 판시사항)
        for key in keys_to_split:
            if key in entry and entry[key]:
                # Split the content by slashes
                parts = entry[key].split(' / ')
                
                # Create separate entries for each part
                for part in parts:
                    new_entry = copy.deepcopy(entry)
                    new_entry[key] = part.strip()
                    split_data.append(new_entry)
            else:
                split_data.append(copy.deepcopy(entry))
    
    return split_data


def last_process(data):
    # Initialize a list to store processed elements
    final_elements = []

    # Loop over each element in the input list
    for element in data:
        # Step 1: Combine certain keys to create a new "인용판례"
        court_name = element.get("법원명", "")
        sentencing_date = element.get("선고일자", "")
        # Format the date from "YYYYMMDD" to "YYYY. MM. DD."
        formatted_date = datetime.strptime(sentencing_date, "%Y%m%d").strftime("%Y. %m. %d.")
        sentencing_type = element.get("선고", "")
        case_number = element.get("사건번호", "")
        ruling_type = element.get("판결유형", "")
        
        # Create the "인용판례" string
        citation = f"{court_name} {formatted_date} {sentencing_type} {case_number} {ruling_type}"
        
        # Step 2: Delete unwanted keys (including the ones used for "인용판례")
        keys_to_delete = ["판례정보일련번호", "법원종류코드", "사건종류코드", "판례내용", "사건번호", "선고일자", "선고", "법원명", "판결유형"]
        for key in keys_to_delete:
            if key in element:
                del element[key]
        
        # Step 3: Extract "적극" or "소극" from "판시사항" and clean it
        pansi_sisang = element.get("판시사항", "")

        # Proceed only if pansi_sisang is not None or an empty string
        if pansi_sisang:
            # Find all occurrences of variations of "적극" or "소극"
            conclusions = re.findall(r"\(([^)]*?(적극|소극)[^)]*?)\)", pansi_sisang)
            pansi_conclusion = [re.sub(r".*소극.*", "소극", re.sub(r".*적극.*", "적극", conclusion[0].strip())) for conclusion in conclusions]
            
            # Completely remove all variations of "적극" or "소극" from the original string
            cleaned_pansi_sisang = re.sub(r"\(([^)]*?(적극|소극)[^)]*?)\)", "", pansi_sisang)
        else:
            # If no 판시사항, set empty values for 판시결론 and cleaned 판시사항
            pansi_conclusion = []
            cleaned_pansi_sisang = ""

        # Update element with new fields
        element["판시결론"] = pansi_conclusion
        element["판시사항"] = cleaned_pansi_sisang.strip()

        # Step 4: Rebuild the dictionary with id at the beginning, and 판시결론 after 판시사항
        new_element = OrderedDict()

        new_element["id"] = None  # The id will be assigned later in final_result_with_ids
        new_element["인용판례"] = citation

        # Loop over the element's items to insert "판시결론" after "판시사항"
        for key, value in element.items():
            new_element[key] = value
            if key == "판시사항":
                # Insert "판시결론" immediately after "판시사항"
                new_element["판시결론"] = pansi_conclusion

        # Add processed element to the list
        final_elements.append(new_element)

    # Return the list of processed elements
    return final_elements

def final_result_with_ids(json_data, starting_id=1):
    # Initialize an empty list to hold processed elements
    processed_data = []

    # Iterate over each element in json_data
    current_id = starting_id
    for element in json_data:

        # Step 1: Split and clean the element using your existing functions
        bracket_splitted = split_info_brackets(element, ["판시사항", "판결요지", "참조조문", "참조판례"])
        cleaned_splitted = splitted_info_cleaner(bracket_splitted)
        slash_splitted = split_info_slashes(cleaned_splitted, ["판시사항"])

        # Step 2: Process the cleaned data using last_process (which may return a list)
        final_elements = last_process(slash_splitted)

        # Step 3: Check if final_elements is a list or a single element
        if isinstance(final_elements, list):
            # If it's a list, assign an id to each element in the list
            for final_element in final_elements:
                final_element['id'] = current_id
                current_id += 1
                processed_data.append(final_element)
        else:
            # If it's a single element, just assign an id and append it
            final_elements['id'] = current_id
            current_id += 1
            processed_data.append(final_elements)

    # Return the processed data and the last used id (to continue if needed)
    return processed_data, current_id


def process_all_supreme_files(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get the list of JSON files in the input folder
    files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    id_counter = 1

    # Use tqdm to create a progress bar
    for filename in tqdm(files, desc="Processing files", unit="file"):
        # Read each JSON file
        input_file_path = os.path.join(input_folder, filename)
        with open(input_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Process the JSON data
        result, id_counter = final_result_with_ids(json_data, id_counter)

        # Modify the filename: replace '_cleaned' with '_quiz'
        output_filename = filename.replace('_cleaned', '_quiz')
        output_file_path = os.path.join(output_folder, output_filename)

        # Save the result to the output folder
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        # (No need to print the filename now since tqdm shows the progress)

# Example usage
input_folder = "dbs/supreme/supreme_infos_cleaned"
output_folder = "dbs/training/supreme_pansi_quiz"

process_all_supreme_files(input_folder, output_folder)