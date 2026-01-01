from http import HTTPStatus

from fastmcp import FastMCP
from qiskit import QuantumCircuit, qasm2
from starlette import requests, responses

mcp = FastMCP(name="qiskit-circuit-generator")


@mcp.custom_route(path="/health", methods=["GET"])
async def health_check(_: requests.Request) -> responses.Response:
    return responses.PlainTextResponse(HTTPStatus.OK)


@mcp.tool()
def bell_state() -> str:
    """
    Returns the OpenQASM 2.0 string representation demonstrating a pair of entangled qubits in a bell state.
    """
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qasm2.dumps(qc)


@mcp.tool()
def deutsch_constant() -> str:
    """
    Returns the OpenQASM 2.0 string representation of Deutsch's algorithm, including an oracle representing the constant function f(x) = 1.
    """
    qc = QuantumCircuit(2, 1)
    qc.x(1)
    qc.h(0)
    qc.h(1)
    # constant oracle
    qc.x(1)
    qc.h(0)
    qc.measure(0, 0)
    return qasm2.dumps(qc)


@mcp.tool()
def deutsch_balanced() -> str:
    """
    Returns the OpenQASM 2.0 string representation of Deutsch's algorithm, including an oracle representing the balanced function f(0) = 1, f(1) = 0.
    """
    qc = QuantumCircuit(2, 1)
    qc.x(1)
    qc.h(0)
    qc.h(1)
    # balanced oracle
    qc.cx(0, 1)
    qc.x(1)
    qc.h(0)
    qc.measure(0, 0)
    return qasm2.dumps(qc)


@mcp.tool()
def bernstein_vazirani(s: str = "0101") -> str:
    """
    Returns the OpenQASM 2.0 string representation of the Bernstein Vazirani, with an oracle function encoding a secret bitstring.

    Args:
        s: bit string secret
    """
    n = len(s)
    qc = QuantumCircuit(n + 1, n)
    qc.h(list(range(n + 1)))
    qc.z(n)
    # oracle
    for i, c in enumerate(s):
        if c == "1":
            qc.cx(i, n)

    qc.h(list(range(n)))
    qc.measure(list(range(n)), list(range(n)))
    return qasm2.dumps(qc)


@mcp.tool()
def three_qubit_bitflip_code() -> str:
    """
    Returns the OpenQASM 2.0 string representation of a 3-qubit error correction code for a single bit-flip error.
    """
    qc = QuantumCircuit(5, 1)
    # encoding
    qc.cx(0, 1)
    qc.cx(0, 2)
    # noisy channel
    ...
    # bit-flip detection
    qc.cx(0, 3)
    qc.cx(1, 3)
    qc.cx(1, 4)
    qc.cx(2, 4)
    # error correction
    qc.ccx(3, 4, 1)
    qc.x(3)
    qc.ccx(3, 4, 2)
    qc.x(3)
    qc.x(4)
    qc.ccx(3, 4, 0)
    # decoding
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.measure(0, 0)
    return qasm2.dumps(qc)


@mcp.tool()
def quantum_teleportation(n: int = 1) -> str:
    """
    Returns the OpenQASM 2.0 string representation of a quantum teleportation scheme of n qubits

    Args:
        n: the number of quantum states to be transmitted
    """
    qc = QuantumCircuit(3 * n, 3 * n)
    # prepare EPR pairs
    for i in range(n):
        qc.h(1 + 3 * i)
        qc.cx(1 + 3 * i, 2 + 3 * i)

    # Alice state encoding
    for i in range(n):
        qc.cx(0 + 3 * i, 1 + 3 * i)
        qc.h(0 + 3 * i)

    # Bob state recovery
    for i in range(n):
        qc.cx(1 + 3 * i, 2 + 3 * i)
        qc.cz(0 + 3 * i, 2 + 3 * i)

    for i in range(n):
        # Alice measurements, deferred - https://en.wikipedia.org/wiki/Deferred_measurement_principle
        qc.measure(0 + 3 * i, 0 + 3 * i)
        qc.measure(1 + 3 * i, 1 + 3 * i)
        # Bob measurement
        qc.measure(2 + 3 * i, 2 + 3 * i)

    return qasm2.dumps(qc)


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8080)
