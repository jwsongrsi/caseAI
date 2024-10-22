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


# New function for replacing crime pronouns
def replace_pronouns_crimes(text, default_crimes):
    # Patterns
    crime_pattern = re.compile(r'([^\s]+죄)')
    pronoun_pattern = re.compile(r'(위 죄|이 죄)')
    
    # Find all matches
    matches = []
    for match in crime_pattern.finditer(text):
        matches.append({
            'type': 'crime',
            'text': match.group(),
            'start': match.start(),
            'end': match.end()
        })
    for match in pronoun_pattern.finditer(text):
        matches.append({
            'type': 'pronoun',
            'text': match.group(),
            'start': match.start(),
            'end': match.end()
        })
    
    # Sort matches by start position
    matches.sort(key=lambda x: x['start'])
    
    # Process the text
    output_text = ''
    last_pos = 0
    last_crime = None
    for match in matches:
        # Add text from last_pos to match['start']
        output_text += text[last_pos:match['start']]
        
        if match['type'] == 'crime':
            last_crime = match['text']
            output_text += match['text']
        elif match['type'] == 'pronoun':
            # Replace pronoun with last_crime or default crime
            if last_crime:
                output_text += last_crime
            else:
                # Use default crime
                output_text += default_crimes[0]
        last_pos = match['end']
    
    # Add remaining text
    output_text += text[last_pos:]
    return output_text