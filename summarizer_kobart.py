from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast
import torch

# 토크나이저 및 모델 로드
tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-summarization')
model = BartForConditionalGeneration.from_pretrained('gogamza/kobart-summarization')

# 입력 텍스트
input_text = """
지방공무원법은 공무원의 결원 발생 시 발생한 결원 수 전체에 대하여 오로지 승진임용의 방법으로 보충하도록 하거나 그 대상자에 대하여 승진임용 절차를 동시에 진행하도록 규정하지 않고, 제26조에서 \"임용권자는 공무원의 결원을 신규임용·승진임용·강임·전직 또는 전보의 방법으로 보충한다.\"라고 규정하여 임용권자에게 다양한 방식으로 결원을 보충할 수 있도록 하고 있다. 그리고 지방공무원법 및 ‘지방공무원 임용령’에서는 인사의 공정성을 높이기 위한 취지에서 임용권자가 승진임용을 할 때에는 임용하려는 결원 수에 대하여 인사위원회의 사전심의를 거치도록 하고 있다(지방공무원법 제39조 제4항, 지방공무원 임용령 제30조 제1항). 즉, 승진임용과 관련하여 인사위원회의 사전심의를 거치는 것은 임용권자가 승진임용 방식으로 인사권을 행사하고자 하는 것을 전제로 한다. 이와 달리 만약 발생한 결원 수 전체에 대하여 동시에 승진임용의 절차를 거쳐야 한다고 해석하면, 해당 기관의 연간 퇴직률, 인사적체의 상황, 승진후보자의 범위, 업무 연속성 보장의 필요성이나 재직가능 기간 등과 무관하게 연공서열에 따라서만 승진임용이 이루어지게 됨에 따라 임용권자의 승진임용에 관한 재량권이 박탈되는 결과가 초래될 수 있으므로, 임용권자는 결원 보충의 방법과 승진임용의 범위에 관한 사항을 선택하여 결정할 수 있는 재량이 있다고 보아야 할 것이다.
"""

# 인코딩
raw_input_ids = tokenizer.encode(input_text)
input_ids = [tokenizer.bos_token_id] + raw_input_ids + [tokenizer.eos_token_id]

# 텐서로 변환
input_ids = torch.tensor([input_ids])

# 요약 생성
summary_ids = model.generate(
    input_ids,
    num_beams=4,
    max_length=128,
    eos_token_id=tokenizer.eos_token_id,
    early_stopping=True
)

# 디코딩
summary = tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)

print("요약 결과:")
print(summary)
