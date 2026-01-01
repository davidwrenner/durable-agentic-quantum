import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio.worker import Worker, workflow_sandbox

from src.app.services import temporal_service
from src.app.temporal import activities, constants, workflow


async def start():
    client = await temporal_service.TemporalService().connect()
    worker = Worker(
        client,
        task_queue=constants.TASK_QUEUE,
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
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(start())
