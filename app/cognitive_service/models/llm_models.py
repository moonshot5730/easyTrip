from langchain_openai import ChatOpenAI

creative_llm_nano = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0.7,
)

creative_openai_mini = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7,
)

precise_llm_nano = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0,
)

precise_llm_mini = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
)