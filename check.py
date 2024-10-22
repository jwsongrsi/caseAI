import re
import copy
import json
from functions.enlist_rule_fullname import enlist_rule_fullname, replace_pronouns

def split_info_brackets(data, keys_to_split):
    # Create a dictionary to store the split JSONs by section number
    split_data = {}

    # Iterate over the keys that need to be split (e.g., 판결요지, 판시사항)
    for key in keys_to_split:
        # Check if the value contains numbered sections like [1], [2], [3], etc.
        if key in data and data[key]:
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
                        # Remove the keys to be split from the copied data
                        for k in keys_to_split:
                            split_data[current_key][k] = ""
                else:
                    split_data[current_key][key] += part.lstrip()  # Append content to the current section

    ### Clean the "참조조문" and "참조판례" keys ###
    for section, section_data in split_data.items():
        # Clean "참조조문"
        if "참조조문" in section_data and section_data["참조조문"]:
            section_data["참조조문"] = re.sub(r'\s*/\s*$', '', section_data["참조조문"])  # Remove trailing slashes and spaces

            # 조문들 풀네임으로 리스트화 
            section_data["참조조문"] = enlist_rule_fullname(section_data["참조조문"]) 
        # Clean "참조판례"
        if "참조판례" in section_data and section_data["참조판례"]:
            section_data["참조판례"] = re.sub(r'\s*/\s*$', '', section_data["참조판례"])  # Remove trailing slashes and spaces

    ### Now process the "판시사항" field to replace pronouns ###
    for section, section_data in split_data.items():
        default_provisions = section_data.get("참조조문", [])
        if not default_provisions:
            default_provisions = ["알 수 없는 조문"]  # Default value if no provisions are available

        # Apply the replacement function only to the "판시사항" key
        if "판시사항" in section_data and section_data["판시사항"] and "/" in section_data["판시사항"]:
            text = section_data["판시사항"]
            # Replace pronouns with provisions
            new_text = replace_pronouns(text, default_provisions)
            section_data["판시사항"] = new_text

    return list(split_data.values())

def split_into_slashes(data, keys_to_split):
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

def final_result():
    # Your existing json_data
    json_data = {
        "판시사항": "금전 대여 등에 부당행위계산의 부인을 적용할 때 시가로 하는 인정이자율을 정한 구 법인세법 시행령 제89조 제3항 제2호의 취지 / 법인이 위 규정에 따라 당좌대출이자율을 시가로 선택하여 적용한 후 그 이후 사업연도에 당좌대출이자율을 시가로 선택하는 경우, 다시 위 규정에 따라 그 사업연도와 이후 2개 사업연도는 당좌대출이자율을 시가로 적용하여야 하는지 여부(적극)",
        "판결요지": "구 법인세법(2018. 12. 24. 법률 제16008호로 개정되기 전의 것) 제52조 제1항 및 구 법인세법 시행령(2019. 2. 12. 대통령령 제29529호로 개정되기 전의 것, 이하 같다) 제88조 제1항 제6호, 제89조 제3항, 제5항에 따르면, 금전의 대여 등에 부당행위계산의 부인을 적용할 때 원칙적으로 ‘가중평균차입이자율’을 그 기준이 되는 시가로 하면서도, 법인이 법인세 신고와 함께 당좌대출이자율을 시가로 선택하는 경우에는 예외적으로 그 사업연도와 이후 2개 사업연도는 ‘당좌대출이자율’을 시가로 하도록 정하고 있다. 이는 납세편의를 도모하고자 법인에 시가에 대한 선택권을 부여하되, 일단 선택권을 행사한 경우 일정기간 동안 그 시가를 의무적으로 적용하게 함으로써 조세회피를 방지하는 데 그 취지가 있다. 따라서 법인이 어느 사업연도에 위와 같은 방법으로 당좌대출이자율을 시가로 선택하였다면, 구 법인세법 시행령 제89조 제3항 단서 제2호에 따라 해당 사업연도와 이후 2개 사업연도는 당좌대출이자율을 시가로 적용하여야 하고, 가중평균차입이자율을 시가로 적용할 수는 없다. 나아가 그 이후의 사업연도에 대하여도 원칙으로 돌아가 가중평균차입이자율을 시가로 하되, 법인이 위와 같은 방법으로 당좌대출이자율을 시가로 선택하는 경우에는 다시 위 규정에 따라 그 사업연도와 이후 2개 사업연도는 당좌대출이자율을 시가로 적용하여야 하고, 이와 달리 법인이 최초로 당좌대출이자율을 시가로 선택한 경우에 한하여 위 규정이 적용된다고 볼 수는 없다.",
        "참조조문": "구 법인세법(2018. 12. 24. 법률 제16008호로 개정되기 전의 것) 제52조 제1항, 제2항, 제4항, 구 법인세법 시행령(2019. 2. 12. 대통령령 제29529호로 개정되기 전의 것) 제88조 제1항 제6호, 제89조 제3항, 제5항",
        "참조판례": ""
    }

    # Define the keys that need to be split based on section markers
    keys_to_split_bracket = ["판시사항", "판결요지", "참조조문", "참조판례"]
    keys_to_split_slash = ["판시사항"]
    
    # Call the function to split the JSON data
    bracket_splitted = split_info_brackets(json_data, keys_to_split_bracket)
    slash_splitted = split_into_slashes(bracket_splitted, keys_to_split_slash)
    return slash_splitted

result = final_result()

# Save the result as a single JSON file
with open("split_json_data.json", 'w', encoding='utf-8') as f: 
    json.dump(result, f, ensure_ascii=False, indent=4) 
 
print("Split JSON data saved to file.")
