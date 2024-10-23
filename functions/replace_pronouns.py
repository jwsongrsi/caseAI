import re

### 지시대명사 구체화 ###
def replace_pronouns_rules(text, default_provisions):
    # Patterns
    provision_pattern = re.compile(r'([^\s]+ 제\d+조(?: 제\d+항)?)')
    pronoun_pattern = re.compile(r'(위 규정|위 조항|위 법조항|위 법률조항)')
    # Find all matches
    matches = []
    for match in provision_pattern.finditer(text):
        matches.append({'type': 'provision', 'text': match.group(), 'start': match.start(), 'end': match.end()})
    for match in pronoun_pattern.finditer(text):
        matches.append({'type': 'pronoun', 'text': match.group(), 'start': match.start(), 'end': match.end()})
    # Sort matches by start position
    matches.sort(key=lambda x: x['start'])
    # Process the text
    output_text = ''
    last_pos = 0
    last_provision = None
    for match in matches:
        # Add text from last_pos to match['start']
        output_text += text[last_pos:match['start']]
        if match['type'] == 'provision':
            last_provision = match['text']
            output_text += match['text']
        elif match['type'] == 'pronoun':
            # Replace pronoun with last_provision
            if last_provision:
                output_text += last_provision
            else:
                # Use default provision
                output_text += default_provisions[0]
        last_pos = match['end']
    # Add remaining text
    output_text += text[last_pos:]

    return output_text

### 죄명 구체화 ### / 작동 안 함 고쳐야 됨
def replace_pronouns_crimes(text, default_crimes):
    # Step 1. 죄명 추출 
    crimes = []
    for crime in default_crimes:
        processed_crimes = []
        for part in crimes:
            if '위반' in part:
                part = part.split('위반')[0]
            processed_crimes.append(part)
        crimes.extend(processed_crimes)

    # Step 2. matching을 위한 띄어쓰기 삭제 ("위 죄"만 남겨두기)
    text_with_placeholder = text.replace(" 위 죄", "##PLACEHOLDER##")
    no_space_text = text_with_placeholder.replace(" ", "")
    no_space_text = no_space_text.replace("##PLACEHOLDER##", " 위 죄")

    # Step 3. matching
    match = re.search(r"위 죄[^\s]*", no_space_text)
    
    if not match:
        # If "위 죄" with variations is not found, return the original text
        return text
    
    index_of_위죄 = match.start()  # Get the starting position of the match
    
    # Step 2: Identify the closest matching crime before "위 죄"
    specified_crime = None
    for crime in crimes:
        crime_pos = no_space_text.rfind(crime, 0, index_of_위죄)  # Search for crime before "위 죄"
        if crime_pos != -1:
            specified_crime = crime
            break  # Stop as soon as we find the closest match
    
    if specified_crime is None:
        # If no matching crime is found, return the original text
        return text
    
    # Step 3: Find the corresponding default_crime from default_crimes
    for i, crime in enumerate(crimes):
        if crime == specified_crime:
            default_version = default_crimes[i]
            break
    
    # Step 4: Replace the "위 " part in the original text, preserving the "죄" part naturally
    replaced_text = text.replace("위 죄", default_version)


    print(replaced_text)
    
    return replaced_text