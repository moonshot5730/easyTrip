from langchain.agents import AgentType, initialize_agent

from app.cognitive_service.tools.search_travel_info import tools
from app.external.openai.openai_client import precise_llm_nano

agent = initialize_agent(
    tools=tools,
    llm=precise_llm_nano,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
)