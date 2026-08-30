# 🔍 API Contract Drift Hunter

An automated system for detecting **API contract drift** between an OpenAPI specification and its actual implementation.

API Contract Drift Hunter combines **OpenAPI contract extraction, source-code analysis, static drift detection, runtime verification, targeted negative testing, runtime drift detection, finding normalization, and automated evaluation** to identify inconsistencies between documented API behavior and actual implementation behavior.

## 🎯 Project Goal

The goal of this project is to automatically discover cases where an API implementation behaves differently from what its OpenAPI contract specifies.

The system is designed to detect both statically identifiable differences and runtime validation failures.

### Key Capabilities

- OpenAPI contract extraction
- Source-code route and request analysis
- Static contract drift detection
- Valid request generation
- Runtime API verification
- Targeted negative-test generation
- Runtime validation testing
- Required-field validation testing
- Request type validation testing
- Constraint validation testing
- Runtime drift detection
- Finding normalization and deduplication
- Automated precision, recall, and F1 evaluation
- 15-case benchmark regression testing
  
## 🚨 Problem

API contracts are used to describe how an API is expected to behave. However, as an application evolves, the implementation can change while the OpenAPI specification remains unchanged.

This creates **API contract drift**.

For example, an OpenAPI contract may define a request field as:

yaml
quantity:
  type: integer

## 💡 Solution

API Contract Drift Hunter solves the problem by combining **static source-code analysis** with **runtime verification**.

Instead of relying only on source-code inspection, the system actively generates requests based on the OpenAPI contract and executes them against the running API.

The solution follows a multi-stage pipeline:

1. **Extract the OpenAPI contract**
   - Parse endpoints, methods, request bodies, properties, types, required fields, constraints, and responses.

2. **Analyze the implementation**
   - Inspect application source code to identify routes, request fields, response fields, and status codes.

3. **Detect static drift**
   - Compare contract information with information that can be determined from the source code.

4. **Generate valid requests**
   - Create contract-compliant requests for normal runtime verification.

5. **Verify runtime behavior**
   - Send valid requests to the running API and capture the actual response.

6. **Generate targeted negative tests**
   - Create intentionally invalid requests from the contract, including type, constraint, nullability, enum, and required-field violations.

7. **Verify negative behavior**
   - Execute the negative requests against the API and determine whether the implementation correctly rejects invalid input.

8. **Detect runtime drift**
   - Convert unexpected runtime behavior into structured drift findings.

9. **Merge evidence**
   - Combine static and runtime findings.

10. **Normalize findings**
    - Remove duplicate and secondary observations while preserving meaningful independent drift.

11. **Evaluate the result**
    - Compare predicted findings with the benchmark's expected findings.

12. **Generate the final report**
    - Produce structured drift findings and evaluation metrics.

### Core Design Principle

The key design principle is:

> **Generate broad evidence, then normalize it into precise findings.**

Negative testing should not be unnecessarily disabled just because one benchmark case produces multiple observations. Instead, the system preserves useful test coverage and uses finding normalization to determine which observations represent meaningful independent contract drift.

This separation between **test generation** and **finding interpretation** improves both coverage and precision.


## 🏗️ Architecture

The system is organized as a sequential pipeline where each stage produces structured information for the next stage.


                         ┌──────────────────────┐
                         │   OpenAPI Contract   │
                         │     openapi.yaml     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Contract Extraction  │
                         │ contract_extractor   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Source Analysis    │
                         │   source_analyzer    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Static Drift         │
                         │ Detection            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Request Generation   │
                         │ request_generator    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Runtime Verification │
                         │ runtime_verifier     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Negative Test        │
                         │ Generation            │
                         │ negative_test_       │
                         │ generator             │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Negative Runtime     │
                         │ Verification         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Runtime Drift        │
                         │ Detection            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Merge Drift Evidence │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Finding Normalizer   │
                         │ finding_normalizer   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Evaluator       │
                         │      evaluator       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Final Drift Report │
                         └──────────────────────┘


### Main Components

| Component                      | Responsibility                                       |
| ------------------------------ | ---------------------------------------------------- |
| `contract_extractor.py`        | Extracts API information from OpenAPI specifications |
| `source_analyzer.py`           | Analyzes implementation source code                  |
| `static_drift_detector.py`     | Detects statically identifiable contract mismatches  |
| `request_generator.py`         | Generates valid requests from the contract           |
| `runtime_verifier.py`          | Verifies normal API runtime behavior                 |
| `negative_test_generator.py`   | Generates targeted invalid requests                  |
| `negative_runtime_verifier.py` | Executes negative requests and captures behavior     |
| `runtime_drift_detector.py`    | Converts runtime evidence into drift candidates      |
| `finding_normalizer.py`        | Deduplicates and prioritizes findings                |
| `pipeline.py`                  | Orchestrates the complete detection pipeline         |
| `evaluator.py`                 | Calculates benchmark evaluation metrics              |
| `run_regression.py`            | Executes the complete 15-case regression suite       |

### Data Flow

The pipeline follows this general data flow:
```
OpenAPI Contract
       │
       ▼
Structured Contract
       │
       ├──────────────► Static Analysis
       │                     │
       │                     ▼
       │               Static Findings
       │
       ▼
Generated Requests
       │
       ▼
Running API
       │
       ▼
Runtime Evidence
       │
       ▼
Runtime Findings
       │
       └──────────────┐
                      ▼
               Evidence Merge
                      │
                      ▼
                Normalization
                      │
                      ▼
                  Evaluation
                      │
                      ▼
              Final Drift Report
```
## 🔄 Pipeline Stages

The complete API Contract Drift Hunter pipeline consists of 12 stages.

### Step 1 — Contract Extraction

The system reads the OpenAPI specification and converts the API contract into a structured representation.

The extracted information includes:

- API endpoints
- HTTP methods
- Request bodies
- Request properties
- Data types
- Required fields
- Numeric and string constraints
- Enum values
- Nullability
- Response schemas
- Expected response status codes

The structured contract becomes the source of truth for subsequent analysis.

---

### Step 2 — Source Analysis

The implementation source code is analyzed to identify how the API actually behaves.

The source analyzer extracts information such as:

- Flask routes
- HTTP methods
- Request parameters
- JSON request-body fields
- Request field access patterns
- Response fields
- Response status codes
- Runtime values where statically identifiable

This provides implementation-side evidence that can be compared with the OpenAPI contract.

---

### Step 3 — Static Drift Detection

The extracted contract and source-code information are compared to detect mismatches that can be identified without executing the application.

Examples include:

- Contract endpoint missing from implementation
- HTTP method mismatch
- Request field mismatch
- Response field mismatch
- Response status mismatch
- Detectable type inconsistencies

Static analysis provides an early layer of drift detection before runtime testing.

---

### Step 4 — Request Generation

The system generates valid requests from the OpenAPI contract.

For each endpoint, the request generator creates suitable values based on the documented schema.

For example:

json
{
  "product_id": 1,
  "quantity": 1
}

## 🧪 Negative Testing

Negative testing is a core part of API Contract Drift Hunter.

A contract can look correct during normal API execution while the implementation still fails to enforce important validation rules. Therefore, the system intentionally generates invalid requests from the OpenAPI specification and observes how the API responds.

### Why Negative Testing?

Consider a contract that defines:

yaml
quantity:
  type: integer
  minimum: 1

## 🔎 Runtime Drift Detection

Runtime drift detection is responsible for converting actual API behavior into structured contract-drift findings.

While static analysis examines the implementation source code, runtime detection verifies what the API actually does when requests are executed.

### Runtime Detection Flow
```
Contract
   │
   ▼
Negative Test
Generation
   │
   ▼
Negative Runtime
Verification
   │
   ▼
Runtime Evidence
   │
   ▼
Runtime Drift
Detection
   │
   ▼
Drift Candidates
```
## 🧹 Finding Normalization

Finding normalization is the stage that converts raw drift candidates into a smaller set of precise, meaningful findings.

Runtime negative testing can generate multiple observations from the same request body or endpoint. Reporting every observation independently can introduce false positives and reduce precision.

The normalizer therefore acts as a final evidence-filtering layer before evaluation.

### Normalization Flow

```
Static Findings
      │
      │
Runtime Findings
      │
      ▼
┌──────────────────────┐
│   Evidence Merge     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Finding Normalizer   │
│                      │
│ • Deduplication      │
│ • Canonical Keys     │
│ • Evidence Ranking   │
│ • Priority Rules     │
└──────────┬───────────┘
           │
           ▼
   Normalized Findings
           │
           ▼
       Evaluator
```
## 📊 Evaluation

The project includes an automated evaluator that compares the drift findings produced by API Contract Drift Hunter with the expected findings defined by the benchmark.

The evaluation focuses on three standard metrics:

- **Precision**
- **Recall**
- **F1 Score**

### Evaluation Metrics

#### Precision

Precision measures how many of the predicted findings are actually correct.

Precision = True Positives / (True Positives + False Positives)

## 📁 Project Structure

The repository is organized into separate modules for contract processing, source analysis, runtime verification, drift detection, evaluation, benchmarking, and regression testing.

```text
api-contract-drift-hunter/
│
├── agents/
│   ├── contract_extractor.py
│   ├── source_analyzer.py
│   ├── static_drift_detector.py
│   ├── request_generator.py
│   ├── runtime_verifier.py
│   ├── negative_test_generator.py
│   ├── negative_runtime_verifier.py
│   ├── runtime_drift_detector.py
│   ├── finding_normalizer.py
│   └── pipeline.py
│
├── baseline/
│   ├── baseline.py
│   └── run_baseline.py
│
├── benchmark/
│   ├── case01/
│   ├── case02/
│   ├── case03/
│   ├── case04/
│   ├── case05/
│   ├── case06/
│   ├── case07/
│   ├── case08/
│   ├── case09/
│   ├── case10/
│   ├── case11/
│   ├── case12/
│   ├── case13/
│   ├── case14/
│   └── case15/
│
├── evaluator/
│   └── evaluator.py
│
├── tests/
│
├── results/
│   ├── case01_pipeline_results.json
│   ├── ...
│   ├── case15_pipeline_results.json
│   └── regression_summary.json
│
├── .gitignore
├── README.md
├── requirements.txt
└── run_regression.py

```
## 🛠️ Technologies

API Contract Drift Hunter is implemented primarily in Python and uses lightweight tools and libraries for contract parsing, source analysis, HTTP runtime verification, and automated evaluation.

### Core Technologies

| Technology | Usage |
|---|---|
| **Python 3** | Main programming language |
| **OpenAPI 3.0** | API contract specification |
| **YAML** | OpenAPI contract format |
| **JSON** | Structured test results, findings, and evaluation output |
| **Flask** | Benchmark API implementations |
| **Requests / HTTP** | Runtime API verification |
| **Python AST / Source Analysis** | Static implementation analysis |
| **PyYAML** | Parsing OpenAPI YAML files |
| **Git / GitHub** | Version control and project submission |

### Python

Python is used throughout the project for:

- Contract extraction
- Source-code analysis
- Test generation
- Runtime verification
- Drift detection
- Finding normalization
- Evaluation
- Regression testing

### OpenAPI

OpenAPI 3.0 specifications provide the expected API contract.

The system extracts information such as:

```text
Endpoints
Methods
Request Bodies
Properties
Types
Required Fields
Constraints
Enums
Nullability
Responses
Status Codes
```
## 📦 Installation
Follow the steps below to set up API Contract Drift Hunter locally.

### Prerequisites

Make sure the following are installed:

- Python 3.x
- pip
- Git
- Flask

You can verify Python and pip with:

```bash
python --version
pip --version
````

### 1. Clone the Repository

Clone the GitHub repository:

```bash
git clone https://github.com/VAMSHIKUMAR32501/api-contract-drift-hunter.git
```

Move into the project directory:

```bash
cd api-contract-drift-hunter
```

### 2. Create a Virtual Environment

Creating a virtual environment is recommended to keep project dependencies isolated.

On Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is empty or dependencies are not listed yet, install the packages required by the current implementation manually and then update `requirements.txt`.

### 4. Verify the Installation

Run a Python compilation check:

```bash
python -m py_compile agents/*.py
```

You can also verify the regression runner is available:

```bash
python run_regression.py
```

### 5. Repository Structure

After installation, the project should contain:

```text
api-contract-drift-hunter/
├── agents/
├── baseline/
├── benchmark/
├── evaluator/
├── results/
├── tests/
├── README.md
├── requirements.txt
└── run_regression.py
```

### Environment Notes

The benchmark applications are local Flask applications.

Each benchmark case uses a different local port:

```text
case01 → 5000
case02 → 5001
case03 → 5002
case04 → 5003
case05 → 5004
case06 → 5005
case07 → 5006
case08 → 5007
case09 → 5008
case10 → 5009
case11 → 5010
case12 → 5011
case13 → 5012
case14 → 5013
case15 → 5014
```

The pipeline accepts the case ID and base URL as command-line arguments, allowing individual cases to be executed against their corresponding local application.

## ▶️ Running a Single Case

Paste this section next:

````markdown
## ▶️ Running a Single Case

API Contract Drift Hunter can be executed against an individual benchmark case.

Each benchmark case contains:

```text
openapi.yaml   → API contract
app.py         → API implementation
expected.json  → Expected benchmark result
````

### 1. Start the Benchmark API

Open a terminal and start the Flask application for the case you want to test.

For example, Case 06:

```bash
python benchmark/case06/app.py
```

The application starts on:

```text
http://127.0.0.1:5005
```

Keep this terminal running.

### 2. Run the Pipeline

Open a second terminal in the project root and run:

```bash
python agents/pipeline.py case06 http://127.0.0.1:5005
```

The pipeline executes all detection stages and prints the results to the terminal.

### 3. Example Pipeline Output

A successful case produces output similar to:

```text
============================================================
STEP 1: CONTRACT EXTRACTION
============================================================
Endpoints extracted: 1

============================================================
STEP 2: SOURCE ANALYSIS
============================================================
Routes analyzed: 1

============================================================
STEP 3: STATIC DRIFT DETECTION
============================================================
Static drifts detected: 0

============================================================
STEP 4: REQUEST GENERATION
============================================================
Requests generated: 1

============================================================
STEP 5: RUNTIME VERIFICATION
============================================================
Runtime results: 1

============================================================
STEP 6: NEGATIVE TEST GENERATION
============================================================
Negative tests generated: ...

============================================================
STEP 7: NEGATIVE RUNTIME VERIFICATION
============================================================
Negative runtime results: ...

============================================================
STEP 8: RUNTIME DRIFT DETECTION
============================================================
Runtime drifts detected: ...

============================================================
STEP 9: MERGE DRIFT EVIDENCE
============================================================
Combined drifts: ...

============================================================
STEP 10: FINDING NORMALIZATION
============================================================
Normalized drifts: ...

============================================================
STEP 11: EVALUATOR FORMAT
============================================================
Evaluator issues: ...

============================================================
STEP 12: EVALUATION
============================================================
```

### 4. Run Other Cases

Use the corresponding case ID and application port.

For example:

```bash
python benchmark/case11/app.py
```

Then, from another terminal:

```bash
python agents/pipeline.py case11 http://127.0.0.1:5010
```

Similarly:

```bash
python agents/pipeline.py case01 http://127.0.0.1:5000
python agents/pipeline.py case02 http://127.0.0.1:5001
python agents/pipeline.py case03 http://127.0.0.1:5002
...
python agents/pipeline.py case15 http://127.0.0.1:5014
```

### 5. Results

After execution, the pipeline saves the complete result under:

```text
results/
```

For example:

```text
results/case06_pipeline_results.json
```

The result contains:

```text
Contract information
Source analysis
Runtime results
Negative runtime results
Raw drift findings
Normalized findings
Evaluation results
Final drift report
```

### ⚠️ Runtime Requirement

For cases that require runtime verification, the corresponding Flask application must be running before executing the pipeline.

If the API is not running, runtime verification cannot connect to the application and the runtime stages may not produce valid drift evidence.

### Stopping the API

After testing a case, return to the terminal running Flask and press:

```text
CTRL + C
```
## 🔌 Benchmark Ports

Each benchmark case contains a local Flask application running on a dedicated port.

This allows multiple benchmark applications to be tested independently without port conflicts.

| Case | Application | Port | Base URL |
|---|---|---:|---|
| `case01` | `benchmark/case01/app.py` | 5000 | `http://127.0.0.1:5000` |
| `case02` | `benchmark/case02/app.py` | 5001 | `http://127.0.0.1:5001` |
| `case03` | `benchmark/case03/app.py` | 5002 | `http://127.0.0.1:5002` |
| `case04` | `benchmark/case04/app.py` | 5003 | `http://127.0.0.1:5003` |
| `case05` | `benchmark/case05/app.py` | 5004 | `http://127.0.0.1:5004` |
| `case06` | `benchmark/case06/app.py` | 5005 | `http://127.0.0.1:5005` |
| `case07` | `benchmark/case07/app.py` | 5006 | `http://127.0.0.1:5006` |
| `case08` | `benchmark/case08/app.py` | 5007 | `http://127.0.0.1:5007` |
| `case09` | `benchmark/case09/app.py` | 5008 | `http://127.0.0.1:5008` |
| `case10` | `benchmark/case10/app.py` | 5009 | `http://127.0.0.1:5009` |
| `case11` | `benchmark/case11/app.py` | 5010 | `http://127.0.0.1:5010` |
| `case12` | `benchmark/case12/app.py` | 5011 | `http://127.0.0.1:5011` |
| `case13` | `benchmark/case13/app.py` | 5012 | `http://127.0.0.1:5012` |
| `case14` | `benchmark/case14/app.py` | 5013 | `http://127.0.0.1:5013` |
| `case15` | `benchmark/case15/app.py` | 5014 | `http://127.0.0.1:5014` |

### Example: Case 06

Start the Case 06 application:

```bash
python benchmark/case06/app.py
````

The application runs at:

```text
http://127.0.0.1:5005
```

Then open another terminal and run:

```bash
python agents/pipeline.py case06 http://127.0.0.1:5005
```

### Example: Case 11

Start the Case 11 application:

```bash
python benchmark/case11/app.py
```

The application runs at:

```text
http://127.0.0.1:5010
```

Then run:

```bash
python agents/pipeline.py case11 http://127.0.0.1:5010
```

### Port Mapping Rule

The benchmark follows a sequential port assignment:

```text
case01 → 5000
case02 → 5001
...
case15 → 5014
```

The pipeline accepts the base URL as an optional command-line argument:

```text
python agents/pipeline.py <case_id> <base_url>
```

Example:

```bash
python agents/pipeline.py case06 http://127.0.0.1:5005
```

### Important

Only start the benchmark server for the case being tested.

If the application is not running, runtime verification will not be able to connect to the endpoint. This can result in connection errors and prevent runtime-based drift detection from producing valid evidence.



