from src.app.services import temporal_service


def test_init() -> None:
    host = "host"
    namespace = "namespace"

    service = temporal_service.TemporalService(host, namespace)

    assert service.config["target_host"] == host
    assert service.config["namespace"] == namespace
    assert "tls" not in service.config
