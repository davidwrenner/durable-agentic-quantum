from qiskit import QuantumCircuit

from src.app.services import qiskit_service


def test_init() -> None:
    mock = True

    service = qiskit_service.QiskitService(mock)

    assert service.mock == mock


def test_run() -> None:
    service = qiskit_service.QiskitService(mock=True)
    shots = 10

    result = service.run(qc=QuantumCircuit(1, 1), shots=shots)

    assert "0" in result
    assert result["0"] == shots
