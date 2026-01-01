import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock

from pytest_mock import MockerFixture
from temporalio.worker import Worker, workflow_sandbox

from src.app.temporal import workflow, activities, models
from src.test.conftest import TemporalClientFixture


async def test_workflow_success(
    mocker: MockerFixture, temporal_client: TemporalClientFixture
):
    mock_connect = mocker.patch(
        target="src.app.services.temporal_service.TemporalService.connect",
        new_callable=AsyncMock,
    )
    mock_connect.return_value = temporal_client

    task_queue_name = str(uuid.uuid4())
    async with Worker(
        temporal_client,
        task_queue=task_queue_name,
        workflows=[workflow.DAQWorkflow],
        activities=[
            activities.list_tools,
            activities.choose_tool,
            activities.use_tool,
            activities.verify_qasm,
            activities.generate_diagram,
            activities.simulate,
        ],
        activity_executor=ThreadPoolExecutor(),
        workflow_runner=workflow_sandbox.SandboxedWorkflowRunner(
            restrictions=workflow_sandbox.SandboxedWorkflowRunner.restrictions.with_passthrough_modules(
                "beartype"
            )
        ),
    ):
        result = await temporal_client.execute_workflow(
            workflow.DAQWorkflow.run,
            args=[models.DAQWorkflowInput(prompt="test", mock=True)],
            id=str(uuid.uuid4()),
            task_queue=task_queue_name,
        )
        assert result
        assert len(result.qasm) == 123
        assert len(result.circuit_diagram) == 10248
        assert len(result.results_plot) == 13168
