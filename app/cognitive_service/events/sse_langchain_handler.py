from asyncio import Queue

from langchain_core.callbacks import AsyncCallbackHandler


class SSELangchainCallbackHandler(AsyncCallbackHandler):
    def __init__(self, queue: Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.queue.put(f"data: {token}\n\n")

    async def on_chain_start(self, serialized, inputs, **kwargs):
        await self.queue.put(f"data: [Chain Start] Inputs: {inputs}\n\n")

    async def on_chain_end(self, outputs, **kwargs):
        await self.queue.put(f"data: [Chain End] Outputs: {outputs}\n\n")

    async def on_tool_start(self, serialized, input_str, **kwargs):
        await self.queue.put(f"data: [Action] {input_str}\n\n")

    async def on_tool_end(self, output, **kwargs):
        await self.queue.put(f"data: [Observation] {output}\n\n")

    async def on_agent_action(self, action, **kwargs):
        await self.queue.put(f"data: [Agent Action] {action.log}\n\n")

    async def on_text(self, text: str, **kwargs):
        await self.queue.put(f"data: {text}\n\n")

    async def on_error(self, error, **kwargs):
        await self.queue.put(f"data: [ERROR] {str(error)}\n\n")


class PrintDebugHandler(AsyncCallbackHandler):
    async def on_llm_new_token(self, token: str, **kwargs):
        print("TOKEN:", token)
