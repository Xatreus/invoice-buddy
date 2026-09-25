import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session

from invoice_buddy.tools.registry import registry


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "openrouter",
).lower()

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free",
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3-flash-preview",
)

MAX_TOOL_STEPS = 3
REQUEST_TIMEOUT = 30.0
MAX_TOKENS = 400


# ============================================================
# SYSTEM PROMPT
# ============================================================

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
5. You may use multiple tools when necessary.
6. When a tool result is needed to decide what to do next,
   use that result to choose the next tool.
7. Perform calculations using tool results when possible.
8. Keep final answers concise and easy to understand.
9. Include the relevant currency when discussing monetary values.
10. Do not expose internal tool names or implementation details
    to the user.
"""


# ============================================================
# OPENROUTER
# ============================================================


def create_openrouter_client() -> OpenAI:
    api_key = os.environ["OPENROUTER_API_KEY"]

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=REQUEST_TIMEOUT,
    )


# ============================================================
# GEMINI
# ============================================================


def create_gemini_client():
    from google import genai

    api_key = os.environ["GEMINI_API_KEY"]

    return genai.Client(
        api_key=api_key,
    )


# ============================================================
# TOOL SCHEMAS
# ============================================================


def get_tool_schemas() -> list[dict[str, Any]]:
    """
    Return OpenAI/OpenRouter-compatible tool schemas.
    """

    return [
        {
            "type": "function",
            "function": schema,
        }
        for schema in registry.schemas()
    ]


def get_gemini_tool_schemas() -> list[dict[str, Any]]:
    """
    Convert our registry schemas into Gemini function declarations.

    The registry already stores function names, descriptions,
    and JSON-schema parameters, so we reuse those definitions.
    """

    declarations = []

    for schema in registry.schemas():
        declarations.append(
            {
                "name": schema["name"],
                "description": schema.get(
                    "description",
                    "",
                ),
                "parameters": schema.get(
                    "parameters",
                    {
                        "type": "object",
                        "properties": {},
                    },
                ),
            }
        )

    return declarations


# ============================================================
# TOOL EXECUTION
# ============================================================


def execute_tool(
    session: Session,
    tool_name: str,
    arguments: dict[str, Any],
) -> Any:
    """
    Execute a registered Invoice Buddy tool.
    """

    tool = registry.get(tool_name)

    cleaned_arguments = {key: value for key, value in arguments.items() if key}

    return tool.function(
        session,
        **cleaned_arguments,
    )


# ============================================================
# OPENROUTER AGENT
# ============================================================


def run_openrouter_agent(
    session: Session,
    user_message: str,
) -> str:
    """
    Run the Invoice Buddy agent using OpenRouter.

    OpenRouter uses the OpenAI-compatible tool-calling format.
    """

    client = create_openrouter_client()

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

    start_time = time.perf_counter()

    for step in range(MAX_TOOL_STEPS):
        print()
        print(f"[AGENT] Step {step + 1}/{MAX_TOOL_STEPS}")

        print("[AGENT] Calling OpenRouter...")

        request_start = time.perf_counter()

        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0,
            max_tokens=MAX_TOKENS,
        )

        request_time = time.perf_counter() - request_start

        print(f"[AGENT] OpenRouter responded in {request_time:.2f}s")

        assistant_message = response.choices[0].message

        messages.append(
            assistant_message.model_dump(
                exclude_none=True,
            )
        )

        # ----------------------------------------------------
        # Final answer
        # ----------------------------------------------------

        if not assistant_message.tool_calls:
            answer = assistant_message.content or ""

            total_time = time.perf_counter() - start_time

            print(f"[AGENT] Finished in {total_time:.2f}s")

            return answer

        # ----------------------------------------------------
        # Tool calls
        # ----------------------------------------------------

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            try:
                arguments = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    "Model returned invalid JSON "
                    f"for tool {tool_name}: "
                    f"{tool_call.function.arguments}"
                ) from exc

            print()
            print(f"TOOL SELECTED: {tool_name}")

            print(f"TOOL ARGUMENTS: {arguments}")

            tool_start = time.perf_counter()

            result = execute_tool(
                session,
                tool_name,
                arguments,
            )

            tool_time = time.perf_counter() - tool_start

            print(f"[AGENT] Tool finished in {tool_time:.2f}s")

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


# ============================================================
# GEMINI AGENT
# ============================================================


def run_gemini_agent(
    session: Session,
    user_message: str,
) -> str:
    """
    Run the Invoice Buddy agent using Gemini.

    Gemini uses its own native function-calling format,
    so this loop is separate from the OpenRouter loop.
    """

    from google.genai import types

    client = create_gemini_client()

    declarations = get_gemini_tool_schemas()

    tools = [
        types.Tool(
            function_declarations=declarations,
        )
    ]

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True,
        ),
        temperature=0,
        max_output_tokens=MAX_TOKENS,
    )

    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=config,
    )

    start_time = time.perf_counter()

    for step in range(MAX_TOOL_STEPS):
        print()
        print(f"[AGENT] Step {step + 1}/{MAX_TOOL_STEPS}")

        print("[AGENT] Calling Gemini...")

        request_start = time.perf_counter()

        response = chat.send_message(user_message)

        request_time = time.perf_counter() - request_start

        print(f"[AGENT] Gemini responded in {request_time:.2f}s")

        # ----------------------------------------------------
        # Check for function calls
        # ----------------------------------------------------

        function_calls = response.function_calls

        if not function_calls:
            answer = response.text or ""

            total_time = time.perf_counter() - start_time

            print(f"[AGENT] Finished in {total_time:.2f}s")

            return answer

        # ----------------------------------------------------
        # Execute requested functions
        # ----------------------------------------------------

        function_responses = []

        for function_call in function_calls:
            tool_name = function_call.name

            arguments = dict(function_call.args or {})

            print()
            print(f"TOOL SELECTED: {tool_name}")

            print(f"TOOL ARGUMENTS: {arguments}")

            tool_start = time.perf_counter()

            result = execute_tool(
                session,
                tool_name,
                arguments,
            )

            tool_time = time.perf_counter() - tool_start

            print(f"[AGENT] Tool finished in {tool_time:.2f}s")

            function_responses.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response={
                        "result": result,
                    },
                )
            )

        # ----------------------------------------------------
        # Send tool results back to Gemini
        # ----------------------------------------------------

        user_message = types.Content(
            role="user",
            parts=function_responses,
        )

    raise RuntimeError(
        "Gemini agent exceeded the maximum number of tool-calling steps."
    )


# ============================================================
# PUBLIC AGENT ENTRY POINT
# ============================================================


def run_agent(
    session: Session,
    user_message: str,
) -> str:
    """
    Main Invoice Buddy agent entry point.

    Selects the configured LLM provider.
    """

    if LLM_PROVIDER == "openrouter":
        return run_openrouter_agent(
            session,
            user_message,
        )

    if LLM_PROVIDER == "gemini":
        return run_gemini_agent(
            session,
            user_message,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}. Use 'openrouter' or 'gemini'."
    )
