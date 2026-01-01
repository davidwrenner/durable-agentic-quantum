import asyncio
from datetime import timedelta
from typing import Any, Coroutine
from uuid import uuid4

from fasthtml.common import fast_app, serve, Meta, Titled, Div
from temporalio.client import (
    WorkflowHandle,
    WorkflowExecutionStatus,
    WorkflowFailureError,
)
from temporalio.common import RetryPolicy
from temporalio.service import RPCError

from src.app.services import temporal_service
from src.app.site import components
from src.app.temporal import models, constants, workflow

app, _ = fast_app(
    htmlkw={"lang": "en"},
    hdrs=(
        Meta(charset="UTF-8"),
        Meta(
            name="description",
            content="Resilient quantum circuit generation with Qiskit, Temporal, Google GenAI, and FastMCP",
        ),
    ),
    static_path="src/app/site/static/",
    live=False,
)
app: Any


@app.get("/")
def get_index() -> Any:
    return (
        Titled(
            "Durable Agentic Quantum",
            Div(
                components.circuit_form(),
                Div(id="result-area"),
            ),
        ),
    )


@app.post("/generate")
async def post_generate(prompt: str, mock: bool = False) -> Any:
    client = await temporal_service.TemporalService().connect()

    coro: Coroutine[
        None, None, WorkflowHandle[workflow.DAQWorkflow, models.DAQWorkflowOutput]
    ] = client.start_workflow(
        workflow.DAQWorkflow.run,
        args=[models.DAQWorkflowInput(prompt=prompt, mock=mock)],
        id=f"{constants.WORKFLOW_KEY}-{uuid4()}",
        task_queue=constants.TASK_QUEUE,
        execution_timeout=timedelta(seconds=30),
        retry_policy=RetryPolicy(maximum_attempts=1),
    )
    handle = await asyncio.create_task(coro)

    return components.polling_progress(job_id=handle.id, step_description="Thinking...")


@app.get("/job/{job_id}")
async def get_job(job_id: str) -> Any:
    client = await temporal_service.TemporalService().connect()
    handle = client.get_workflow_handle(workflow_id=job_id)

    try:
        description = await handle.describe()
    except RPCError:
        return components.failed_result()

    status_message = {
        "list_tools": "Getting available MCP tools",
        "choose_tool": "Picking the best tool",
        "use_tool": "Generating OpenQASM",
        "verify_qasm": "Checking correctness",
        "generate_diagram": "Drawing your QuantumCircuit",
        "simulate": "Running simulation",
    }

    if description.status == WorkflowExecutionStatus.FAILED:
        return components.failed_result()
    elif description.status == WorkflowExecutionStatus.RUNNING:
        pending = description.raw_description.pending_activities
        loading_text = status_message[pending[0].activity_type.name] if pending else ""
        return components.polling_progress(
            job_id=job_id, step_description=f"{loading_text}...!"
        )

    try:
        workflow_output = await handle.result()
    except WorkflowFailureError | Exception:
        return components.failed_result()

    return components.circuit_result(workflow_output)


if __name__ == "__main__":
    serve(appname="src.app.cmd.site")
