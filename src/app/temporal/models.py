from dataclasses import dataclass
from typing import List


@dataclass
class DAQWorkflowInput:
    prompt: str
    mock: bool


@dataclass
class DAQWorkflowOutput:
    qasm: str
    circuit_diagram: str
    results_plot: str


@dataclass
class ListToolsInput:
    mock: bool


@dataclass
class ChooseToolInput:
    prompt: str
    available_tools: List[dict]
    mock: bool


@dataclass
class UseToolInput:
    available_tools: List[dict]
    name: str
    args: dict
    mock: bool


@dataclass
class VerifyQASMInput:
    prompt: str
    qasm: str
    mock: bool


@dataclass
class GenerateDiagramInput:
    qasm: str


@dataclass
class SimulateInput:
    qasm: str
    mock: bool
