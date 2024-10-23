import re

### 나열된 조문 구체화 ###
def enlist_rule_fullname(section_data): 

    sections = [s.strip() for s in section_data.split(',')]

    def parse_section(section, current_parts):
        new_parts = {}
        # 법령 추출
        law_match = re.match(r'((?:.*?법|.*?령|.*?규칙|.*?법률)(?: 시행령| 시행규칙)?)', section)
        #law_match = re.match(r'(.*?[법령](?: 시행령)?)', section)
        if law_match:
            new_parts['법령'] = law_match.group(1)
            section = section[law_match.end():].strip()
        # 조 추출
        article_match = re.search(r'(제\d+조의?\d*)', section)
        if article_match:
            new_parts['조'] = article_match.group(1)
            section = section[article_match.end():].strip()
        # 항 추출
        paragraph_match = re.search(r'(제\d+항)', section)
        if paragraph_match:
            new_parts['항'] = paragraph_match.group(1)
            section = section[paragraph_match.end():].strip()
            # 항 다음의 [별표] 처리
            appendix_match = re.match(r'\s*(\[.*?\])', section)
            if appendix_match:
                new_parts['항'] += ' ' + appendix_match.group(1)
                section = section[appendix_match.end():].strip()
        else:
            # 항이 없을 때 조 다음의 [별표] 처리
            appendix_match = re.match(r'\s*(\[.*?\])', section)
            if appendix_match:
                if '조' in new_parts:
                    new_parts['조'] += ' ' + appendix_match.group(1)
                section = section[appendix_match.end():].strip()
        # 호 추출
        item_match = re.search(r'(제\d+호)', section)
        if item_match:
            new_parts['호'] = item_match.group(1)
            section = section[item_match.end():].strip()
        # 목 추출
        subitem_match = re.search(r'(\([가-힣]\)목(?: \d+\))?)', section)
        if subitem_match:
            new_parts['목'] = subitem_match.group(1)
            section = section[subitem_match.end():].strip()
        # 남은 텍스트 처리
        if section.strip():
            if '목' in new_parts:
                new_parts['목'] += ' ' + section.strip()
            elif '호' in new_parts:
                new_parts['호'] += ' ' + section.strip()
        # 현재 파트 업데이트
        parts_order = ['법령', '조', '항', '호', '목']
        last_updated_index = -1
        for idx, key in enumerate(parts_order):
            if key in new_parts:
                current_parts[key] = new_parts[key]
                last_updated_index = idx
        # 마지막 업데이트 이후의 파트 초기화
        for key in parts_order[last_updated_index+1:]:
            current_parts[key] = ''
        # 전체 참조 생성
        full_ref = ' '.join([current_parts[key] for key in parts_order if current_parts.get(key)])
        return full_ref, current_parts

    current_parts = {'법령': '', '조': '', '항': '', '호': '', '목': ''}
    result = []

    for section in sections:
        full_ref, current_parts = parse_section(section, current_parts)
        result.append(full_ref)

    return result 

