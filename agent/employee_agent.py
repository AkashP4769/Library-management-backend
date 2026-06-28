import os
from langchain.agents import create_agent
from langchain.messages import AIMessage
from langchain_litellm import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logging.basicConfig(level=logging.INFO)

from agent.tools import (
    search_in_policy_documents,
    make_search_address_by_employee_id,
    make_search_employee_by_id,
)

SYSTEM_PROMPT = """You are a helpful assistant EmployeeBot that can answer questions and perform tasks for HR employees.
When using tools:
- Never copy tool output verbatim.
- Summarize and rewrite information naturally.
- Search sometimes returns wrong information. If you are unsure, say "I could not find the information in the policy documents."
- Format answers using markdown.
- Use bullet points when appropriate.
- Cite the source tool when useful.
- Present information conversationally.
- If a tool returns raw text, rewrite it before responding.
"""

TOOLS_BY_NAME = {
    "search_in_policy_documents": search_in_policy_documents,
    "search_employee_by_id": make_search_employee_by_id(),
    "search_address_by_employee_id": make_search_address_by_employee_id(),
}

TOOLS = list(TOOLS_BY_NAME.values())


class EmployeeAgent:
    def __init__(self):
        self.API_KEY = os.environ["AGENT_API_KEY"]
        # self.API_BASE = os.environ['API_BASE']
        self.TOOLS_BY_NAME = TOOLS_BY_NAME

        self.llm = ChatLiteLLM(
            # api_base=self.API_BASE,
            api_key=self.API_KEY,
            model="groq/qwen/qwen3-32b",
        )
        self.messages = [
            SystemMessage(content=SYSTEM_PROMPT),
        ]

    async def stream(self, prompt: str, db):
        tools = [
            search_in_policy_documents,
            make_search_employee_by_id(db),
            make_search_address_by_employee_id(db),
        ]
        agent = create_agent(self.llm, tools)
        self.messages.append(HumanMessage(content=prompt))

        async for message, metadata in agent.astream(
            {"messages": self.messages},
            stream_mode="messages",
        ):
            if (
                isinstance(message, AIMessage)
                and not message.tool_calls
                and message.content
            ):
                logging.info(f"Agent message: {message.content}")
                yield message.content

    async def process_prompt(
        self,
        db,
        prompt: str,
    ):
        tools = [
            search_in_policy_documents,
            make_search_employee_by_id(db),
            make_search_address_by_employee_id(db),
        ]

        agent = create_agent(self.llm, tools)

        self.messages.append(HumanMessage(content=prompt))

        result = await agent.ainvoke({"messages": self.messages})
        logging.info(f"Agent result: {result['messages'][-1].content}")

        return result["messages"][-1].content


agent_map = {}


def get_agent(id) -> EmployeeAgent:
    if id not in agent_map.keys():
        agent_map[id] = EmployeeAgent()

    return agent_map.get(id)
