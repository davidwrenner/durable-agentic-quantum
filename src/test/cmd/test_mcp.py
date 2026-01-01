import math
from collections import Counter

from fastmcp import Client
from qiskit import QuantumCircuit, circuit
from qiskit.circuit import CircuitInstruction
from qiskit.circuit.library import XGate, UGate

from src.app.cmd import mcp
from src.app.services import qiskit_service


def gate_counts(qc_data: circuit.quantumcircuitdata.QuantumCircuitData) -> Counter:
    return Counter([i.name for i in qc_data])


async def test_bell_state() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(name=mcp.bell_state.name, arguments={})

    qc = QuantumCircuit().from_qasm_str(tool_result.data)
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates.get("h") == 1
    assert gates.get("cx") == 1
    assert gates.get("measure") == 2
    assert "01" not in sim_results
    assert "10" not in sim_results
    assert "11" in sim_results
    assert "00" in sim_results


async def test_deutsch_constant() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.deutsch_constant.name, arguments={}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates.get("x") == 2
    assert gates.get("h") == 3
    assert gates.get("measure") == 1
    assert "1" not in sim_results
    assert "0" in sim_results


async def test_deutsch_balanced() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.deutsch_balanced.name, arguments={}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates.get("x") == 2
    assert gates.get("h") == 3
    assert gates.get("measure") == 1
    assert "0" not in sim_results
    assert "1" in sim_results


async def test_bernstein_vazirani_default_s() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.bernstein_vazirani.name, arguments={}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates.get("h") == 9
    assert gates.get("z") == 1
    assert gates.get("cx") == 2
    assert gates.get("measure") == 4
    assert "0101" in sim_results
    assert sim_results["0101"] == sum(sim_results.values())


async def test_bernstein_vazirani_with_s() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.bernstein_vazirani.name, arguments={"s": "011"}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates.get("h") == 7
    assert gates.get("z") == 1
    assert gates.get("cx") == 2
    assert gates.get("measure") == 3
    assert "011" in sim_results
    assert sim_results["011"] == sum(sim_results.values())


async def test_three_qubit_bitflip_code_no_error() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.three_qubit_bitflip_code.name, arguments={}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates.get("cx") == 8
    assert gates.get("ccx") == 3
    assert gates.get("x") == 3
    assert gates.get("measure") == 1
    assert "0" in sim_results
    assert sim_results["0"] == sum(sim_results.values())


async def test_three_qubit_bitflip_code_qubit_0_error() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.three_qubit_bitflip_code.name, arguments={}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    qc.data.insert(2, CircuitInstruction(XGate(), [qc.qregs[0][0]], []))
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates.get("cx") == 8
    assert gates.get("ccx") == 3
    assert gates.get("x") == 4
    assert gates.get("measure") == 1
    assert "0" in sim_results
    assert sim_results["0"] == sum(sim_results.values())


async def test_three_qubit_bitflip_code_qubit_1_error() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.three_qubit_bitflip_code.name, arguments={}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    qc.data.insert(2, CircuitInstruction(XGate(), [qc.qregs[0][1]], []))
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates.get("cx") == 8
    assert gates.get("ccx") == 3
    assert gates.get("x") == 4
    assert gates.get("measure") == 1
    assert "0" in sim_results
    assert sim_results["0"] == sum(sim_results.values())


async def test_three_qubit_bitflip_code_qubit_2_error() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.three_qubit_bitflip_code.name, arguments={}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    qc.data.insert(2, CircuitInstruction(XGate(), [qc.qregs[0][2]], []))
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates.get("cx") == 8
    assert gates.get("ccx") == 3
    assert gates.get("x") == 4
    assert gates.get("measure") == 1
    assert "0" in sim_results
    assert sim_results["0"] == sum(sim_results.values())


async def test_quantum_teleportation_default() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.quantum_teleportation.name, arguments={}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)

    assert gates.get("h") == 2
    assert gates.get("cx") == 3
    assert gates.get("cz") == 1
    assert gates.get("measure") == 3
    for result in sim_results.keys():
        assert result[2] == "0"


async def test_quantum_teleportation_complex_state() -> None:
    async with Client(mcp.mcp) as client:
        tool_result = await client.call_tool(
            name=mcp.quantum_teleportation.name, arguments={"n": 1}
        )

    qc = QuantumCircuit.from_qasm_str(tool_result.data)
    u = UGate(1.047 * math.pi, -3 + 0.785, 1.571)
    qc.data.insert(0, CircuitInstruction(u, [qc.qubits[0]], []))
    qc.data.insert(9, CircuitInstruction(u.inverse(), [qc.qubits[2]], []))
    gates = gate_counts(qc.data)
    sim_results = qiskit_service.QiskitService(mock=True).run(qc)
    assert gates["u"] == 2
    for result in sim_results.keys():
        assert result[2] == "0"
