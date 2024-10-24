

text = "성폭력범죄의 처벌 등에 관한 특례법 제13조에서 정한 ‘통신매체 이용 음란죄’의 보호법익 / 위 죄의 구성요건 중 ‘자기 또는 다른 사람의 성적 욕망을 유발하거나 만족시킬 목적’이 있는지 판단하는 기준 및 ‘성적 욕망’에 상대방을 성적으로 비하하거나 조롱하는 등 상대방에게 성적 수치심을 줌으로써 자신의 심리적 만족을 얻고자 하는 욕망이 포함되는지 여부(적극)와 이러한 ‘성적 욕망’이 상대방에 대한 분노감과 결합되어 있더라도 마찬가지인지 여부(적극)"
default_crimes = ["협박", "성폭력범죄의처벌등에관한특례법위반(통신매체이용음란)"]


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
    index_of_this_crime = no_space_text.find("위 죄")
    
    if index_of_this_crime == -1:
        # If "위 죄" is not found, return the original text
        return text
    
    # Step 2: Identify the closest matching crime before "위 죄"
    specified_crime = None
    for crime in crimes:
        crime_pos = no_space_text.rfind(crime, 0, index_of_this_crime)  # Search for crime before "위 죄"
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
    
    # Step 4: Replace "specified_crime" with "default_version" in the original text
    replaced_text = text.replace(specified_crime, default_version, 1)  # Replace only the first occurrence

    print(replaced_text)
    
    return replaced_text


replaced_text = replace_pronouns_crimes(text, default_crimes)