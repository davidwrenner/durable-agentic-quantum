import os
from typing import Optional, List, Tuple

from dotenv import load_dotenv
from google import genai


def genai_tool_from(mcp_tool: dict) -> genai.types.Tool:
    return genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name=mcp_tool["name"],
                description=mcp_tool["description"],
                parameters=mcp_tool["inputSchema"],
            )
        ]
    )


class LLMService:
    api_key: str
    model: str
    model_temperature: float
    mock: bool

    def __init__(
        self,
        model: str = "gemini-3-flash-preview",
        model_temperature: float = 0.5,
        mock: bool = False,
    ) -> None:
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        assert self.api_key, "`GOOGLE_API_KEY` is a required environment variable"
        self.model = model
        self.model_temperature = model_temperature
        self.mock = mock

    async def choose_tool(
        self, prompt: str, available_tools: List[dict]
    ) -> Optional[list[genai.types.FunctionCall]]:
        if self.mock:
            return [genai.types.FunctionCall(args={}, name="bell_state")]

        system_instruction = """\
You are a specialized router for Quantum Computing algorithms.
Your sole task is to map the user's request to the single most appropriate tool from the provided list.

RULES:
1. Extract parameters accurately (e.g., number of qubits, gate types, register names).
2. If the user request is ambiguous, pick the tool that most closely aligns with the quantum algorithm described.
3. If no tool is appropriate, DO NOT invent a tool; simply provide no function call.
4. Ensure the tool arguments match the types defined in the tool schema.
"""

        with (
            genai.Client(  # pyrefly: ignore[bad-context-manager] # false positive within dependency
                api_key=self.api_key
            ) as genai_client
        ):
            response = await genai_client.aio.models.generate_content(
                model=self.model,
                contents=genai.types.Part.from_text(text=prompt),
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[genai_tool_from(t) for t in available_tools],
                    tool_config=genai.types.ToolConfig(
                        function_calling_config=genai.types.FunctionCallingConfig(
                            mode=genai.types.FunctionCallingConfigMode.AUTO
                        ),
                    ),
                    temperature=self.model_temperature,
                ),
            )

        return response.function_calls

    async def validate(
        self, tool_output: str, user_prompt: str
    ) -> Tuple[bool, str | None]:
        if self.mock:
            return True, ""

        system_instruction = """\
You are an expert Quantum Computing Verification Assistant. 
Your sole task is to verify if the provided OpenQASM code matches the user's requirements.
Your output must be a single boolean value (`true` or `false`) and nothing else. Do not include explanations.
Failure to comply will be really, really, really bad.

CRITERIA:
1. Qubit Count: Does it use the correct number of qubits and registers?
2. Gate Logic: Are the specific gates required (H, CNOT, etc.) applied in the correct order? Measurements are always valid unless they
contradict the spirit of the user's request circuit/algorithm.
3. Consistency: The QASM must not blatantly contradict the user's request. However, some clever tricks such as
the principle of deferred measurement or additional ancilla qubits may be present in the QASM; these should be treated as valid.
When in doubt, do not nitpick implementation details and return `true`.
"""

        validation_input = f"""\
USER PROMPT:
```text
{user_prompt}
```
QASM OUTPUT:
```qasm
{tool_output}
```
"""

        with (
            genai.Client(  # pyrefly: ignore[bad-context-manager] # false positive within dependency
                api_key=self.api_key
            ) as genai_client
        ):
            response = await genai_client.aio.models.generate_content(
                model=self.model,
                contents=genai.types.Part.from_text(text=validation_input),
                config=genai.types.GenerateContentConfig(
                    response_schema=genai.types.Schema(type=genai.types.Type.BOOLEAN),
                    system_instruction=system_instruction,
                    temperature=self.model_temperature,
                ),
            )

        return bool(response.parsed), response.text
