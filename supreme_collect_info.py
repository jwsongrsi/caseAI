import requests
import json
import xmltodict
from tqdm import tqdm
from collections import defaultdict
import os
import time

### open.law.go.kr ###

        #행정규칙   유권해석      정보      공정       금융      방통    토지     권익      고용      환경       산재     자치법규
label = ['rule', 'interpret', 'private', 'trade', 'finance', 'cast', 'land', 'right', 'employ', 'nature', 'industy', 'ordin', 'supreme']

###################### 입력창 #####################
mydata = 'supreme' #가져오려는 api 데이터 (label 참조)
maxnum = 10000 #한 파일당 최대 개수 (100의 배수)

court = '대법원'
###################################################

target_num = label.index(mydata)
targetlist = ['admrul', 'expc', 'ppc', 'ftc', 'fsc', 'kcc', 'oclt', 'acr', 'eiac', 'ecc', 'iaciac', 'ordin', 'prec']
#totalCnts =  [ 19847,   7702,  1548,  7245,   552,   811,    23,    448,   118,    266,    934,     141659] #2023.12.13 기준 

firstDict_list = ['AdmRulSearch', 'Expc', 'Ppc', 'Ftc', 'Fsc', 'Kcc', 'Oclt', 'Acr', 'Eiac', 'Ecc', 'Iaciac', 'OrdinSearch', 'PrecSearch']
firstDict_info = ['AdmRulService'] + [item + 'Service' for item in firstDict_list[1:11]] + ['LawService', 'PrecService']

target = targetlist[target_num]

# 데이터를 연도별로 저장하기 위한 딕셔너리
yearly_infos = defaultdict(list)

# 이미 저장된 데이터를 확인하고 재개할 위치 설정
processed_serials = set()
if os.path.exists('processed_serials.txt'):
    with open('processed_serials.txt', 'r', encoding='utf-8') as f:
        processed_serials = set(line.strip() for line in f.readlines())

with open(f'dbs/supreme_serial.txt', 'r', encoding='utf-8') as file:
    serials = [line.strip() for line in file.readlines()]

def save_processed_serial(serial):
    with open('processed_serials.txt', 'a', encoding='utf-8') as f:
        f.write(f"{serial}\n")

def save_yearly_info(year):
    filename = f'supreme_info_{year}.json'
    with open(filename, "w", encoding='utf-8') as json_file:
        json.dump(yearly_infos[year], json_file, ensure_ascii=False, indent=4)

def all_infos():
    for i in tqdm(range(0, len(serials))):
        serial = serials[i]
        if serial in processed_serials:
            continue

        try:
            url = 'https://www.law.go.kr/DRF/lawService.do'
            params = {'OC': 'dev', 'target': target, 'type': 'XML', 'ID': int(serial)}
            headers = {'Host': 'www.law.go.kr', 'Referer': 'https://bigcase.ai/', 'Content-Type': 'application/json'}

            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            xmlData = response.text
            jsonStr = json.dumps(xmltodict.parse(xmlData), indent=4)
            jsontext = json.loads(jsonStr)

            jsontext = jsontext[firstDict_info[target_num]]
            if '선고일자' in jsontext:
                year = str(jsontext['선고일자'])[:4]
                yearly_infos[year].append(jsontext)
                save_processed_serial(serial)

                # Save the yearly data after each year is added to
                save_yearly_info(year)

        except requests.exceptions.RequestException as e:
            print(f"Request failed for serial {serial}: {e}")
            time.sleep(5)  # Wait before retrying
            continue  # Skip to the next iteration
        
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)
            continue

all_infos()