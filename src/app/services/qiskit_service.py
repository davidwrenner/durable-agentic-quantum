import base64
import io

from matplotlib import figure, pyplot as plt  # pyrefly: ignore[untyped-import]
from qiskit import QuantumCircuit, transpile
from qiskit.providers import basic_provider
from qiskit.visualization import plot_histogram


class QiskitService:
    mock: bool

    def __init__(
        self,
        mock: bool = False,
    ) -> None:
        self.sim = basic_provider.BasicSimulator()
        self.mock = mock

    def draw(self, qc: QuantumCircuit) -> str:
        buffer = io.BytesIO()

        fig: figure.Figure = qc.draw(  # pyrefly: ignore[bad-assignment] # Figure is correct for output='mpl'
            output="mpl"
        )
        plt.savefig(fname=buffer, format="png")
        plt.close(fig)

        png_bytes = buffer.getvalue()
        buffer.close()

        return base64.b64encode(png_bytes).decode("utf-8")

    def run(self, qc: QuantumCircuit, shots: int = 1024) -> dict:
        if self.mock:
            job = self.sim.run(
                transpile(qc.reverse_bits(), self.sim), shots=shots, seed_simulator=1024
            )
        else:
            job = self.sim.run(transpile(qc.reverse_bits(), self.sim), shots=shots)
        return job.result().get_counts()

    def plot(self, results: dict) -> str:
        buffer = io.BytesIO()

        fig: figure.Figure = plot_histogram(results)
        plt.savefig(fname=buffer, format="png")
        plt.close(fig)

        png_bytes = buffer.getvalue()
        buffer.close()

        return base64.b64encode(png_bytes).decode("utf-8")
