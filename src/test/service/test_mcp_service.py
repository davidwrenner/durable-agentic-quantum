from src.app.services import mcp_service


def test_init() -> None:
    server_addr = "server_addr"
    mock = True

    service = mcp_service.MCPService(server_addr, mock)

    assert service.server_addr == server_addr
    assert service.mock == mock
