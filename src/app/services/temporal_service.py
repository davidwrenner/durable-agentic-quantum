import logging

from temporalio import client, envconfig

from src.app.temporal import constants


class TemporalService:
    config: envconfig.ClientConnectConfig

    def __init__(
        self, host: str = "temporal-server:7233", namespace: str = constants.NAMESPACE
    ) -> None:
        logging.basicConfig(level=logging.ERROR)
        config = envconfig.ClientConfig.load_client_connect_config()
        config["target_host"] = host
        config["namespace"] = namespace
        self.config = config

    async def connect(self) -> client.Client:
        return await client.Client.connect(**self.config)
