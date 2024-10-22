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

### 죄명 구체화 ###
def replace_pronouns_crimes(text, default_crimes):
    # Initialize default_crime with the first crime in default_crimes
    default_crime = default_crimes[0]
    
    # Patterns to identify crimes and pronouns
    crime_pattern = re.compile(r'\b([가-힣\s]+죄)')
    pronoun_pattern = re.compile(r'\b(위 죄|이 죄)')

    # Find all crime and pronoun matches in the text
    matches = []
    for match in crime_pattern.finditer(text):
        crime_text = match.group()
        # Skip pronouns when capturing crimes
        if crime_text.strip() in ['위 죄', '이 죄']:
            continue
        matches.append({
            'type': 'crime',
            'text': crime_text,
            'start': match.start(),
            'end': match.end(),
            'normalized_text': re.sub(r'\s', '', crime_text)
        })
    for match in pronoun_pattern.finditer(text):
        matches.append({
            'type': 'pronoun',
            'text': match.group(),
            'start': match.start(),
            'end': match.end()
        })
    
    # Sort matches based on their position in the text
    matches.sort(key=lambda x: x['start'])
    
    # Process the text and replace crimes and pronouns
    output_text = ''
    last_pos = 0
    for match in matches:
        # Append text before the current match
        output_text += text[last_pos:match['start']]
        
        if match['type'] == 'crime':
            crime_name_no_space = match['normalized_text']
            matched = False
            # Attempt to match the crime with one from default_crimes
            for default_crime_candidate in default_crimes:
                default_crime_candidate_no_space = re.sub(r'\s', '', default_crime_candidate)
                if (default_crime_candidate_no_space in crime_name_no_space or
                    crime_name_no_space in default_crime_candidate_no_space):
                    # Update default_crime and replace in text
                    default_crime = default_crime_candidate
                    output_text += default_crime
                    matched = True
                    break
            if not matched:
                output_text += match['text']
        elif match['type'] == 'pronoun':
            # Replace pronoun with the default_crime
            output_text += default_crime + '죄'
        last_pos = match['end']
    
    # Append any remaining text after the last match
    output_text += text[last_pos:]
    return output_text
