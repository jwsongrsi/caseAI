from transformers import GPT2LMHeadModel, PreTrainedTokenizerFast
import torch

# 토크나이저 및 모델 로드
# 카카오 KoGPT2 사용
kogpt2_tokenizer = PreTrainedTokenizerFast.from_pretrained('skt/kogpt2-base-v2')
kogpt2_model = GPT2LMHeadModel.from_pretrained('skt/kogpt2-base-v2')

# 입력 텍스트
input_text = """
부동산 실권리자명의 등기에 관한 법률(이하 ‘부동산실명법’이라 한다) 시행 전에 명의수탁자가 명의신탁 약정에 따라 부동산에 관한 소유명의를 취득한 경우에 부동산실명법의 시행 후 같은 법 제11조의 유예기간이 경과하기 전까지 명의신탁자는 언제라도 명의신탁 약정을 해지하고 해당 부동산에 관한 소유권을 취득할 수 있었던 것으로, 실명화 등의 조치 없이 위 유예기간이 경과함으로써 같은 법 제12조 제1항, 제4조에 의해 명의신탁 약정은 무효로 되는 한편, 명의수탁자가 해당 부동산에 관한 완전한 소유권을 취득하게 된다. 그런데 부동산실명법 제3조 및 제4조가 명의신탁자에게 소유권이 귀속되는 것을 막는 취지의 규정은 아니므로 명의수탁자는 명의신탁자에게 자신이 취득한 해당 부동산을 부당이득으로 반환할 의무가 있고(대법원 2002. 12. 26. 선고 2000다21123 판결, 대법원 2008. 11. 27. 선고 2008다62687 판결 등 참조), 이와 같은 경위로 명의신탁자가 해당 부동산의 회복을 위해 명의수탁자에 대해 가지는 소유권이전등기청구권은 그 성질상 법률의 규정에 의한 부당이득반환청구권으로서 민법 제162조 제1항에 따라 10년의 기간이 경과함으로써 시효로 소멸한다.
"""

# 인코딩
input_ids = kogpt2_tokenizer.encode(input_text, return_tensors='pt')

# 요약 생성
summary_ids = kogpt2_model.generate(
    input_ids,
    num_beams=4,
    max_length=128,
    eos_token_id=kogpt2_tokenizer.eos_token_id,
    early_stopping=True
)

# 디코딩
summary = kogpt2_tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)

print("요약 결과:")
print(summary)
