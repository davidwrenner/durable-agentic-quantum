import os
import pytest_asyncio
from temporalio import client, testing


def pytest_configure(config) -> None:
    os.environ["MPLBACKEND"] = "Agg"


type TemporalClientFixture = client.Client


@pytest_asyncio.fixture
async def temporal_client():
    async with await testing.WorkflowEnvironment.start_local() as env:
        yield env.client
