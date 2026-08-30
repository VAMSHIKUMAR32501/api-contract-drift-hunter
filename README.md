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

```yaml
quantity:
  type: integer
````

but the actual implementation may accept:

```json
{
  "quantity": "2"
}
```

The API may still return a successful response even though the request violates the documented contract.

### Types of Drift

This project targets several types of API contract inconsistencies:

* **Request type mismatch** — an API accepts a value with an incorrect type.
* **Missing required-field validation** — an API accepts a request even when a required field is missing.
* **Constraint violation** — an API accepts values outside documented limits.
* **Enum violation** — an API accepts values outside the documented enum.
* **Nullability mismatch** — an API accepts or rejects `null` differently from the contract.
* **Response mismatch** — the actual response does not match the documented response schema.
* **Status-code mismatch** — the implementation returns a different status code from the documented behavior.
* **Undocumented behavior** — the implementation exposes behavior that is not represented in the contract.

### Why This Matters

Contract drift can cause:

* Client integration failures
* Unexpected runtime behavior
* Incorrect API documentation
* Production defects
* Difficult debugging
* Compatibility issues between API consumers and providers

The challenge is therefore to automatically compare the **documented contract** with the **actual implementation behavior** and identify meaningful drift.

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
```


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
```

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

```json
{
  "product_id": 1,
  "quantity": 1
}
````

These requests are used to verify that normal contract-compliant API calls behave as expected.

---

### Step 5 — Runtime Verification

Generated valid requests are sent to the running API.

The runtime verifier records information such as:

* Request URL
* HTTP method
* Request body
* Response status code
* Response body
* Response time
* Runtime errors

This provides direct evidence of actual API behavior.

---

### Step 6 — Negative Test Generation

The system generates targeted invalid requests from the OpenAPI contract.

Negative tests are designed to verify whether the implementation enforces the documented validation rules.

Supported negative-test categories include:

* Type violations
* Minimum violations
* Maximum violations
* Minimum-length violations
* Maximum-length violations
* Minimum-items violations
* Maximum-items violations
* Enum violations
* Nullability violations
* Missing required fields

Example:

Contract:

```yaml
quantity:
  type: integer
  minimum: 1
```

Generated negative tests can include:

```json
{
  "quantity": "2"
}
```

and:

```json
{
  "quantity": 0
}
```

---

### Step 7 — Negative Runtime Verification

The generated invalid requests are executed against the running API.

The system determines whether the implementation correctly rejects invalid requests.

For each test, the verifier records:

* Request body
* Test type
* Field under test
* HTTP status code
* Response body
* Whether the request was rejected
* Whether validation was enforced
* Runtime errors

An invalid request that is accepted by the API becomes evidence for possible contract drift.

---

### Step 8 — Runtime Drift Detection

Runtime evidence is converted into structured drift candidates.

For example, if the contract states:

```yaml
email:
  type: string
```

but the API accepts:

```json
{
  "email": 123
}
```

the runtime detector can produce a finding such as:

```json
{
  "issue_type": "request_body_type_mismatch",
  "field_or_parameter": "email",
  "expected": "string",
  "actual": "integer"
}
```

Required-field violations are also detected when a field documented as required is omitted but the API still accepts the request.

---

### Step 9 — Merge Drift Evidence

Static and runtime findings are combined into a single collection of drift candidates.

This allows the system to use multiple sources of evidence rather than relying on only one detection mechanism.

```text
Static Findings
       │
       ├──────────────┐
       │              │
       ▼              ▼
              Evidence Merge
                     ▲
       │              │
       └──────────────┘
Runtime Findings
```

---

### Step 10 — Finding Normalization

Raw runtime testing can produce multiple observations for the same underlying contract problem.

The finding normalizer removes duplicate findings and prioritizes the strongest evidence.

The normalization stage performs tasks such as:

* Removing duplicate findings
* Creating canonical finding keys
* Selecting the strongest type finding for a field
* Preventing duplicate required-field findings
* Prioritizing required-field violations over secondary type observations
* Preserving independent drift findings

This stage is important for maintaining high precision.

The goal is not simply to report every failed negative test. The goal is to report the meaningful contract drift represented by the collected evidence.

---

### Step 11 — Evaluator Format

The normalized findings are converted into the format expected by the benchmark evaluator.

A finding is represented using fields such as:

```json
{
  "endpoint": "/users",
  "issue_type": "missing_required_request_field",
  "field_or_parameter": "email",
  "expected": "required",
  "actual": "missing"
}
```

The evaluator then compares the predicted issues with the benchmark's expected drift.

---

### Step 12 — Evaluation

The final predictions are evaluated using:

* Precision
* Recall
* F1 score
* True positives
* False positives
* False negatives

The project also provides a 15-case regression runner to ensure that improvements to one benchmark case do not break previously passing cases.

The final target is:

```text
15 / 15 cases passed

Precision : 1.000
Recall    : 1.000
F1        : 1.000
```

This regression process was used throughout development to validate changes to negative-test generation, runtime drift detection, and finding normalization.
## 🧪 Negative Testing
Negative testing is a core part of API Contract Drift Hunter.

A contract can look correct during normal API execution while the implementation still fails to enforce important validation rules. Therefore, the system intentionally generates invalid requests from the OpenAPI specification and observes how the API responds.

### Why Negative Testing?

Consider a contract that defines:

```yaml
quantity:
  type: integer
  minimum: 1
````

A normal request such as:

```json
{
  "quantity": 2
}
```

may succeed even when the implementation has no validation.

To detect the drift, the system also tests invalid values such as:

```json
{
  "quantity": "2"
}
```

and:

```json
{
  "quantity": 0
}
```

If the implementation accepts these requests instead of rejecting them, the runtime behavior provides evidence of contract drift.

---

### Negative Test Categories

The negative test generator supports the following categories:

| Test Type                  | Purpose                                                 |
| -------------------------- | ------------------------------------------------------- |
| `type_violation`           | Tests whether an incorrect data type is rejected        |
| `minimum_violation`        | Tests values below the documented minimum               |
| `maximum_violation`        | Tests values above the documented maximum               |
| `minLength_violation`      | Tests strings shorter than the documented minimum       |
| `maxLength_violation`      | Tests strings longer than the documented maximum        |
| `minItems_violation`       | Tests arrays with fewer items than allowed              |
| `maxItems_violation`       | Tests arrays with more items than allowed               |
| `enum_violation`           | Tests values outside the documented enum                |
| `nullability_violation`    | Tests whether invalid `null` values are accepted        |
| `required_field_violation` | Tests whether documented required fields can be omitted |

---

### Required-Field Testing

For every request body containing required fields, the generator creates a request where a required field is omitted.

For example:

```yaml
required:
  - product_id
  - quantity
```

The generator can produce:

```json
{
  "quantity": 1
}
```

If the API accepts the request with a successful status code instead of rejecting it, the runtime detector can identify:

```json
{
  "issue_type": "missing_required_request_field",
  "field_or_parameter": "product_id",
  "expected": "required",
  "actual": "missing"
}
```

---

### Property-Level Testing

The generator also creates invalid values for individual request properties.

For example:

```yaml
product_id:
  type: integer

quantity:
  type: integer
  minimum: 1
```

The generator can create tests such as:

```json
{
  "product_id": "2",
  "quantity": 1
}
```

and:

```json
{
  "product_id": 1,
  "quantity": "2"
}
```

and:

```json
{
  "product_id": 1,
  "quantity": 0
}
```

Each test isolates a specific contract rule.

---

### Separating Test Generation from Finding Detection

An important design decision in this project is that **generating a negative test does not automatically mean that a drift should be reported**.

The system separates:

```text
Negative Test Generation
          │
          ▼
Runtime Execution
          │
          ▼
Runtime Evidence
          │
          ▼
Drift Detection
          │
          ▼
Finding Normalization
          │
          ▼
Final Finding
```

This prevents the final report from treating every generated test as an independent API defect.

---

### Case 06: Required Field vs Type Violation

During development, Case 06 exposed an important precision problem.

The API accepted both:

1. A request with a required field missing.
2. A request containing an incorrect type.

For example, the runtime could observe:

```text
Missing email
    → API returned 201
    → Required-field validation not enforced
```

and:

```text
email = 123
    → API returned 201
    → Type validation not enforced
```

Both observations are technically valid runtime observations, but the benchmark expects the primary required-field drift.

The solution was to keep the negative tests available while using the **finding normalization stage** to avoid reporting secondary observations as independent findings when they represent the same underlying benchmark behavior.

This allowed the final result for Case 06 to remain precise without disabling negative testing globally.

---

### Cases 11–14: Preserving Property-Level Coverage

Another important development challenge was avoiding an overly aggressive rule such as:

```python
if required_fields:
    skip_property_tests()
```

That approach could make Case 06 pass but would prevent property-level tests from being generated for cases where required fields and property constraints coexist.

The final approach keeps property-level testing available while controlling the final findings through runtime evidence and normalization.

This preserves broader test coverage while preventing unnecessary false-positive findings.

---

### Design Principle

The negative testing strategy follows a simple principle:

> **Generate enough invalid tests to expose contract violations, but report only evidence-backed, meaningful drift.**

This separation improves the balance between:

* **Recall** — finding real contract drift
* **Precision** — avoiding unnecessary findings
* **Regression safety** — preventing fixes for one case from breaking other cases
## 🔎 Runtime Drift Detection

Runtime drift detection is responsible for converting actual API behavior into structured contract-drift findings.

While static analysis examines the implementation source code, runtime detection verifies what the API actually does when requests are executed.

### Runtime Detection Flow

```text
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
````

### Runtime Evidence

For every executed negative test, the system captures information such as:

* HTTP method
* Endpoint
* Request URL
* Test type
* Field being tested
* Request body
* HTTP status code
* Response body
* Response time
* Whether the request was rejected
* Whether validation was enforced
* Runtime errors

Example runtime evidence:

```json
{
  "method": "POST",
  "endpoint": "/users",
  "test_type": "type_violation",
  "field": "email",
  "request_body": {
    "name": "test",
    "email": 123
  },
  "status_code": 201,
  "validation_enforced": false
}
```

This evidence is then passed to the runtime drift detector.

---

### Validation Behavior

The runtime detector first checks whether validation was successfully enforced.

If the API correctly rejects an invalid request, the test does not produce a drift finding.

```text
Invalid Request
      │
      ▼
API rejects request
      │
      ▼
Validation enforced
      │
      ▼
No Drift
```

If the API accepts an invalid request, the behavior becomes a candidate for contract drift.

```text
Invalid Request
      │
      ▼
API accepts request
      │
      ▼
Validation not enforced
      │
      ▼
Drift Candidate
```

---

### Type Mismatch Detection

For type violations, the detector compares the contract's expected type with the actual value accepted by the implementation.

Example contract:

```yaml
email:
  type: string
```

Negative request:

```json
{
  "email": 123
}
```

If the API accepts the request and preserves the integer value, the detector can create:

```json
{
  "issue_type": "request_body_type_mismatch",
  "field_or_parameter": "email",
  "expected": "string",
  "actual": "integer"
}
```

The finding also retains runtime evidence so that the result can be traced back to the executed test.

---

### Required-Field Drift Detection

Required-field validation is handled separately.

Suppose the contract states:

```yaml
required:
  - email
```

The negative test removes `email` from the request.

If the API returns a successful response instead of rejecting the request, the detector creates:

```json
{
  "issue_type": "missing_required_request_field",
  "field_or_parameter": "email",
  "expected": "required",
  "actual": "missing"
}
```

This provides direct runtime evidence that the implementation does not enforce the documented requirement.

---

### Constraint Drift Detection

The runtime detector also handles contract constraints such as:

* `minimum`
* `maximum`
* `minLength`
* `maxLength`
* `minItems`
* `maxItems`
* `enum`

For example:

```yaml
quantity:
  type: integer
  minimum: 1
```

The generated request may contain:

```json
{
  "quantity": 0
}
```

If the implementation accepts the value, the runtime result can be converted into a constraint-drift finding.

---

### Nullability Drift Detection

The same approach is used for nullability.

If a property is documented as non-nullable, the negative test generator can send:

```json
{
  "quantity": null
}
```

If the API accepts the value when the contract does not permit `null`, the runtime detector can identify a nullability mismatch.

---

### Evidence-Based Findings

Runtime drift detection does not assume that generating an invalid request automatically means a drift exists.

The finding is created only after examining the actual runtime result.

The general decision process is:

```text
                Negative Test
                     │
                     ▼
              Execute Request
                     │
                     ▼
             Capture Response
                     │
             ┌───────┴───────┐
             │               │
             ▼               ▼
          Rejected         Accepted
             │               │
             ▼               ▼
      Validation OK     Compare with
                         Contract
                             │
                             ▼
                       Drift Candidate
```

This makes runtime findings evidence-based rather than assumption-based.

---

### Runtime vs Static Detection

The project uses both static and runtime techniques because they provide different types of evidence.

| Detection Method         | Strength                                                  |
| ------------------------ | --------------------------------------------------------- |
| Static analysis          | Detects mismatches visible from source code               |
| Runtime verification     | Observes actual API behavior                              |
| Negative runtime testing | Tests validation rules that may not be visible statically |
| Finding normalization    | Converts multiple observations into precise findings      |

The combination provides stronger coverage than relying on either static analysis or runtime testing alone.

---

### Runtime Drift Output

Runtime drift candidates are structured before being passed to the merge and normalization stages.

A typical finding contains:

```json
{
  "endpoint": "/users",
  "method": "POST",
  "issue_type": "request_body_type_mismatch",
  "field_or_parameter": "email",
  "expected": "string",
  "actual": "integer",
  "severity": "medium",
  "evidence": {
    "test_type": "type_violation",
    "status_code": 201,
    "validation_enforced": false
  }
}
```

The evidence makes the finding explainable and allows the final report to show why the system considers the behavior to be contract drift.

## 🧹 Finding Normalization

Finding normalization is the stage that converts raw drift candidates into a smaller set of precise, meaningful findings.

Runtime negative testing can generate multiple observations from the same request body or endpoint. Reporting every observation independently can introduce false positives and reduce precision.

The normalizer therefore acts as a final evidence-filtering layer before evaluation.

### Normalization Flow

```text
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
````

### Why Normalization Is Required

A single API endpoint can produce several runtime observations.

For example, an endpoint may accept:

```json
{
  "name": 123,
  "email": 123
}
```

and may also accept a request where:

```json
{
  "name": "test"
}
```

is missing a required `email` field.

These are multiple observations, but the benchmark may define only one expected drift.

Without normalization, all observations could be reported independently:

```text
Finding 1 → Missing required email
Finding 2 → Invalid email type
Finding 3 → Invalid name type
```

This can increase the number of predicted issues and create false positives.

---

### Canonical Deduplication

The normalizer first removes duplicate findings.

Each finding is converted into a canonical identity based on information such as:

* Endpoint
* HTTP method
* Field or parameter
* Issue type
* Expected value
* Actual value

Conceptually:

```text
Finding
   │
   ▼
Canonical Key
   │
   ▼
Already seen?
   │
 ┌─┴─────────┐
 │           │
Yes          No
 │           │
 ▼           ▼
Skip       Keep
```

This prevents identical evidence from appearing multiple times in the final report.

---

### Strong Type Evidence

When multiple type-mismatch observations exist for the same endpoint and field, the normalizer selects the strongest available runtime evidence.

Type findings are grouped using:

```text
Endpoint + Method + Field
```

The strongest finding is retained rather than reporting multiple observations for the same field.

This keeps the final output concise while preserving the most useful evidence.

---

### Required-Field Priority

Required-field findings receive special handling.

If an API accepts a request where a documented required field is completely missing, the normalizer treats that observation as more meaningful than a secondary type observation for the same field.

For example:

```text
Contract:
email → required + string
```

Runtime observations:

```text
1. email is missing → API accepts request
2. email is integer → API accepts request
```

The normalized result can prioritize:

```json
{
  "issue_type": "missing_required_request_field",
  "field_or_parameter": "email",
  "expected": "required",
  "actual": "missing"
}
```

The reason is that a missing field has no runtime value whose type can meaningfully be checked.

---

### Important Design Decision

During development, a major challenge was finding the correct balance between negative-test coverage and final finding precision.

An early approach was to disable property-level negative tests whenever required fields existed:

```python
if required_fields:
    skip_property_tests()
```

This could make some cases pass, but it also removed useful type and constraint tests from other benchmark cases.

The final design does **not** use this global shortcut.

Instead:

```text
Generate Negative Tests
          │
          ▼
Execute All Relevant Tests
          │
          ▼
Collect Runtime Evidence
          │
          ▼
Normalize Findings
```

This preserves test coverage while allowing the final finding set to remain precise.

---

### Case 06 Improvement

Case 06 was particularly useful during development.

Initially, the system produced three findings:

```text
1. missing_required_request_field → email
2. request_body_type_mismatch     → email
3. request_body_type_mismatch     → name
```

The benchmark expected one drift.

The initial evaluation was:

```text
Expected drifts : 1
Predicted       : 3
True positives  : 1
False positives : 2

Precision : 0.333
Recall    : 1.000
F1        : 0.500
```

After improving the negative-test generation and normalization behavior, Case 06 produced only the expected finding:

```text
Expected drifts : 1
Predicted       : 1
True positives  : 1
False positives : 0
False negatives : 0

Precision : 1.000
Recall    : 1.000
F1        : 1.000
```

---

### Regression Safety

The normalization changes were validated against the complete benchmark rather than only Case 06.

This was important because changing negative-test generation to solve one case initially caused Cases 11–14 to fail.

The development process therefore followed:

```text
Change
  │
  ▼
Run Target Case
  │
  ▼
Check Result
  │
  ▼
Run Full 15-Case Regression
  │
  ▼
Confirm No Regression
```

The final implementation reached:

```text
Cases tested : 15
Cases passed : 15
Cases failed : 0

Average Precision : 1.000
Average Recall    : 1.000
Average F1        : 1.000
```

---

### Goal of Normalization

The purpose of normalization is not to hide runtime observations.

It is to distinguish between:

* Duplicate findings
* Secondary observations
* Meaningful independent contract violations

The final report should contain **precise, evidence-backed drift findings** rather than simply reporting every invalid request that an API accepted.

## 📊 Evaluation

The project includes an automated evaluator that compares the drift findings produced by API Contract Drift Hunter with the expected findings defined by the benchmark.

The evaluation focuses on three standard metrics:

- **Precision**
- **Recall**
- **F1 Score**

### Evaluation Metrics

#### Precision

Precision measures how many of the predicted findings are actually correct.

```text
Precision = True Positives / (True Positives + False Positives)
````

A high precision means the system produces fewer incorrect or unnecessary findings.

---

#### Recall

Recall measures how many of the expected contract drifts were successfully detected.

```text
Recall = True Positives / (True Positives + False Negatives)
```

A high recall means the system is successfully finding the expected API contract violations.

---

#### F1 Score

F1 is the harmonic mean of precision and recall.

```text
F1 = 2 × Precision × Recall / (Precision + Recall)
```

F1 provides a single metric that balances both detection coverage and finding accuracy.

---

### Evaluation Terminology

| Metric              | Meaning                                                   |
| ------------------- | --------------------------------------------------------- |
| True Positive (TP)  | A predicted finding that matches an expected drift        |
| False Positive (FP) | A predicted finding that is not expected by the benchmark |
| False Negative (FN) | An expected drift that was not detected                   |
| Precision           | Accuracy of the predicted findings                        |
| Recall              | Coverage of expected findings                             |
| F1                  | Balance between precision and recall                      |

---

### Evaluator Workflow

The evaluator receives the normalized findings in a simplified format.

For example:

```json
{
  "issues": [
    {
      "endpoint": "/users",
      "issue_type": "missing_required_request_field",
      "field_or_parameter": "email",
      "expected": "required",
      "actual": "missing"
    }
  ]
}
```

The evaluator compares these predicted issues against the benchmark's `expected.json` file.

The result contains:

```json
{
  "expected_drifts": 1,
  "predicted_issues": 1,
  "true_positives": 1,
  "false_positives": 0,
  "false_negatives": 0,
  "precision": 1.0,
  "recall": 1.0,
  "f1": 1.0
}
```

---

### Per-Case Evaluation

Each benchmark case is evaluated independently.

For example, a successful case produces:

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

This makes it possible to identify regressions introduced by changes to individual pipeline components.

---

### 15-Case Regression Evaluation

The project includes `run_regression.py`, which executes all 15 benchmark cases and calculates aggregate metrics.

The regression process:

```text
Case 01 ─┐
Case 02  │
Case 03  │
Case 04  │
Case 05  │
Case 06  │
Case 07  │
Case 08  ├──► Pipeline ──► Evaluation
Case 09  │
Case 10  │
Case 11  │
Case 12  │
Case 13  │
Case 14  │
Case 15 ─┘
                    │
                    ▼
             Regression Summary
```

The regression runner records:

* Number of cases tested
* Number of cases passed
* Number of cases failed
* Average precision
* Average recall
* Average F1
* Individual case results

Results are also saved to:

```text
results/regression_summary.json
```

---

### Final Benchmark Result

The final implementation passes the complete benchmark:

```text
============================================================
REGRESSION SUMMARY
============================================================

Cases tested : 15
Cases passed : 15
Cases failed : 0

Average Precision : 1.000
Average Recall    : 1.000
Average F1        : 1.000

ALL 15 CASES PASSED
============================================================
```

### Final Metrics

| Metric            | Result |
| ----------------- | -----: |
| Cases Tested      |     15 |
| Cases Passed      |     15 |
| Cases Failed      |      0 |
| Average Precision |  1.000 |
| Average Recall    |  1.000 |
| Average F1        |  1.000 |

This final regression result confirms that the changes made to negative-test generation, runtime drift detection, and finding normalization did not introduce regressions across the benchmark.

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
````

### 📂 Directory Responsibilities

#### `agents/`

Contains the main API Contract Drift Hunter pipeline.

The modules are responsible for:

* Contract extraction
* Source-code analysis
* Static drift detection
* Valid request generation
* Runtime verification
* Negative-test generation
* Negative runtime verification
* Runtime drift detection
* Finding normalization
* Pipeline orchestration

#### `baseline/`

Contains the baseline implementation used for comparison and benchmark evaluation.

#### `benchmark/`

Contains the 15 benchmark cases used to evaluate the system.

Each case contains the API contract, implementation, and expected result.

Typical case structure:

```text
benchmark/caseXX/
├── openapi.yaml
├── app.py
└── expected.json
```

#### `evaluator/`

Contains the evaluation logic used to compare predicted drift findings with the expected benchmark findings.

The evaluator calculates:

* True positives
* False positives
* False negatives
* Precision
* Recall
* F1 score

#### `tests/`

Contains project-level tests used to validate individual components and behavior.

#### `results/`

Stores generated pipeline and regression results.

Example:

```text
results/
├── case06_pipeline_results.json
├── case11_pipeline_results.json
├── ...
└── regression_summary.json
```

These files contain structured outputs from the pipeline and evaluation stages.

### 📄 Important Root Files

| File                | Purpose                                      |
| ------------------- | -------------------------------------------- |
| `README.md`         | Project documentation and reproduction guide |
| `requirements.txt`  | Python dependencies                          |
| `run_regression.py` | Runs all 15 benchmark cases                  |
| `.gitignore`        | Defines files excluded from Git              |
| `pipeline.py`       | Main pipeline orchestration                  |

### 🔗 Overall Repository Flow

```text
benchmark/
    │
    ▼
OpenAPI + Application
    │
    ▼
agents/
    │
    ├── Contract Extraction
    ├── Source Analysis
    ├── Static Detection
    ├── Request Generation
    ├── Runtime Verification
    ├── Negative Testing
    ├── Runtime Drift Detection
    └── Finding Normalization
    │
    ▼
evaluator/
    │
    ▼
results/
    │
    ▼
Regression Summary
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
````

This contract information is used as the reference point for drift detection.

### Flask

The benchmark applications use Flask to provide local API implementations.

Each benchmark case runs its application on a dedicated local port.

For example:

```text
Case 01 → 5000
Case 02 → 5001
Case 03 → 5002
...
Case 11 → 5010
...
Case 15 → 5014
```

### JSON

JSON is used for structured communication between pipeline stages and for storing results.

Examples include:

```text
Runtime results
Drift findings
Evaluation results
Regression summaries
```

### Git and GitHub

Git is used to manage the project source code and track improvements.

The completed project is hosted in a GitHub repository:

**API Contract Drift Hunter**

The repository contains the implementation, benchmark cases, evaluator, regression runner, documentation, and generated project artifacts.

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



