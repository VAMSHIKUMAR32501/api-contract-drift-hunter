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
| static_drift_detector.py      | Detects statically identifiable contract mismatches  |
| `request_generator.py`         | Generates valid requests from the contract           |
| `runtime_verifier.py`          | Verifies normal API runtime behavior                 |
| `negative_test_generator.py`   | Generates targeted invalid requests                  |
| `negative_runtime_verifier.py` | Executes negative requests and captures behavior     |
| `runtime_drift_detector.py`    | Converts runtime evidence into drift candidates      |
| `finding_normalizer.py`        | Deduplicates and prioritizes findings                |
| `pipeline.py`                  | Orchestrates the complete detection pipeline         |
| `evaluator.py`                 | Calculates benchmark evaluation metrics              |
| `run_regression.py            | Executes the complete 15-case regression suite       |

### Data Flow

The pipeline follows this general data flow:

OpenAPI
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
