# Case 11 — Agent Trajectory

## Overview

Case 11 demonstrates a request-validation drift where the OpenAPI contract requires `product_id` to be an integer, but the running implementation accepts a request in which the required field is missing.

The case is particularly useful because the final detection depends on negative runtime testing rather than static analysis alone.

---

## Input

### Contract

```text
benchmark/case11/openapi.yaml
````

### Implementation

```text
benchmark/case11/app.py
```

### Endpoint

```text
POST /cart/items
```

### Runtime

```text
http://127.0.0.1:5010
```

---

## Pipeline Trajectory

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
benchmark/case11/openapi.yaml
```

and extracts the endpoint:

```text
POST /cart/items
```

The request body contains:

```text
product_id
quantity
```

The contract specifies:

```text
product_id → integer
quantity   → integer
```

The required-field definition identifies `product_id` as required.

---

# Stage 2 — Source Analysis

The source analyzer examines:

```text
benchmark/case11/app.py
```

and identifies:

```text
POST /cart/items
```

The implementation reads the request body using expressions equivalent to:

```python
data.get("product_id")
data.get("quantity")
```

The analyzer records the request fields and their source expressions.

The extracted source information indicates that the fields are accessed from the JSON request body.

---

# Stage 3 — Static Drift Detection

The static detector compares the OpenAPI contract with the implementation.

For Case 11, the static stage does not produce the final required-field drift:

```text
Static drifts detected: 0
```

This is an important part of the trajectory because the actual violation is exposed through runtime behavior.

---

# Stage 4 — Request Generation

The request generator creates the normal request derived from the contract.

```text
Requests generated: 1
```

The generated valid request is used for normal runtime verification.

---

# Stage 5 — Runtime Verification

The normal request is sent to:

```text
http://127.0.0.1:5010/cart/items
```

The runtime verifier records the response and runtime behavior of the endpoint.

This establishes that the endpoint is reachable before negative testing is performed.

---

# Stage 6 — Negative Test Generation

The negative-test generator examines the request schema and generates targeted contract violations.

The generated negative test is:

```text
test_type:
required_field_violation

field:
product_id
```

The request body is:

```json
{
  "quantity": 1
}
```

The `product_id` field is deliberately removed.

The expected contract type for `product_id` is:

```text
integer
```

This creates a targeted request that violates the contract's required-field rule.

---

# Stage 7 — Negative Runtime Verification

The negative request is sent to:

```text
POST http://127.0.0.1:5010/cart/items
```

### Request

```json
{
  "quantity": 1
}
```

### Expected Behavior

Because `product_id` is required, the API should reject the request.

The expected validation response is:

```text
HTTP 400
```

### Actual Behavior

The implementation accepts the request and returns:

```text
HTTP 201
```

Runtime evidence:

```text
rejected: false
validation_enforced: false
```

This provides direct evidence that the implementation does not enforce the required-field rule.

---

# Stage 8 — Runtime Drift Detection

The runtime drift detector compares the negative-test expectation with the observed response.

```text
Expected:
400 / validation rejection

Actual:
201 / request accepted
```

The detector therefore creates a drift finding:

```text
issue_type:
missing_required_request_field

field:
product_id

expected:
required

actual:
missing
```

---

# Stage 9 — Merge Drift Evidence

Static and runtime findings are combined.

For Case 11:

```text
Static findings:
0

Runtime findings:
1

Combined findings:
1
```

The runtime finding becomes the primary evidence for the detected drift.

---

# Stage 10 — Finding Normalization

The finding normalizer converts the raw runtime evidence into the canonical drift representation.

Final normalized finding:

```json
{
  "endpoint": "/cart/items",
  "method": "POST",
  "issue_type": "missing_required_request_field",
  "field_or_parameter": "product_id",
  "expected": "required",
  "actual": "missing",
  "severity": "high"
}
```

Runtime evidence is preserved:

```json
{
  "test_type": "required_field_violation",
  "field": "product_id",
  "expected_status": 400,
  "actual_status": 201,
  "validation_enforced": false
}
```

---

# Stage 11 — Evaluator Format

The normalized finding is converted into the evaluator format:

```json
{
  "endpoint": "/cart/items",
  "issue_type": "missing_required_request_field",
  "field_or_parameter": "product_id",
  "expected": "required",
  "actual": "missing"
}
```

This provides a consistent structure for benchmark evaluation.

---

# Stage 12 — Evaluation

The evaluator compares the predicted finding against the expected benchmark finding.

The Case 11 finding is:

```text
Endpoint:
POST /cart/items

Issue:
missing_required_request_field

Field:
product_id

Expected:
required

Actual:
missing
```

The final benchmark evaluation confirms the finding as a true positive.

---

# Final Finding

```text
POST /cart/items

Missing required request field:
product_id

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
{"quantity": 1}

Expected status:
400

Actual status:
201

Validation enforced:
false
```

---

# Why Case 11 Matters

Case 11 demonstrates why contract-drift detection should not depend exclusively on static source analysis.

The implementation accesses the request field, but runtime testing reveals that the API accepts a request where the contract requires the field.

The important detection chain is:

```text
Contract Requirement
       +
Targeted Negative Test
       +
Runtime Acceptance
       ↓
Evidence-Based Drift
```

---

# Reproduction

Start the Case 11 Flask application:

```bash
python benchmark/case11/app.py
```

The application runs on:

```text
http://127.0.0.1:5010
```

In a second terminal:

```bash
python agents/pipeline.py case11 http://127.0.0.1:5010
```

The pipeline produces:

```text
STEP 1: CONTRACT EXTRACTION
STEP 2: SOURCE ANALYSIS
STEP 3: STATIC DRIFT DETECTION
STEP 4: REQUEST GENERATION
STEP 5: RUNTIME VERIFICATION
STEP 6: NEGATIVE TEST GENERATION
STEP 7: NEGATIVE RUNTIME VERIFICATION
STEP 8: RUNTIME DRIFT DETECTION
STEP 9: MERGE DRIFT EVIDENCE
STEP 10: FINDING NORMALIZATION
STEP 11: EVALUATOR FORMAT
STEP 12: EVALUATION
```

The final result is written to:

```text
results/case11_pipeline_results.json
```

---

# Engineering Lesson

Case 11 demonstrates that a contract-aware system should distinguish between:

```text
Field is accessed
```

and:

```text
Field requirement is actually enforced
```

Runtime negative testing provides the evidence needed to make that distinction.

---

# Representative Agent Workflow

```text
Contract Extractor
    ↓
Extract endpoint and schema

Source Analyzer
    ↓
Extract implementation behavior

Negative Test Generator
    ↓
Remove required product_id

Negative Runtime Verifier
    ↓
Observe HTTP 201

Runtime Drift Detector
    ↓
Compare expected 400 vs actual 201

Finding Normalizer
    ↓
Create canonical finding

Evaluator
    ↓
Compare with expected benchmark
```

This trajectory represents the actual deterministic execution flow of the Case 11 pipeline.




