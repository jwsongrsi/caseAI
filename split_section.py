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
            section_data["참조조문"] = enlist_rule_fullname(section_data["참조조문"]) # 조문들 리스트화
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
        "판시사항": "[1] 지방공무원의 승진임용에 관하여 임용권자에게 부여된 인사재량의 범위 / 지방공무원법 제42조의 구성요건인 ‘임용에 관하여 부당한 영향을 미치는 행위’에 해당하는지를 판단할 때 고려하여야 할 사항 [2] 지방공무원법상 공무원의 결원 발생 시 발생한 결원 수 전체에 대하여 오로지 승진임용의 방법으로 보충하거나 그 대상자에 대하여 승진임용 절차를 동시에 진행하여야 하는지 여부(소극) / 승진임용과 관련하여 인사위원회의 사전심의를 거치는 것은 임용권자가 승진임용 방식으로 인사권을 행사하고자 하는 것을 전제로 하는지 여부(적극) / 임용권자는 결원 보충의 방법과 승진임용의 범위에 관한 사항을 선택하여 결정할 수 있는 재량이 있는지 여부(적극) [3] 지방공무원법상 임용권자는 인사위원회의 심의·의결 결과와 다른 내용으로 승진대상자를 결정하여 승진임용을 할 수 있는지 여부(적극) / 인사위원회의 심의·의결 결과에 따르도록 규정한 ‘지방공무원 임용령’ 제38조의5가 임용권자의 인사재량을 배제하는 규정인지 여부(소극) 및 위 규정은 임용권자로 하여금 가급적 인사위원회의 심의·의결 결과를 존중하라는 취지인지 여부(적극)",
        "판결요지": "[1] 지방공무원의 승진임용에 관해서는 임용권자에게 일반 국민에 대한 행정처분이나 공무원에 대한 징계처분에서와는 비교할 수 없을 정도의 광범위한 재량이 부여되어 있다. 따라서 승진임용자의 자격을 정한 관련 법령 규정에 위배되지 아니하고 사회통념상 합리성을 갖춘 사유에 따른 것이라는 일응의 주장·증명이 있다면 쉽사리 위법하다고 판단하여서는 아니 된다. 특히 임용권자의 인사와 관련한 행위에 대하여 형사처벌을 하는 경우에는 임용권자의 광범위한 인사재량권을 고려하여 해당 규정으로 인하여 임용권자의 인사재량을 부당히 박탈하는 결과가 초래되지 않도록 처벌규정을 엄격하게 해석·적용하여야 할 것이다. 따라서 \"누구든지 시험 또는 임용에 관하여 고의로 방해하거나 부당한 영향을 미치는 행위를 하여서는 아니 된다.\"라고 규정하는 지방공무원법 제42조의 ‘임용에 관하여 부당한 영향을 미치는 행위’에 해당하는지를 판단함에 있어서도 임용권자가 합리적인 재량의 범위 내에서 인사에 관한 행위를 하였다면 쉽사리 구성요건해당성을 인정하여서는 아니 된다. [2] 지방공무원법은 공무원의 결원 발생 시 발생한 결원 수 전체에 대하여 오로지 승진임용의 방법으로 보충하도록 하거나 그 대상자에 대하여 승진임용 절차를 동시에 진행하도록 규정하지 않고, 제26조에서 \"임용권자는 공무원의 결원을 신규임용·승진임용·강임·전직 또는 전보의 방법으로 보충한다.\"라고 규정하여 임용권자에게 다양한 방식으로 결원을 보충할 수 있도록 하고 있다. 그리고 지방공무원법 및 ‘지방공무원 임용령’에서는 인사의 공정성을 높이기 위한 취지에서 임용권자가 승진임용을 할 때에는 임용하려는 결원 수에 대하여 인사위원회의 사전심의를 거치도록 하고 있다(지방공무원법 제39조 제4항, 지방공무원 임용령 제30조 제1항). 즉, 승진임용과 관련하여 인사위원회의 사전심의를 거치는 것은 임용권자가 승진임용 방식으로 인사권을 행사하고자 하는 것을 전제로 한다. 이와 달리 만약 발생한 결원 수 전체에 대하여 동시에 승진임용의 절차를 거쳐야 한다고 해석하면, 해당 기관의 연간 퇴직률, 인사적체의 상황, 승진후보자의 범위, 업무 연속성 보장의 필요성이나 재직가능 기간 등과 무관하게 연공서열에 따라서만 승진임용이 이루어지게 됨에 따라 임용권자의 승진임용에 관한 재량권이 박탈되는 결과가 초래될 수 있으므로, 임용권자는 결원 보충의 방법과 승진임용의 범위에 관한 사항을 선택하여 결정할 수 있는 재량이 있다고 보아야 할 것이다. [3] 징계에 관해서는 인사위원회의 징계의결 결과에 따라 징계처분을 하여야 한다고 분명하게 규정하고 있는 반면(지방공무원법 제69조 제1항), 승진임용에 관해서는 인사위원회의 사전심의를 거치도록 규정하였을 뿐 그 심의·의결 결과에 따라야 한다고 규정하고 있지 않으므로, 임용권자는 인사위원회의 심의·의결 결과와는 다른 내용으로 승진대상자를 결정하여 승진임용을 할 수 있다. ‘지방공무원 임용령’ 제38조의5가 ‘임용권자는 특별한 사유가 없으면 소속 공무원의 승진임용을 위한 인사위원회의 사전심의 또는 승진의결 결과에 따라야 한다.’라고 규정하고 있으나 위 규정은 지방공무원법의 구체적인 위임에 따른 것이 아니므로 그로써 임용권자의 인사재량을 배제한다고 볼 수 없으며, 문언 자체로도 특별한 사유가 있으면 임용권자가 인사위원회의 심의·의결 결과를 따르지 않을 수 있음을 전제하고 있으므로 임용권자로 하여금 가급적 인사위원회의 심의·의결 결과를 존중하라는 취지로 이해하여야 한다.",
        "참조조문": "[1] 지방공무원법 제42조, 제83조 / [2] 지방공무원법 제26조, 제39조 제4항, 지방공무원 임용령 제30조 제1항 / [3] 지방공무원법 제39조 제4항, 제69조 제1항, 지방공무원 임용령 제38조의5",
        "참조판례": "[1] 대법원 2018. 3. 27. 선고 2015두47492 판결(공2018상, 817) / [3] 대법원 2020. 12. 10. 선고 2019도17879 판결(공2021상, 240)"
}

# Define the keys that need to be split based on section markers
keys_to_split_bracket = ["판시사항", "판결요지", "참조조문", "참조판례"]
keys_to_split_slash = ["판시사항"]

# Call the function to split the JSON data
def final_result(): 
    bracket_splitted = split_info_brackets(json_data, keys_to_split_bracket)
    slash_splitted = split_into_slashes(bracket_splitted, keys_to_split_slash)
    
    return slash_splitted

result = final_result()

# Save the result as a single JSON file
with open("split_json_data.json", 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print("Split JSON data saved to file.")
