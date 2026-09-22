import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session

from invoice_buddy.tools.registry import registry

load_dotenv()


MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
You are Invoice Buddy, an AI assistant that helps users understand
their company's invoices.

You have access to tools that query the invoice database.

Rules:

1. Use tools whenever the user's question requires invoice data.
2. Never invent invoice information.
3. Base financial answers on tool results.
4. If the database does not contain the requested information,
   say so clearly.
5. You may use multiple tools when necessary to answer a question.
6. When one tool result is needed to decide what to do next,
   use that result to choose the next tool.
7. Perform calculations using tool results when possible.
8. Keep final answers concise and easy to understand.
9. Include the relevant currency when discussing monetary values.
10. Do not expose internal tool names or implementation details
    to the user.
"""


def create_client() -> OpenAI:
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.environ["NVIDIA_API_KEY"],
    )


def get_tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": schema,
        }
        for schema in registry.schemas()
    ]


def execute_tool(
    session: Session,
    tool_name: str,
    arguments: dict[str, Any],
) -> Any:
    tool = registry.get(tool_name)

    cleaned_arguments = {key: value for key, value in arguments.items() if key}

    return tool.function(
        session,
        **cleaned_arguments,
    )


def run_agent(
    session: Session,
    user_message: str,
) -> str:
    client = create_client()

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    tools = get_tool_schemas()

    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0,
            max_tokens=2000,
        )

        assistant_message = response.choices[0].message

        messages.append(
            assistant_message.model_dump(
                exclude_none=True,
            )
        )

        if not assistant_message.tool_calls:
            return assistant_message.content or ""

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

        print()
        print(f"TOOL SELECTED: {tool_name}")
        print(f"TOOL ARGUMENTS: {arguments}")

        result = execute_tool(
            session,
            tool_name,
            arguments,
        )

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(
                    result,
                    default=str,
                ),
            }
        )

    raise RuntimeError("Agent exceeded the maximum number of tool-calling steps.")
