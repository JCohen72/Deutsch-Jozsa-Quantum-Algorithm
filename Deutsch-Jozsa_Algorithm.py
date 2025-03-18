# Import necessary modules
from qiskit import QuantumCircuit, IBMQ, transpile
from qiskit.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
from qiskit.ignis.mitigation.measurement import complete_meas_cal, CompleteMeasFitter
from qiskit_ibm_provider import IBMProvider
from qiskit import Aer
import matplotlib.pyplot as plt

# Configure IBM Quantum Experience account
IBMProvider.save_account('<IBMQ_API_KEY>', overwrite=True)
provider = IBMProvider()

# Function to create the constant 0 oracle
def constant_0_oracle(n):
    oracle = QuantumCircuit(n+1)
    return oracle.to_gate(label="Constant 0 Oracle")

# Function to create the parity oracle (balanced)
# VERSION 1
def parity_oracle(n):
    oracle = QuantumCircuit(n+1)
    for qubit in range(n):
        oracle.cx(qubit, n)
    return oracle.to_gate(label="Parity Oracle")

# VERSION 2
# def parity_oracle(n):
#     oracle = QuantumCircuit(n+1)
#     control_qubits = range((n + 1) // 2)
#     for qubit in control_qubits:
#         oracle.cx(qubit, n)
#     return oracle.to_gate(label="Parity Oracle")

# Function to create the Deutsch-Jozsa circuit
def deutsch_jozsa_circuit(n, oracle_gate):
    circuit = QuantumCircuit(n+1, n)
    circuit.x(n)
    circuit.h(range(n+1))
    circuit.append(oracle_gate(n), range(n+1))
    circuit.h(range(n))
    circuit.measure(range(n), range(n))
    return circuit

# Number of qubits
n = 4

# Create the circuits with print checks
dj_circuit_constant_0 = deutsch_jozsa_circuit(n, constant_0_oracle)
print("Deutsch-Jozsa Circuit with Constant 0 Oracle:")
print(dj_circuit_constant_0)

dj_circuit_parity = deutsch_jozsa_circuit(n, parity_oracle)
print("Deutsch-Jozsa Circuit with Parity Oracle:")
print(dj_circuit_parity)

# BACKEND OPTIONS
# IBMQ Manila - A newer quantum system with more qubits, suitable for more complex experiments
# backend = provider.get_backend('ibmq_manila')

# IBMQ Quito - A stable and widely used quantum system, good for general purposes
# backend = provider.get_backend('ibmq_quito')

# IBMQ Lima - A smaller quantum system, suitable for quicker access and shorter experiments
# backend = provider.get_backend('ibmq_lima')

# Simulator - A classical simulator that can mimic quantum computation, good for testing
backend = Aer.get_backend('aer_simulator')

# Check if the backend is a simulator
#is_simulator = backend.configuration().simulator

# Transpile the circuits for the backend
transpiled_constant_0 = transpile(dj_circuit_constant_0, backend)
print("Transpiled Constant 0 Circuit for Backend:")
print(transpiled_constant_0)

transpiled_parity = transpile(dj_circuit_parity, backend)
print("Transpiled Parity Balanced Circuit for Backend:")
print(transpiled_parity)

# Error mitigation: Calibration only for real devices
#if not is_simulator:
    # Calibration Circuits
    #cal_circuits, state_labels = complete_meas_cal(qr=transpiled_constant_0.qregs[0], circlabel='measerrormitigationcal')
    #cal_circuits = transpile(cal_circuits, backend=backend)
    #cal_job = backend.run(cal_circuits, shots=1024)
    #job_monitor(cal_job)
    #cal_results = cal_job.result()

    # Create a measurement fitter
    #meas_fitter = CompleteMeasFitter(cal_results, state_labels, circlabel='measerrormitigationcal')

# Execute the circuits
job_constant_0 = backend.run(transpiled_constant_0, shots=1024)
job_parity = backend.run(transpiled_parity, shots=1024)
job_monitor(job_constant_0)
job_monitor(job_parity)

# Retrieve results
result_constant_0 = job_constant_0.result()
result_parity = job_parity.result()

result_parity = job_parity.result()
counts_parity = result_parity.get_counts(transpiled_parity)

# Apply error mitigation filter if on a real device
#if not is_simulator:
    #result_constant_0 = meas_fitter.filter.apply(result_constant_0)
    #result_parity = meas_fitter.filter.apply(result_parity)

# Get counts
counts_constant_0 = result_constant_0.get_counts(transpiled_constant_0)
counts_parity = result_parity.get_counts(transpiled_parity)

# Graph setup
def complete_counts(n_qubits, actual_counts):
    # Generate all possible bitstrings from '000' to '111' (for 3 qubits)
    all_bitstrings = ['{:0{}b}'.format(i, n_qubits) for i in range(2**n_qubits)]
    # Initialize counts with zeros
    complete_counts = {bitstring: 0 for bitstring in all_bitstrings}
    # Update with the actual counts
    complete_counts.update(actual_counts)
    return complete_counts

complete_counts_constant_0 = complete_counts(n, counts_constant_0)
complete_counts_parity = complete_counts(n, counts_parity)

# Histogram plotting for the constant oracle
constant_0_histogram = plot_histogram(complete_counts_constant_0, legend=['Constant 0'], title='Constant 0 Oracle Results', figsize=(15, 8))
constant_0_histogram.savefig('constant_0_results.png')

# Histogram plotting for the balanced (parity) oracle
parity_histogram = plot_histogram(complete_counts_parity, legend=['Parity'], title='Parity Oracle Results', figsize=(15, 8))
parity_histogram.savefig('parity_results.png')