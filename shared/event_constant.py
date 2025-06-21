from enum import Enum

SPLIT_PATTEN = "\n\n"

class SSETag(str, Enum):
    CHAT = "chat: "
    STREAM = "stream: "
    CHAIN = "chain: "
    NODE = "node: "
    TOOL = "tool: "
    SEARCH = "search: "

    def __str__(self):
        return self.value
