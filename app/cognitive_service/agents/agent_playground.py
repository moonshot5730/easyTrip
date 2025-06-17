from app.cognitive_service.models.llm_models import precise_llm_nano
from app.cognitive_service.prompts.intent_prompt_parser import intent_prompt_template, intent_parser

intent_chain = intent_prompt_template | precise_llm_nano | intent_parser

result = intent_chain.invoke({"input": "너는 뭐하는애야?"})
print(result)