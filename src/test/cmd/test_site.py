import asyncio
from unittest.mock import AsyncMock

from pytest_mock import MockerFixture
from starlette.testclient import TestClient

from src.app.cmd import site
from src.app.temporal import constants
from src.test.conftest import TemporalClientFixture

test_client = TestClient(site.app)


def test_get_index() -> None:
    response = test_client.get("/")
    assert response.status_code == 200
    assert "How can we help?" in response.text


def test_get_robots_txt() -> None:
    response = test_client.get("/robots.txt")
    assert response.status_code == 200


async def test_post_generate(
    mocker: MockerFixture, temporal_client: TemporalClientFixture
):
    mock_connect = mocker.patch(
        target="src.app.services.temporal_service.TemporalService.connect",
        new_callable=AsyncMock,
    )
    mock_connect.return_value = temporal_client

    response = test_client.post(
        url="/generate", data={"prompt": "some user prompt"}, headers={"mock": "true"}
    )

    assert response.status_code == 200

    workflows = []
    for _ in range(25):
        workflows = [w async for w in temporal_client.list_workflows()]
        if workflows:
            break
        await asyncio.sleep(0.1)

    assert workflows
    assert constants.WORKFLOW_KEY in workflows[0].id


async def test_get_job(mocker: MockerFixture, temporal_client: TemporalClientFixture):
    mock_connect = mocker.patch(
        target="src.app.services.temporal_service.TemporalService.connect",
        new_callable=AsyncMock,
    )
    mock_connect.return_value = temporal_client

    test_client.post(
        url="/generate", data={"prompt": "some user prompt"}, headers={"mock": "true"}
    )

    workflows = []
    for _ in range(25):
        workflows = [w async for w in temporal_client.list_workflows()]
        if workflows:
            break
        await asyncio.sleep(0.1)

    assert workflows
    job_id = workflows[0].id

    response = test_client.get(url=f"/job/{job_id}")

    assert response.status_code == 200
