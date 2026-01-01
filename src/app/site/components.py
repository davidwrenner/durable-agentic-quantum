import random
from typing import Any

from fasthtml.common import (
    Form,
    Input,
    Label,
    Button,
    Div,
    P,
    Progress,
    H3,
    H5,
    Img,
    Pre,
    Code,
)


def circuit_form() -> Any:
    placeholder_carousel = [
        "Generate a bell state",
        "Show me Deutsch's algorithm implementing a balanced oracle",
        "Use an error correction code to decode and interpret a bit-flip syndrome",
        "Demonstrate quantum teleportation of a quantum state",
        "Encode the little-endian string `01101` as a Bernstein–Vazirani oracle",
    ]

    return Div(
        P(
            "Use this tool to reliably generate quantum circuits using Qiskit, Temporal, Google GenAI, and FastMCP"
        ),
        Form(
            H5("How can we help?"),
            Input(
                id="prompt",
                name="prompt",
                required=True,
                type="text",
                placeholder=random.choice(seq=placeholder_carousel),
            ),
            H5("Config"),
            Label(
                Input(
                    id="want-code",
                    name="code",
                    type="checkbox",
                    checked=True,
                    disabled=True,
                ),
                "Generate OpenQASM 2.0 Code",
            ),
            Label(
                Input(
                    id="want-diagram",
                    name="diagram",
                    type="checkbox",
                    checked=True,
                    disabled=True,
                ),
                "Generate Matplotlib diagram",
            ),
            Label(
                Input(
                    id="want-simulate",
                    name="simulation",
                    type="checkbox",
                    checked=True,
                    disabled=True,
                ),
                "Run ideal simulation",
            ),
            Div(Button("Let's Go!", type="submit"), style={"margin-top": "12px"}),
            hx_post="/generate",
            hx_target="#result-area",
            hx_swap="innerHTML",
        ),
        id="form-container",
    )


def polling_progress(job_id: str, step_description: str) -> Any:
    return Div(
        P(f"Status: {step_description}", cls="animate-pulse"),
        Progress(value=None),
        hx_get=f"/job/{job_id}",
        hx_trigger="load delay:1s",
        hx_target="this",
        hx_swap="outerHTML",
    )


def circuit_result(result: dict) -> Any:
    return Div(
        Div(id="form-container", hx_swap_oob="true"),
        H3("Results"),
        Pre(Code(result["qasm"])),
        Div(
            Img(
                src=f"data:image/png;base64,{result['circuit_diagram']}",
                alt="Quantum Circuit",
            ),
        ),
        Div(
            Img(
                src=f"data:image/png;base64,{result['results_plot']}",
                alt="Simulation results",
                style={},
            ),
            style={"margin-top": "15px"},
        ),
        Div(
            Button(
                "Reset",
                type="reset",
                hx_get="/",
                hx_target="body",
                hx_push_url="true",
            ),
            style={"margin-top": "12px"},
        ),
    )


def failed_result() -> Any:
    return Div(
        Div(id="form-container", hx_swap_oob="true"),
        P("Something went wrong, please try again."),
        Div(
            Button(
                "Reset",
                type="reset",
                hx_get="/",
                hx_target="body",
                hx_push_url="true",
            ),
            style={"margin-top": "12px"},
        ),
    )
