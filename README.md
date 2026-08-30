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

## 🧪 Full 15-Case Regression

The project includes an automated regression runner that executes the complete benchmark suite of 15 API contract drift cases.

The regression suite is used to verify that improvements to one part of the pipeline do not introduce failures in other benchmark cases.

### Run the Complete Regression

From the project root, run:

```bash
python run_regression.py
````

The regression runner executes:

```text
case01
case02
case03
case04
case05
case06
case07
case08
case09
case10
case11
case12
case13
case14
case15
```

Each case is executed through the complete API Contract Drift Hunter pipeline.

### Regression Process

```text
                  15 Benchmark Cases
                         │
                         ▼
                 ┌─────────────────┐
                 │ run_regression  │
                 │      .py        │
                 └────────┬────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
       Case 01          Case 02         Case 03
          │               │               │
          └───────────────┼───────────────┘
                          │
                         ...
                          │
                          ▼
                       Case 15
                          │
                          ▼
                  Pipeline Evaluation
                          │
                          ▼
                 Regression Summary
```

### What Is Checked?

For every case, the regression runner records:

* Case ID
* Pass/fail status
* Precision
* Recall
* F1 score

A case is considered **PASS** when:

```text
Precision = 1.000
Recall    = 1.000
F1        = 1.000
```

Otherwise, the case is marked as **FAIL**.

### Regression Output

A successful regression run produces a summary similar to:

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

### Results File

The regression runner saves the summary to:

```text
results/regression_summary.json
```

The file contains:

```text
Total cases
Passed cases
Failed cases
Average precision
Average recall
Average F1
Individual case results
```

### Regression During Development

The 15-case regression suite was also used during development to prevent changes from breaking previously working cases.

For example, changes to negative-test generation initially improved one benchmark case but caused multiple other cases to fail.

The development workflow was therefore:

```text
Modify Implementation
        │
        ▼
Run Target Case
        │
        ▼
Check Detection Result
        │
        ▼
Run Full Regression
        │
        ▼
15-Case Verification
        │
        ▼
Commit Only Stable Changes
```

This approach helped ensure that improvements to negative testing and finding normalization remained compatible with the complete benchmark.

### Final Regression Status

The final implementation achieved:

```text
Cases tested : 15
Cases passed : 15
Cases failed : 0

Average Precision : 1.000
Average Recall    : 1.000
Average F1        : 1.000
```

This represents a complete pass of the available 15-case benchmark.

## 🏆 Final Benchmark Result

The final version of API Contract Drift Hunter was validated against all 15 benchmark cases.

### Final Results

| Metric | Result |
|---|---:|
| Cases Tested | **15** |
| Cases Passed | **15** |
| Cases Failed | **0** |
| Average Precision | **1.000** |
| Average Recall | **1.000** |
| Average F1 | **1.000** |

### Result Summary

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
````

### What This Result Demonstrates

The final implementation successfully detected the expected benchmark behavior across the complete 15-case test suite.

The final system achieved:

* **100% precision** — no false-positive findings across the benchmark evaluation.
* **100% recall** — all expected benchmark drifts were detected.
* **100% F1** — perfect balance between precision and recall.
* **15/15 benchmark cases passed**.

### Development and Regression Improvements

The final result was achieved through iterative improvements to the detection pipeline.

In particular, the project improved:

1. **Negative-test generation**

   * Added targeted property-level validation tests.
   * Preserved required-field testing.
   * Added support for type and constraint violations.

2. **Runtime drift detection**

   * Used actual API responses as evidence.
   * Distinguished accepted invalid requests from correctly rejected requests.

3. **Finding normalization**

   * Removed duplicate findings.
   * Prioritized meaningful required-field violations.
   * Reduced secondary observations that could become false positives.

4. **Regression validation**

   * Re-ran all 15 cases after major changes.
   * Prevented a fix for one benchmark case from breaking other cases.

### Reproducible Result

The final benchmark can be reproduced from the project root with:

```bash
python run_regression.py
```

The generated regression summary is saved to:

```text
results/regression_summary.json
```

Individual pipeline results are saved as:

```text
results/caseXX_pipeline_results.json
```

### Final Status

```text
✅ 15 / 15 benchmark cases passed
✅ Precision: 1.000
✅ Recall:    1.000
✅ F1:        1.000
✅ Regression complete
```

## 🧪 Example: Case 06

Case 06 demonstrates why API Contract Drift Hunter uses both **negative testing** and **finding normalization**.

### Contract

The Case 06 API documents required request fields and their expected types.

The system generates negative requests from this contract to verify whether the implementation actually enforces the documented rules.

### Initial Detection

During development, the runtime verifier observed multiple accepted invalid requests.

The API accepted:

```json
{
  "name": 123,
  "email": "test"
}
````

even though `name` was documented as a string.

It also accepted a request where the required `email` field was omitted:

```json
{
  "name": "test"
}
```

The runtime evidence therefore contained multiple potential findings:

```text
1. missing_required_request_field → email
2. request_body_type_mismatch     → name
3. request_body_type_mismatch     → email
```

### Initial Evaluation

Reporting all observations independently produced false positives:

```text
Expected drifts : 1
Predicted issues: 3

True positives  : 1
False positives : 2
False negatives : 0

Precision : 0.333
Recall    : 1.000
F1        : 0.500
```

The problem was not that the runtime tests were incorrect. The problem was that multiple runtime observations were being treated as independent final findings.

### Improvement

The pipeline was improved by separating:

```text
Negative Test Generation
          │
          ▼
Runtime Verification
          │
          ▼
Runtime Evidence
          │
          ▼
Drift Detection
          │
          ▼
Finding Normalization
```

The negative-test generator continues to create relevant property-level tests, while the normalizer determines which observations should become final findings.

### Required-Field Priority

For Case 06, the missing required field is treated as the primary finding.

The final normalized finding is:

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

The runtime evidence shows that the API returned a successful response even though the required field was missing:

```json
{
  "test_type": "required_field_violation",
  "field": "email",
  "expected_status": 400,
  "actual_status": 201,
  "validation_enforced": false
}
```

### Final Evaluation

After the improvement:

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

### Key Lesson

Case 06 demonstrated an important design principle:

> **Negative tests should provide broad evidence, while normalization should determine the precise final findings.**

Disabling property-level tests globally would have reduced coverage and caused other benchmark cases to fail.

Instead, the final solution preserved negative-test coverage and used evidence-based normalization to maintain precision.

## 🧪 Example: Case 11

Case 11 demonstrates a **request body type-validation drift** and shows why property-level negative testing must remain enabled even when the request body contains required fields.

### Contract

The OpenAPI contract defines the `/cart/items` endpoint:

```yaml
paths:
  /cart/items:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - product_id
                - quantity
              properties:
                product_id:
                  type: integer
                quantity:
                  type: integer
                  minimum: 1
````

The important contract rules are:

```text
product_id → integer
quantity   → integer
quantity   → minimum 1
product_id → required
quantity   → required
```

### Implementation

The benchmark implementation accepts values directly from the JSON request:

```python
data = request.get_json(silent=True) or {}

item = {
    "product_id": data.get("product_id"),
    "quantity": data.get("quantity")
}

return jsonify(item), 201
```

There is no explicit runtime validation enforcing the documented property types.

### Expected Drift

The benchmark expects a type mismatch for `quantity`:

```json
{
  "case_id": "case11",
  "description": "Request body field has incorrect type",
  "endpoint": "POST /cart/items",
  "field": "quantity",
  "expected_type": "integer",
  "actual_type": "string",
  "drift": true,
  "severity": "medium"
}
```

### Negative Test

The negative test generator creates a type-violation request:

```json
{
  "product_id": 1,
  "quantity": "2"
}
```

The contract expects:

```text
quantity → integer
```

but the invalid request supplies:

```text
quantity → string
```

### Runtime Behavior

Because the implementation does not enforce the documented type, the API can accept the invalid value instead of rejecting it.

This runtime behavior provides evidence of contract drift.

The intended detection flow is:

```text
OpenAPI Contract
       │
       ▼
quantity: integer
       │
       ▼
Generate invalid value
quantity: "2"
       │
       ▼
Send request to API
       │
       ▼
API accepts invalid value
       │
       ▼
Runtime Drift
       │
       ▼
request_body_type_mismatch
```

### Important Development Lesson

Case 11 exposed a problem with an overly broad optimization.

An earlier approach effectively used:

```python
if required_fields:
    skip_property_tests()
```

This was problematic because Case 11 contains required fields **and** an independently meaningful property-level type constraint.

Skipping property-level tests whenever required fields exist would prevent the system from generating the test needed to detect the Case 11 drift.

### Correct Approach

The final design separates required-field testing from property-level testing.

```text
Required Fields
      │
      ├──► Required-field tests
      │
      ▼
Property Schemas
      │
      ├──► Type tests
      ├──► Constraint tests
      ├──► Enum tests
      └──► Nullability tests
```

The presence of required fields therefore does not automatically disable property-level tests.

### Regression Importance

Case 11 was especially important because changes made while fixing Case 06 initially caused Cases 11–14 to fail.

This demonstrated that a local fix should not be applied globally without running the complete regression suite.

The development cycle became:

```text
Fix Case 06
     │
     ▼
Run Case 06
     │
     ▼
Run Cases 11–14
     │
     ▼
Run Full 15-Case Regression
     │
     ▼
Confirm No Regression
```

### Final Result

After the negative-test generation and finding-normalization behavior was corrected, the complete benchmark achieved:

```text
Cases tested : 15
Cases passed : 15
Cases failed : 0

Average Precision : 1.000
Average Recall    : 1.000
Average F1        : 1.000
```

### Key Lesson

Case 11 demonstrates that:

> **Required-field testing and property-level validation testing are independent concerns.**

A robust drift detector should preserve both types of tests and use runtime evidence and finding normalization to determine which observations become final findings.

## 📝 Improvement Changelog

The project was developed iteratively using the 15-case benchmark as a regression suite.

The main improvements focused on increasing detection coverage while preventing false positives.

### Version 1 — Initial Pipeline

The initial implementation established the complete end-to-end pipeline:

```text
Contract
   ↓
Source Analysis
   ↓
Static Detection
   ↓
Request Generation
   ↓
Runtime Verification
   ↓
Negative Testing
   ↓
Runtime Drift Detection
   ↓
Evaluation
````

This provided the foundation for automated API contract drift detection.

---

### Version 2 — Required-Field Negative Testing

Required request-body fields were added to negative-test generation.

The generator creates requests where a documented required field is omitted while other fields receive valid values.

Example:

```json
{
  "name": "test"
}
```

when `email` is documented as required.

This allows the runtime verifier to detect implementations that accept incomplete requests.

---

### Version 3 — Property-Level Negative Testing

Property-level negative tests were added for individual schema properties.

Supported tests include:

```text
type violations
minimum violations
maximum violations
minLength violations
maxLength violations
minItems violations
maxItems violations
enum violations
nullability violations
```

This significantly improved the ability to detect validation drift.

---

### Version 4 — Case 06 Precision Improvement

Case 06 initially produced multiple runtime findings for one benchmark drift.

Initial result:

```text
Expected drifts : 1
Predicted issues: 3

Precision : 0.333
Recall    : 1.000
F1        : 0.500
```

The issue was that multiple runtime observations were being treated as independent final findings.

The pipeline was improved by strengthening finding normalization and prioritizing meaningful required-field evidence.

Final Case 06 result:

```text
Expected drifts : 1
Predicted issues: 1

Precision : 1.000
Recall    : 1.000
F1        : 1.000
```

---

### Version 5 — Avoiding Over-Aggressive Test Suppression

An intermediate solution attempted to disable property-level tests whenever required fields existed:

```python
if required_fields:
    skip_property_tests()
```

Although this could improve one case, it caused Cases 11–14 to lose important property-level coverage.

This approach was therefore rejected.

The final implementation keeps required-field and property-level testing as separate concerns.

---

### Version 6 — Case 11–14 Regression Fix

Cases 11–14 demonstrated that required fields and property constraints can coexist within the same request body.

The negative-test generator was adjusted so that the presence of required fields does not automatically suppress property-level tests.

For example, Case 11 requires testing:

```text
quantity → integer
```

while also documenting required fields.

The final design preserves both testing paths.

---

### Version 7 — Finding Normalization

Finding normalization was strengthened to:

* Deduplicate identical findings
* Create canonical finding identities
* Select the strongest type evidence
* Avoid duplicate required-field findings
* Prioritize required-field violations where appropriate
* Preserve independent property-level drift

This reduced false positives without reducing the underlying runtime test coverage.

---

### Version 8 — Full Regression Validation

After changes to negative-test generation and normalization, the complete 15-case benchmark was repeatedly executed.

The final result:

```text
Cases tested : 15
Cases passed : 15
Cases failed : 0

Average Precision : 1.000
Average Recall    : 1.000
Average F1        : 1.000
```

---

### Final Engineering Outcome

The final implementation follows three important principles:

```text
1. Generate broad evidence
          ↓
2. Analyze actual runtime behavior
          ↓
3. Normalize into precise findings
```

This avoids solving individual benchmark cases with overly restrictive rules and instead improves the underlying detection architecture.

## 🤖 Agent Trajectory

The project was developed through an iterative engineering process in which each change was validated against the benchmark before being retained.

The main objective was not only to make individual cases pass, but to improve the underlying detection pipeline while maintaining regression safety.

### Development Strategy

The development process followed this cycle:

```text
Understand Benchmark Case
          │
          ▼
Inspect Contract + Implementation
          │
          ▼
Identify Detection Gap
          │
          ▼
Modify Relevant Agent
          │
          ▼
Run Target Case
          │
          ▼
Inspect Runtime Evidence
          │
          ▼
Run Full Regression
          │
          ▼
Keep Change Only If Regression-Safe
````

### Trajectory 1 — Establish the Baseline

The first step was to understand the existing pipeline and run the benchmark cases.

The baseline established the initial behavior of:

* Contract extraction
* Source analysis
* Static detection
* Request generation
* Runtime verification
* Negative testing
* Runtime drift detection
* Finding normalization
* Evaluation

The benchmark results were then used to identify failing cases.

---

### Trajectory 2 — Investigate Case 06

Case 06 became an important debugging case because the system initially detected more findings than the benchmark expected.

The runtime evidence showed multiple accepted invalid requests.

The initial evaluation was:

```text
Expected drifts : 1
Predicted issues: 3
True positives  : 1
False positives : 2
False negatives : 0

Precision : 0.333
Recall    : 1.000
F1        : 0.500
```

The investigation showed that the problem was not simply negative-test generation.

The pipeline was collecting multiple valid runtime observations and treating them as separate final findings.

This led to an investigation of:

```text
negative_test_generator.py
runtime_drift_detector.py
finding_normalizer.py
```

---

### Trajectory 3 — Improve Required-Field Testing

Required-field negative tests were retained so the system could detect APIs that accept requests missing documented required fields.

For a required field such as:

```text
email
```

the generator creates a request without that field.

The runtime result is then analyzed to determine whether the API incorrectly accepts the request.

This allowed Case 06 to detect the expected required-field drift.

---

### Trajectory 4 — Add and Preserve Property-Level Testing

The next challenge was preserving property-level tests.

A property such as:

```yaml
quantity:
  type: integer
  minimum: 1
```

requires tests for:

```text
type violation
minimum violation
nullability violation
```

The generator was therefore designed to produce property-level tests independently of required-field tests.

This became particularly important for Cases 11–14.

---

### Trajectory 5 — Avoid the Global `required_fields` Shortcut

An intermediate implementation used logic equivalent to:

```python
if required_fields:
    skip_property_tests()
```

This helped suppress unwanted observations in one case, but it introduced a larger regression.

Cases containing both required fields and property-level constraints lost their necessary negative tests.

The approach was therefore rejected.

The important lesson was:

> A required-field test and a property-level test represent different validation behaviors and should not be globally treated as mutually exclusive.

---

### Trajectory 6 — Improve Finding Normalization

Instead of disabling useful tests, the pipeline was improved at the finding interpretation stage.

The normalizer was strengthened to:

```text
Collect Evidence
      │
      ▼
Deduplicate Findings
      │
      ▼
Group Related Findings
      │
      ▼
Prioritize Strong Evidence
      │
      ▼
Produce Precise Findings
```

This allowed the system to maintain broad runtime test coverage while controlling the number of final reported issues.

---

### Trajectory 7 — Validate Case 11

Case 11 was then used to verify that property-level testing remained active.

The contract defines:

```text
product_id → integer
quantity   → integer
quantity   → minimum 1
```

The implementation accepts request values directly without enforcing the documented types.

The negative test generator therefore produces a type violation such as:

```json
{
  "product_id": 1,
  "quantity": "2"
}
```

This provides runtime evidence for the expected type mismatch.

Case 11 helped confirm that the Case 06 fix did not disable necessary property-level detection.

---

### Trajectory 8 — Regression Across Cases 11–14

After changes to Case 06, Cases 11–14 were explicitly checked.

This was necessary because a change that improves one benchmark case can unintentionally suppress evidence needed by other cases.

The development process therefore moved from:

```text
Fix One Case
```

to:

```text
Fix One Case
      ↓
Run Related Cases
      ↓
Run Full Benchmark
      ↓
Confirm Regression Safety
```

---

### Trajectory 9 — Final 15-Case Validation

After the final changes were made, the complete benchmark was executed using:

```bash
python run_regression.py
```

The final result was:

```text
Cases tested : 15
Cases passed : 15
Cases failed : 0

Average Precision : 1.000
Average Recall    : 1.000
Average F1        : 1.000
```

### Engineering Lessons From the Trajectory

The development process resulted in several important design lessons:

1. **Do not optimize for a single benchmark case.**
2. **Negative-test generation should preserve broad validation coverage.**
3. **Runtime evidence should be separated from final finding interpretation.**
4. **Required-field and property-level validation are independent concerns.**
5. **Finding normalization is important for controlling false positives.**
6. **Every major change should be validated against the full regression suite.**
7. **A successful local fix is not sufficient unless it remains regression-safe.**

### Final Agent Workflow

The final development workflow can be summarized as:

```text
Benchmark
   │
   ▼
Contract + Source Inspection
   │
   ▼
Hypothesis
   │
   ▼
Targeted Code Change
   │
   ▼
Runtime Verification
   │
   ▼
Finding Analysis
   │
   ▼
Regression Testing
   │
   ▼
Stable Implementation
```

This iterative approach resulted in a final implementation that passed all 15 benchmark cases.
## 🧠 Key Engineering Lessons

The development of API Contract Drift Hunter highlighted several practical lessons about building reliable automated API validation systems.

### 1. Separate Contract Expectations From Runtime Behavior

The OpenAPI specification describes what the API **should** do, while the running application demonstrates what the API **actually** does.

The system therefore keeps these two sources separate:

```text
OpenAPI
   │
   ▼
Expected Behavior
````

and:

```text
Running API
   │
   ▼
Actual Behavior
```

Drift is identified by comparing the two.

---

### 2. Static Analysis Alone Is Not Enough

Source-code analysis can identify some contract mismatches, but validation behavior is often only observable when an actual request is executed.

For example, an implementation may read a field using:

```python
data.get("quantity")
```

Static analysis can identify the field, but it cannot necessarily determine whether the application rejects an invalid value such as:

```json
{
  "quantity": "2"
}
```

Runtime verification provides the missing evidence.

---

### 3. Negative Testing Is Essential

Valid requests mainly demonstrate that an endpoint works under expected conditions.

They do not adequately test whether the implementation enforces the contract.

Negative tests deliberately violate contract rules:

```text
Required field
      ↓
Remove field

Type constraint
      ↓
Use wrong type

Minimum constraint
      ↓
Use value below minimum

Enum constraint
      ↓
Use unsupported value

Nullability
      ↓
Use null
```

This makes negative testing a core part of contract-drift detection.

---

### 4. Required Fields and Property Constraints Are Different

A required-field violation answers:

> Does the API require this field to exist?

A type violation answers:

> Does the API enforce the field's documented type?

A constraint violation answers:

> Does the API enforce the documented value constraint?

These are different questions and should be tested independently.

This lesson became especially important when working with Cases 06 and 11–14.

---

### 5. Do Not Fix One Benchmark With a Global Shortcut

During development, disabling property-level tests whenever required fields existed appeared to solve one problem.

Conceptually:

```python
if required_fields:
    skip_property_tests()
```

However, this caused other benchmark cases to lose important tests.

The better approach was to preserve test coverage and improve the interpretation of the resulting evidence.

---

### 6. Runtime Evidence Should Be Preserved

A finding should not simply say:

```text
Type mismatch detected
```

It should retain evidence explaining why.

For example:

```json
{
  "test_type": "type_violation",
  "field": "email",
  "invalid_value": 123,
  "status_code": 201,
  "validation_enforced": false
}
```

Evidence makes findings easier to debug, explain, and reproduce.

---

### 7. Test Generation and Finding Generation Are Different Problems

A useful distinction emerged during development:

```text
Test Generation
      │
      ▼
"What should we test?"
```

versus:

```text
Finding Generation
      │
      ▼
"What actual behavior constitutes a final drift?"
```

The generator should provide sufficient coverage.

The detector and normalizer should determine whether the observed behavior represents a meaningful contract violation.

---

### 8. Normalization Improves Precision

A single endpoint can generate multiple related runtime observations.

Reporting every observation independently can create false positives.

Finding normalization provides a final interpretation layer:

```text
Raw Evidence
     │
     ▼
Grouping
     │
     ▼
Deduplication
     │
     ▼
Evidence Prioritization
     │
     ▼
Final Findings
```

This helped improve Case 06 from:

```text
Precision : 0.333
Recall    : 1.000
F1        : 0.500
```

to:

```text
Precision : 1.000
Recall    : 1.000
F1        : 1.000
```

---

### 9. Regression Testing Is Part of Development

A fix should not be considered complete after one benchmark passes.

The project uses the full 15-case regression suite to verify every significant change.

```text
Code Change
    │
    ▼
Target Case
    │
    ▼
Related Cases
    │
    ▼
Full 15-Case Regression
    │
    ▼
Accept / Rework
```

This prevented improvements for one case from silently breaking other cases.

---

### 10. Prefer Evidence-Based Detection

The final architecture follows a simple principle:

```text
Do not assume drift.
        ↓
Generate a targeted test.
        ↓
Execute it.
        ↓
Observe actual behavior.
        ↓
Compare against the contract.
        ↓
Report evidence-backed drift.
```

This makes the system more explainable and reduces reliance on assumptions.

---

### 11. Precision and Recall Must Be Balanced

A detector that reports everything may achieve high recall but poor precision.

A detector that reports only obvious issues may achieve high precision but miss expected drifts.

The goal is therefore:

```text
High Coverage
     +
Low False Positives
     =
Reliable Drift Detection
```

The final benchmark result demonstrates this balance:

```text
Precision : 1.000
Recall    : 1.000
F1        : 1.000
```

---

### 12. Reproducibility Matters

A benchmark result is most useful when another developer can reproduce it.

The project therefore documents:

* Installation
* Benchmark ports
* Single-case execution
* Full regression execution
* Result file locations
* Runtime requirements

The complete regression can be executed with:

```bash
python run_regression.py
```

---

### Summary

The most important engineering principle from the project is:

> **Generate broad, targeted runtime evidence, then use contract-aware detection and normalization to produce precise findings.**

This approach allows the system to maintain strong test coverage without sacrificing final-result precision.

## 🔁 Reproduction Guide

This guide provides the exact steps required to reproduce the final benchmark results from a clean checkout of the repository.

### 1. Clone the Repository

```bash
git clone https://github.com/VAMSHIKUMAR32501/api-contract-drift-hunter.git
cd api-contract-drift-hunter
````

### 2. Create a Virtual Environment

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify the Source

Run a Python compilation check:

```bash
python -m py_compile agents/*.py
```

No `IndentationError` or other Python syntax errors should be reported.

### 5. Run a Single Benchmark Case

Start the Flask application for the case.

Example — Case 06:

```bash
python benchmark/case06/app.py
```

The application runs on:

```text
http://127.0.0.1:5005
```

Keep the Flask server running.

Open a second terminal and run:

```bash
python agents/pipeline.py case06 http://127.0.0.1:5005
```

The pipeline executes all 12 stages and writes the result to:

```text
results/case06_pipeline_results.json
```

### 6. Reproduce Case 11

Start the Case 11 application:

```bash
python benchmark/case11/app.py
```

It runs on:

```text
http://127.0.0.1:5010
```

Then, from another terminal:

```bash
python agents/pipeline.py case11 http://127.0.0.1:5010
```

The result is saved to:

```text
results/case11_pipeline_results.json
```

### 7. Run the Complete Regression

For the final benchmark, run:

```bash
python run_regression.py
```

The regression runner evaluates all 15 cases.

```text
case01
case02
case03
case04
case05
case06
case07
case08
case09
case10
case11
case12
case13
case14
case15
```

### 8. Check the Final Result

A successful run should report:

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

### 9. Inspect Generated Results

The regression summary is stored at:

```text
results/regression_summary.json
```

Individual case results are stored as:

```text
results/case01_pipeline_results.json
results/case02_pipeline_results.json
...
results/case15_pipeline_results.json
```

### 10. Reproduce the Complete Workflow

The complete reproducible workflow is:

```text
Clone Repository
      │
      ▼
Create Virtual Environment
      │
      ▼
Install Dependencies
      │
      ▼
Verify Python Source
      │
      ▼
Start Benchmark API
      │
      ▼
Run Pipeline
      │
      ▼
Inspect Case Result
      │
      ▼
Run 15-Case Regression
      │
      ▼
Inspect regression_summary.json
```

### Runtime Requirement

For individual runtime-based pipeline execution, the corresponding Flask benchmark application must be running.

The benchmark applications use ports `5000` through `5014`.

For the automated regression runner, follow the execution behavior implemented in `run_regression.py` and ensure the required runtime environment is available.

### Expected Final State

After successful reproduction:

```text
15 / 15 cases passed
Precision = 1.000
Recall    = 1.000
F1        = 1.000
```

The generated results provide the evidence needed to verify the final benchmark performance.

## 🖥️ Runtime Requirement

API Contract Drift Hunter performs both static analysis and runtime verification.

Static analysis can inspect the contract and source code without starting the application. However, runtime-based drift detection requires the benchmark API to be running and accessible.

### Required Runtime Components

The runtime environment consists of:

- Python 3.x
- Flask benchmark applications
- Local HTTP connectivity
- The API Contract Drift Hunter pipeline
- Required Python dependencies from `requirements.txt`

### Benchmark API Servers

Each benchmark case contains its own Flask application.

The applications use dedicated local ports:

| Case | Port | Base URL |
|---|---:|---|
| `case01` | 5000 | `http://127.0.0.1:5000` |
| `case02` | 5001 | `http://127.0.0.1:5001` |
| `case03` | 5002 | `http://127.0.0.1:5002` |
| `case04` | 5003 | `http://127.0.0.1:5003` |
| `case05` | 5004 | `http://127.0.0.1:5004` |
| `case06` | 5005 | `http://127.0.0.1:5005` |
| `case07` | 5006 | `http://127.0.0.1:5006` |
| `case08` | 5007 | `http://127.0.0.1:5007` |
| `case09` | 5008 | `http://127.0.0.1:5008` |
| `case10` | 5009 | `http://127.0.0.1:5009` |
| `case11` | 5010 | `http://127.0.0.1:5010` |
| `case12` | 5011 | `http://127.0.0.1:5011` |
| `case13` | 5012 | `http://127.0.0.1:5012` |
| `case14` | 5013 | `http://127.0.0.1:5013` |
| `case15` | 5014 | `http://127.0.0.1:5014` |

### Starting an API

For example, to start Case 06:

```bash
python benchmark/case06/app.py
````

The Flask server should display:

```text
Running on http://127.0.0.1:5005
```

Keep the server running while executing the pipeline.

### Running the Pipeline

Open another terminal in the project root:

```bash
python agents/pipeline.py case06 http://127.0.0.1:5005
```

The pipeline can then execute runtime verification and negative runtime verification against the running API.

### Runtime Verification

The runtime stages perform the following operations:

```text
Generated Request
       │
       ▼
HTTP Request
       │
       ▼
Running Flask API
       │
       ▼
HTTP Response
       │
       ▼
Runtime Evidence
       │
       ▼
Drift Detection
```

Runtime evidence may include:

* HTTP status code
* Response body
* Response time
* Validation behavior
* Accepted/rejected state
* Runtime errors
* Observed field values and types

### Server Not Running

If the benchmark application is not running, the runtime verifier may receive a connection error such as:

```text
Connection refused
```

In this situation, runtime verification cannot establish the actual behavior of the API.

Therefore, when reproducing an individual runtime-based case, start the corresponding benchmark application first.

### Running Multiple Cases

Multiple benchmark applications can technically use different ports, but they do not need to be running simultaneously for normal single-case testing.

The recommended workflow is:

```text
Start Case
    │
    ▼
Run Pipeline
    │
    ▼
Inspect Result
    │
    ▼
Stop Server
    │
    ▼
Start Next Case
```

Stop a running Flask application with:

```text
CTRL + C
```

### Static vs Runtime Execution

The project combines two complementary approaches:

| Mode                          | Requires API Server? | Purpose                                |
| ----------------------------- | -------------------- | -------------------------------------- |
| Static analysis               | No                   | Analyze source and contract            |
| Request generation            | No                   | Generate requests from contract        |
| Runtime verification          | Yes                  | Observe actual API behavior            |
| Negative runtime verification | Yes                  | Test validation enforcement            |
| Runtime drift detection       | Yes                  | Detect behavior-based drift            |
| Evaluation                    | No*                  | Compare findings with expected results |

`*` Evaluation itself does not require an API server once the required pipeline results have been generated.

### Recommended Reproduction Environment

For the most reliable reproduction:

```text
Windows / Linux / macOS
        │
        ▼
Python 3.x
        │
        ▼
Virtual Environment
        │
        ▼
Project Dependencies
        │
        ▼
Local Flask Benchmark API
        │
        ▼
API Contract Drift Hunter
```

### Final Runtime Check

Before running a runtime-based case, verify that the expected port is listening.

For example, Case 06:

```text
http://127.0.0.1:5005
```

Then run:

```bash
python agents/pipeline.py case06 http://127.0.0.1:5005
```

This ensures that the runtime stages have access to the actual API implementation.


## 🎥 Solution Video

A short solution walkthrough is provided as part of the challenge submission.

### Video Duration

**Maximum duration: 5 minutes**

### Recommended Walkthrough

The video demonstrates the following:

```text
1. Problem
      ↓
2. Solution Architecture
      ↓
3. Key Agents / Pipeline
      ↓
4. Negative Testing
      ↓
5. Runtime Drift Detection
      ↓
6. Case 06 Demonstration
      ↓
7. Case 11 Demonstration
      ↓
8. Full 15-Case Regression
      ↓
9. Final Results
````

### Suggested Video Timeline

| Time        | Content                                           |
| ----------- | ------------------------------------------------- |
| 0:00 – 0:30 | Problem and project objective                     |
| 0:30 – 1:15 | Architecture and pipeline overview                |
| 1:15 – 2:00 | Negative-test generation and runtime verification |
| 2:00 – 2:45 | Case 06: required-field drift and normalization   |
| 2:45 – 3:30 | Case 11: property-level type drift                |
| 3:30 – 4:30 | Run the 15-case regression                        |
| 4:30 – 5:00 | Final metrics and key engineering decisions       |

### Demo Commands

The video can demonstrate a single case with:

```bash
python agents/pipeline.py case06 http://127.0.0.1:5005
```

and the complete regression with:

```bash
python run_regression.py
```

### Final Result Shown in the Video

The final regression should show:

```text
Cases tested : 15
Cases passed : 15
Cases failed : 0

Average Precision : 1.000
Average Recall    : 1.000
Average F1        : 1.000

ALL 15 CASES PASSED
```

### Video Focus

The walkthrough should emphasize the engineering decisions behind the solution:

* Contract-driven test generation
* Static source analysis
* Runtime verification
* Negative testing
* Evidence-based drift detection
* Finding normalization
* Regression-safe improvements

The goal of the video is to demonstrate both **how the solution works** and **why the final architecture produces reliable results**.

