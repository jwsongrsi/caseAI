import re
import copy
import json
from enlist_rule_fullname import enlist_rule_fullname

def split_info_brackets(data, keys_to_split): #
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
    
    # Clean the "참조조문" and "참조판례" keys
    for section, section_data in split_data.items():
        # Clean "참조조문"
        if "참조조문" in section_data and section_data["참조조문"]:
            section_data["참조조문"] = re.sub(r'\s*/\s*$', '', section_data["참조조문"])  # Remove trailing slashes and spaces

            # 조문들 풀네임으로 리스트화 
            section_data["참조조문"] = enlist_rule_fullname(section_data["참조조문"]) 
        # Clean "참조판례"
        if "참조판례" in section_data and section_data["참조판례"]:
            section_data["참조판례"] = re.sub(r'\s*/\s*$', '', section_data["참조판례"])  # Remove trailing slashes and spaces

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

# Example usage:
json_data =     {
        "판시사항": "[1] 상법 제42조 제1항이 영업양수인으로 하여금 양도인의 영업자금과 관련한 피보증인의 지위까지 승계하도록 한 규정인지 여부(소극) / 영업양수인이 위 규정에 따라 책임지는 제3자의 채권은 영업양도 당시까지 발생한 것이어야 하는지 여부(적극) 및 영업양도 당시로 보아 가까운 장래에 발생될 것이 확실한 채권도 영업양수인이 책임져야 하는지 여부(소극) [2] 민법 제481조, 제482조에서 정한 변제자대위에 의하여 원채권 및 담보권을 행사할 수 있는 범위(=변제자가 갖는 구상권의 범위 내)",
        "판결요지": "[1] 상법 제42조 제1항은 영업양수인이 양도인의 상호를 계속 사용하는 경우 양도인의 영업으로 인한 제3자의 채권에 대하여 양수인도 변제할 책임이 있다고 규정함으로써 양도인이 여전히 주채무자로서 채무를 부담하면서 양수인도 함께 변제책임을 지도록 하고 있으나, 위 규정이 영업양수인이 양도인의 영업자금과 관련한 피보증인의 지위까지 승계하도록 한 것이라고 보기는 어렵고, 영업양수인이 위 규정에 따라 책임지는 제3자의 채권은 영업양도 당시 채무의 변제기가 도래할 필요까지는 없다고 하더라도 그 당시까지 발생한 것이어야 하고, 영업양도 당시로 보아 가까운 장래에 발생될 것이 확실한 채권도 양수인이 책임져야 한다고 볼 수 없다. [2] 민법 제481조, 제482조에서 규정하고 있는 변제자대위는 제3자 또는 공동채무자의 한 사람이 주채무를 변제함으로써 채무자 또는 다른 공동채무자에 대하여 갖게 된 구상권의 효력을 확보하기 위한 제도이므로, 대위에 의한 원채권 및 담보권의 행사 범위는 구상권의 범위로 한정된다.",
        "참조조문": "[1] 상법 제42조 제1항 / [2] 민법 제481조, 제482조",
        "참조판례": "[1] 대법원 2004. 2. 13. 선고 2003다51569 판결, 대법원 2004. 12. 9. 선고 2004다35656 판결 / [2] 대법원 1999. 10. 22. 선고 98다22451 판결(공1999하, 2408), 대법원 2010. 5. 27. 선고 2009다85861 판결(공2010하, 1246)"
}

# Define the keys that need to be split based on section markers
keys_to_split_bracket = ["판시사항", "판결요지", "참조조문", "참조판례"]
keys_to_split_slash = ["판시사항"]

# Call the function to split the JSON data
def final_result(): 
    bracket_splitted = split_info_brackets(json_data, keys_to_split_bracket)
    #slash_splitted = split_into_slashes(bracket_splitted, keys_to_split_slash)
    
    return bracket_splitted

result = final_result()

# Save the result as a single JSON file
with open("split_json_data.json", 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print("Split JSON data saved to file.")
