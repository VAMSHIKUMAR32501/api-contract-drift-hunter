# Case 06 — Agent Trajectory

## Overview

Case 06 demonstrates detection of a missing required request field.

The OpenAPI contract requires the `email` field for the `POST /users` endpoint. The implementation accepts a request without `email` and returns HTTP `201`.

The final pipeline identifies this behavior as a contract drift.

---

## Input

### Contract

```text
benchmark/case06/openapi.yaml
````

### Implementation

```text
benchmark/case06/app.py
```

### Endpoint

```text
POST /users
```

### Runtime

```text
http://127.0.0.1:5005
```

---

## Pipeline Trajectory

The case passes through the following stages:

```text
OpenAPI Contract
       |
       v
Contract Extraction
       |
       v
Source Analysis
       |
       v
Static Drift Detection
       |
       v
Request Generation
       |
       v
Runtime Verification
       |
       v
Negative Test Generation
       |
       v
Negative Runtime Verification
       |
       v
Runtime Drift Detection
       |
       v
Finding Normalization
       |
       v
Evaluation
       |
       v
Final Finding
```

---

# Stage 1 — Contract Extraction

The contract extractor reads:

```text
benchmark/case06/openapi.yaml
```

and produces a structured representation of the API contract.

The endpoint identified is:

```text
POST /users
```

The request body contains:

```text
email
name
```

The contract marks `email` as required.

Expected contract behavior:

```text
email → required
email → string
name  → string
```

---

# Stage 2 — Source Analysis

The source analyzer examines:

```text
benchmark/case06/app.py
```

It identifies the Flask route:

```text
POST /users
```

and extracts the request-body fields used by the implementation.

The implementation accesses the request data and returns the received values.

This stage provides implementation evidence but does not by itself prove that runtime validation is enforced.

---

# Stage 3 — Static Drift Detection

The static drift detector compares the OpenAPI contract with the source implementation.

For Case 06:

```text
Static drifts detected: 0
```

No statically provable drift is reported at this stage.

This demonstrates why runtime testing is required in addition to static analysis.

---

# Stage 4 — Request Generation

The request generator creates a valid request based on the extracted contract.

The generated request is used for normal runtime verification.

```text
Requests generated: 1
```

---

# Stage 5 — Runtime Verification

The pipeline sends the generated request to:

```text
http://127.0.0.1:5005/users
```

The running Flask application responds successfully.

Runtime verification confirms that the endpoint is reachable and records the actual HTTP behavior.

---

# Stage 6 — Negative Test Generation

The negative-test generator creates targeted tests from the contract.

For Case 06, the important negative test is:

```text
Test type:
required_field_violation

Field:
email
```

The generated request body is:

```json
{
  "name": "test"
}
```

The `email` field is intentionally removed because the contract requires it.

This creates a controlled contract violation.

---

# Stage 7 — Negative Runtime Verification

The negative request is sent to the running API:

```text
POST http://127.0.0.1:5005/users
```

### Request

```json
{
  "name": "test"
}
```

### Actual Response

```text
HTTP 201
```

Response body:

```json
{
  "email": null,
  "name": "test"
}
```

Runtime evidence:

```text
rejected: false
validation_enforced: false
```

This is the critical evidence for Case 06.

The contract expects the request to be rejected because `email` is required, but the implementation accepts it.

---

# Stage 8 — Runtime Drift Detection

The runtime drift detector evaluates the negative-test result against the contract.

Observed:

```text
Expected:
400 / validation rejection

Actual:
201 / request accepted
```

Therefore:

```text
validation_enforced = false
```

The runtime evidence is converted into a drift candidate:

```text
issue_type:
missing_required_request_field

field:
email

expected:
required

actual:
missing
```

---

# Stage 9 — Finding Normalization

The runtime finding is passed to the finding normalizer.

The normalized finding becomes:

```json
{
  "endpoint": "/users",
  "method": "POST",
  "issue_type": "missing_required_request_field",
  "field_or_parameter": "email",
  "expected": "required",
  "actual": "missing",
  "severity": "high"
}
```

The runtime evidence is preserved:

```json
{
  "test_type": "required_field_violation",
  "field": "email",
  "expected_status": 400,
  "actual_status": 201,
  "validation_enforced": false
}
```

Normalization ensures that the final evaluator receives a canonical finding rather than multiple raw observations.

---

# Stage 10 — Evaluation

The normalized finding is converted into evaluator format:

```json
{
  "endpoint": "/users",
  "issue_type": "missing_required_request_field",
  "field_or_parameter": "email",
  "expected": "required",
  "actual": "missing"
}
```

The evaluator compares the predicted finding with the benchmark's expected finding.

The final Case 06 result is:

```text
Expected drifts : 1
Predicted issues: 1
True positives  : 1
False positives : 0
False negatives : 0

Precision : 1.000
Recall    : 1.000
F1        : 1.000
```

---

# Final Finding

```text
Endpoint:
POST /users

Issue:
Missing required request field

Field:
email

Expected:
required

Actual:
missing

Severity:
high
```

### Evidence

```text
Negative request:
{"name": "test"}

Expected behavior:
Reject request

Actual status:
201

Validation enforced:
false
```

---

# Why Case 06 Matters

Case 06 demonstrates an important limitation of static-only analysis.

The source code can reveal that `email` is accessed, but runtime execution demonstrates whether the implementation actually enforces the OpenAPI requirement.

The complete detection therefore depends on:

```text
Contract
   +
Source Analysis
   +
Negative Test
   +
Runtime Evidence
   =
Contract Drift
```

---

# Reproduction

Start the Case 06 Flask application:

```bash
python benchmark/case06/app.py
```

The application runs on:

```text
http://127.0.0.1:5005
```

In a second terminal:

```bash
python agents/pipeline.py case06 http://127.0.0.1:5005
```

The expected final evaluation is:

```text
Precision : 1.000
Recall    : 1.000
F1        : 1.000
```

---

# Key Engineering Lesson

The main lesson from Case 06 is:

> A contract violation is not proven merely because a source-code pattern looks suspicious. Targeted runtime evidence provides stronger proof of whether the implementation actually enforces the contract.


