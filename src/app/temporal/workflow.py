from datetime import timedelta

from temporalio import workflow, common

from src.app.temporal import models


@workflow.defn
class DAQWorkflow:
    @workflow.run
    async def run(self, input: models.DAQWorkflowInput) -> models.DAQWorkflowOutput:
        available_tools = await workflow.execute_activity(
            "list_tools",
            models.ListToolsInput(mock=input.mock),
            retry_policy=common.RetryPolicy(maximum_attempts=1),
            start_to_close_timeout=timedelta(seconds=5),
        )

        tool = await workflow.execute_activity(
            "choose_tool",
            models.ChooseToolInput(
                prompt=input.prompt, available_tools=available_tools, mock=input.mock
            ),
            retry_policy=common.RetryPolicy(maximum_attempts=1),
            start_to_close_timeout=timedelta(seconds=10),
        )

        qasm = await workflow.execute_activity(
            "use_tool",
            models.UseToolInput(
                available_tools=available_tools,
                name=tool["name"],
                args=tool["args"],
                mock=input.mock,
            ),
            retry_policy=common.RetryPolicy(maximum_attempts=1),
            start_to_close_timeout=timedelta(seconds=3),
        )

        await workflow.execute_activity(
            "verify_qasm",
            models.VerifyQASMInput(prompt=input.prompt, qasm=qasm, mock=input.mock),
            retry_policy=common.RetryPolicy(maximum_attempts=1),
            start_to_close_timeout=timedelta(seconds=10),
        )

        circuit_diagram = await workflow.execute_activity(
            "generate_diagram",
            models.GenerateDiagramInput(qasm=qasm),
            retry_policy=common.RetryPolicy(maximum_attempts=1),
            start_to_close_timeout=timedelta(seconds=5),
        )

        simulation_result = await workflow.execute_activity(
            "simulate",
            models.SimulateInput(qasm=qasm, mock=input.mock),
            retry_policy=common.RetryPolicy(maximum_attempts=1),
            start_to_close_timeout=timedelta(seconds=5),
        )

        return models.DAQWorkflowOutput(
            qasm=qasm, circuit_diagram=circuit_diagram, results_plot=simulation_result
        )
