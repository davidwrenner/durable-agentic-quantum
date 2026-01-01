from typing import List

from google.genai.types import FunctionCall
from mcp import types as mcp_types
from qiskit import QuantumCircuit
from temporalio import activity

from src.app.services import llm_service, mcp_service, qiskit_service
from src.app.temporal import models


@activity.defn
async def list_tools(input: models.ListToolsInput) -> List[mcp_types.Tool]:
    return await mcp_service.MCPService(mock=input.mock).get_available_tools()


@activity.defn
async def choose_tool(input: models.ChooseToolInput) -> FunctionCall:
    tools = await llm_service.LLMService(mock=input.mock).choose_tool(
        prompt=input.prompt, available_tools=input.available_tools
    )

    if not tools:
        raise RuntimeError("LLM was unable to pick a tool supported by the MCP server")

    return tools[0]


@activity.defn
async def use_tool(input: models.UseToolInput) -> str:
    result = await mcp_service.MCPService(mock=input.mock).call_tool(
        input.name, input.args
    )

    if result.is_error or not result.data:
        raise RuntimeError("Something went wrong trying to use the tool")

    return result.data


@activity.defn
async def verify_qasm(input: models.VerifyQASMInput) -> None:
    is_valid, raw_text = await llm_service.LLMService(
        model_temperature=0.2, mock=input.mock
    ).validate(tool_output=input.qasm, user_prompt=input.prompt)

    if not is_valid:
        raise RuntimeError(
            f"LLM unable to validate output with user input. Raw LLM text: {raw_text}"
        )


@activity.defn
def generate_diagram(input: models.GenerateDiagramInput) -> str:
    try:
        qc = QuantumCircuit().from_qasm_str(qasm_str=input.qasm)
    except Exception as e:
        raise RuntimeError(
            f"Unable to construct a QuantumCircuit from the provided QASM: {e}"
        )

    return qiskit_service.QiskitService().draw(qc)


@activity.defn
def simulate(input: models.SimulateInput) -> str:
    try:
        qc = QuantumCircuit().from_qasm_str(qasm_str=input.qasm)
    except Exception as e:
        raise RuntimeError(
            f"Unable to construct a QuantumCircuit from the provided QASM: {e}"
        )

    service = qiskit_service.QiskitService(mock=input.mock)
    results = service.run(qc)
    return service.plot(results=results)
