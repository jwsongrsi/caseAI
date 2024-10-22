import re
import copy
import json
from functions import *

def split_info_brackets(data, keys_to_split):
    # Create a dictionary to store the split JSONs by section number
    split_data = {}

    # Iterate over the keys that need to be split (e.g., 판결요지, 판시사항)
    for key in keys_to_split:
        # Check if the value contains numbered sections like [1], [2], [3], etc.
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
                            # Remove the keys to be split from the copied data
                            for k in keys_to_split:
                                split_data[current_key][k] = ""
                    elif current_key:
                        # Ensure current_key is not None before appending content
                        split_data[current_key][key] += part.lstrip()  # Append content to the current section
                    else:
                        # Handle case where there's no valid section marker
                        print(f"Warning: No valid section marker found before this content: {part}")
            else:
                # If no section markers are found, retain the original data
                split_data["original"] = copy.deepcopy(data)
                break  # No need to further process if there's no marker

    split_data = splitted_info_cleaner(split_data)             

    return list(split_data.values())


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

     ### 판시사항의 죄명 구체화 ### (위 죄, 등)
    for section, section_data in split_data.items():
        default_crimes = section_data.get("사건명", [])
        if not default_crimes:
            default_crimes = ["알 수 없는 죄"]  # Default value if no crime names are available
        
        if "판시사항" in section_data and section_data["판시사항"]:
            text = section_data["판시사항"]
            new_text = replace_pronouns_crimes(text, default_crimes)
            section_data["판시사항"] = new_text

    return split_data

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

def final_result():
    # Your existing json_data
    json_data =           {
        "판례정보일련번호": "219741",
        "사건명": "자본시장과금융투자업에관한법률위반·증거은닉교사·특정경제범죄가중처벌등에관한법률위반(횡령)·업무상횡령·사문서위조·위조사문서행사·주식회사등의외부감사에관한법률위반·사기",
        "사건번호": "2021도11110",
        "선고일자": "20220113",
        "선고": "선고",
        "법원명": "대법원",
        "법원종류코드": "400201",
        "사건종류명": "형사",
        "사건종류코드": "400102",
        "판결유형": "판결",
        "판시사항": "[1] 주권상장법인의 주식 등 대량보유·변동 보고의무 위반으로 인한 자본시장과 금융투자업에 관한 법률 위반죄가 진정부작위범에 해당하는지 여부(적극) / 위 죄의 공동정범은 그 의무가 수인에게 공통으로 부여되어 있는데도 수인이 공모하여 전원이 그 의무를 이행하지 않았을 때 성립하는지 여부(적극)[2] 주권상장법인의 주식 등 변경 보고의무 위반으로 인한 자본시장과 금융투자업에 관한 법률 위반죄가 진정부작위범에 해당하는지 여부(적극) / 위 죄의 공동정범은 그 의무가 수인에게 공통으로 부여되어 있는데도 수인이 공모하여 전원이 그 의무를 이행하지 않았을 때 성립하는지 여부(적극)",
        "판결요지": "[1] 자본시장과 금융투자업에 관한 법률(이하 ‘자본시장법’이라 한다) 제147조 제1항 전문은 “주권상장법인의 주식 등을 대량보유(본인과 그 특별관계자가 보유하게 되는 주식 등의 수의 합계가 그 주식 등의 총수의 100분의 5 이상인 경우를 말한다)하게 된 자는 그날부터 5일 이내에 그 보유상황, 보유 목적, 그 보유 주식 등에 관한 주요계약내용, 그 밖에 대통령령으로 정하는 사항을 대통령령으로 정하는 방법에 따라 금융위원회와 거래소에 보고하여야 하며, 그 보유 주식 등의 수의 합계가 그 주식 등의 총수의 100분의 1 이상 변동된 경우에는 그 변동된 날부터 5일 이내에 그 변동내용을 대통령령으로 정하는 방법에 따라 금융위원회와 거래소에 보고하여야 한다.”라고 규정하고 있고, 자본시장법 제445조 제20호는 제147조 제1항을 위반하여 주식 등 대량보유·변동 보고를 하지 아니한 자를 처벌한다고 규정하고 있다. 그 규정 형식과 취지에 비추어 보면 주권상장법인의 주식 등 대량보유·변동 보고의무 위반으로 인한 자본시장법 위반죄는 구성요건이 부작위에 의해서만 실현될 수 있는 진정부작위범에 해당한다. 진정부작위범인 주식 등 대량보유·변동 보고의무 위반으로 인한 자본시장법 위반죄의 공동정범은 그 의무가 수인에게 공통으로 부여되어 있는데도 수인이 공모하여 전원이 그 의무를 이행하지 않았을 때 성립할 수 있다.[2] 자본시장과 금융투자업에 관한 법률(이하 ‘자본시장법’이라 한다) 제147조 제4항은 “제1항에 따라 보고한 자는 그 보유 목적이나 그 보유 주식 등에 관한 주요계약내용 등 대통령령으로 정하는 중요한 사항의 변경이 있는 경우에는 5일 이내에 금융위원회와 거래소에 보고하여야 한다.”라고 규정하고 있고, 자본시장법 제445조 제20호는 제147조 제4항을 위반하여 주식 등 변경 보고를 하지 아니한 자를 처벌한다고 규정하고 있다. 그 규정 형식과 취지에 비추어 보면 주권상장법인의 주식 등 변경 보고의무 위반으로 인한 자본시장법 위반죄는 구성요건이 부작위에 의해서만 실현될 수 있는 진정부작위범에 해당한다. 진정부작위범인 주식 등 변경 보고의무 위반으로 인한 자본시장법 위반죄의 공동정범은 그 의무가 수인에게 공통으로 부여되어 있는데도 수인이 공모하여 전원이 그 의무를 이행하지 않았을 때 성립할 수 있다.",
        "참조조문": "[1] 자본시장과 금융투자업에 관한 법률 제147조 제1항, 제445조 제20호, 형법 제30조 / [2] 자본시장과 금융투자업에 관한 법률 제147조 제4항, 제445조 제20호, 형법 제30조",
        "참조판례": "[1][2] 대법원 2008. 3. 27. 선고 2008도89 판결(공2008상, 641), 대법원 2009. 2. 12. 선고 2008도9476 판결, 대법원 2021. 5. 7. 선고 2018도12973 판결(공2021하, 1211)"}

    # Define the keys that need to be split based on section markers
    keys_to_split_bracket = ["판시사항", "판결요지", "참조조문", "참조판례"]
    keys_to_split_slash = ["판시사항"]
    
    # Call the function to split the JSON data
    bracket_splitted = split_info_brackets(json_data, keys_to_split_bracket)
    slash_splitted = split_info_slashes(bracket_splitted, keys_to_split_slash)
    return slash_splitted

result = final_result()

# Save the result as a single JSON file
with open("split_json_data.json", 'w', encoding='utf-8') as f: 
    json.dump(result, f, ensure_ascii=False, indent=4) 
 
print("Split JSON data saved to file.")
