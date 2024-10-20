import re
import copy
import json

def split_json_data(data, keys_to_split):
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
    
    return list(split_data.values())

# Example usage:
# Define the keys that need to be split based on section markers
keys_to_split = ["판시사항", "판결요지", "참조조문", "참조판례"]


# Example usage:
json_data =     {
        "판례정보일련번호": "209130",
        "사건명": "임금·임금",
        "사건번호": "2016다9704, 9711",
        "선고일자": "20190814",
        "선고": "선고",
        "법원명": "대법원",
        "법원종류코드": "400201",
        "사건종류명": "민사",
        "사건종류코드": "400101",
        "판결유형": "판결",
        "판시사항": "[1] 통상임금의 개념적 징표로서 ‘고정성’을 갖추었는지 판단하는 기준 및 단체협약이나 취업규칙 등에 휴직자나 복직자 또는 징계대상자 등에 대하여 특정 임금에 대한 지급 제한사유를 규정하고 있다는 사정만으로 정상적인 근로관계를 유지하는 근로자에 대하여 그 임금이 고정적 임금에 해당하지 않는다고 할 수 있는지 여부(소극)[2] 구 근로기준법 제56조에 따라 휴일근로수당을 지급하여야 하는 휴일근로에 단체협약이나 취업규칙 등에 의하여 휴일로 정하여진 날의 근로가 포함되는지 여부(적극) 및 휴일로 정하였는지 판단하는 기준[3] 여객자동차운수업을 영위하는 甲 주식회사 등에서 운전기사로 근무한 乙 등이 월간 근무일수 15일(만근일)을 초과하는 근로일이 휴일임을 전제로 만근 초과 근로일의 1일 15시간 근로 중 8시간을 넘는 7시간 부분에 대해 휴일근로에 따른 가산수당의 지급을 구한 사안에서, 제반 사정에 비추어 甲 회사 등의 사업장에서는 만근 초과 근로일을 ‘휴일’로 정하고 있다고 보이므로 乙 등의 만근 초과 근로일 근로는 근로기준법상 가산수당이 지급되어야 하는 휴일의 근로라고 보아야 하는데도, 이와 달리 본 원심판결에 법리오해 등의 잘못이 있다고 한 사례",
        "판결요지": "[1] 근로기준법이 연장·야간·휴일 근로에 대한 가산임금 등의 산정 기준으로 규정하고 있는 통상임금은 근로자가 소정근로시간에 통상적으로 제공하는 근로인 소정근로의 대가로 지급하기로 약정한 금품으로서, 정기적·일률적·고정적으로 지급되는 임금을 말한다. 여기서 고정적인 임금이란 명칭 여하를 불문하고 임의의 날에 소정근로시간을 근무한 근로자가 그 다음 날 퇴직한다고 하더라도 그 하루의 근로에 대한 대가로 당연하고도 확정적으로 지급받게 되는 최소한의 임금을 말하므로, 근로자가 임의의 날에 소정근로를 제공하면 업적, 성과 기타의 추가적인 조건의 충족 여부와 관계없이 당연히 지급될 것으로 예정되어 지급 여부나 지급액이 사전에 확정된 임금은 고정성을 갖춘 것으로 볼 수 있다. 단체협약이나 취업규칙 등에 휴직자나 복직자 또는 징계대상자 등에 대하여 특정 임금에 대한 지급 제한사유를 규정하고 있다 하더라도, 이는 해당 근로자의 개인적인 특수성을 고려하여 임금 지급을 제한하고 있는 것에 불과하므로, 그러한 사정만을 들어 정상적인 근로관계를 유지하는 근로자에 대하여 그 임금이 고정적 임금에 해당하지 않는다고 할 수는 없다.[2] 구 근로기준법(2018. 3. 20. 법률 제15513호로 개정되기 전의 것) 제56조에 따라 휴일근로수당으로 통상임금의 100분의 50 이상을 가산하여 지급하여야 하는 휴일근로에는 같은 법 제55조 소정의 주휴일 근로뿐만 아니라 단체협약이나 취업규칙 등에 의하여 휴일로 정하여진 날의 근로도 포함된다. 그리고 휴일로 정하였는지는 단체협약이나 취업규칙 등에 있는 휴일 관련 규정의 문언과 그러한 규정을 두게 된 경위, 해당 사업장의 근로시간에 관한 규율 체계와 관행, 근로 제공이 이루어진 경우 실제로 지급된 임금의 명목과 지급금액, 지급액의 산정 방식 등을 종합적으로 고려하여 판단하여야 한다.[3] 여객자동차운수업을 영위하는 甲 주식회사 등에서 운전기사로 근무한 乙 등이 월간 근무일수 15일(만근일)을 초과하는 근로일이 휴일임을 전제로 만근 초과 근로일의 1일 15시간 근로 중 8시간을 넘는 7시간 부분에 대해 휴일근로에 따른 가산수당의 지급을 구한 사안에서, 乙 등에게 적용되는 급여조견표상 수당 항목에 ‘연장’, ‘야간’ 외에 ‘휴일’ 항목이 별도로 있고, 휴일수당란에 월간 근무일수 15일을 초과하여 근무하는 날마다 8시간분 기본급의 50%를 가산하여 지급하는 것으로 기재되어 있는 점, 실제로 乙 등은 월간 근무일수 15일을 초과하여 근무한 날마다 8시간분 기본급의 50%에 해당하는 휴일수당을 지급받아 온 점 등 제반 사정에 비추어 보면, 甲 회사 등의 사업장에서는 만근 초과 근로일을 ‘휴일’로 정하고 있다고 봄이 타당하고, 따라서 乙 등의 만근 초과 근로일 근로는 근로기준법상 가산수당이 지급되어야 하는 휴일의 근로라고 보아야 하는데도, 이와 달리 본 원심판결에 법리오해 등의 잘못이 있다고 한 사례.",
        "참조조문": "[1] 근로기준법 제2조 제1항 제5호, 제56조, 근로기준법 시행령 제6조 제1항 / [2] 구 근로기준법(2018. 3. 20. 법률 제15513호로 개정되기 전의 것) 제55조, 제56조 / [3] 근로기준법 제56조",
        "참조판례": "[1] 대법원 2013. 12. 18. 선고 2012다89399 전원합의체 판결(공2014상, 236) / [2] 대법원 1991. 5. 14. 선고 90다14089 판결(공1991, 1617)"
    }


# Call the function to split the JSON data
result = split_json_data(json_data, keys_to_split)

# Save the result as a single JSON file
with open("split_json_data.json", 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print("Split JSON data saved to file.")
