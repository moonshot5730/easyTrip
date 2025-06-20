from enum import Enum

SPLIT_PATTEN = "\n\n"
END_MSG = "[DONE]"

DATA_TAG = "data: "
STEP_TAG = "step: "
SEARCH_TAG = "search: "


CHAIN_START = "on_chain_start"
CHAIN_STREAM = "on_chain_stream"
CHAIN_END = "on_chain_end"

PROMPT_START = "on_prompt_start"
PROMPT_END = "on_prompt_end"

CHAT_MODEL_START = "on_chat_model_start"
CHAT_MODEL_STREAM = "on_chat_model_stream"


class SSETag(str, Enum):
    CHAT = "chat: "
    DATA = "data: "
    CHAIN = "chain: "
    NODE = "node: "
    TOOL = "tool: "
    SEARCH = "search: "

    def __str__(self):
        return self.value
