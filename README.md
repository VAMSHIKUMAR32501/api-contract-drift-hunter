# API Contract Drift Hunter

An automated system for detecting API contract drift between an OpenAPI specification and its actual implementation.

The system combines static source analysis with runtime verification and targeted negative testing to identify mismatches between what an API contract promises and what the implementation actually does.

---

## Problem

API contract drift occurs when an API implementation no longer behaves according to its documented OpenAPI contract.

Examples include:

- Request field type mismatches
- Missing required-field validation
- Invalid enum values being accepted
- Nullability mismatches
- Constraint violations
- Response type mismatches
- Status-code mismatches
- Undocumented response fields

The goal of this project is to automatically discover these inconsistencies.

---

## Solution

The system uses a multi-stage pipeline:

```text
OpenAPI Contract
       |
       v
Contract Extraction
       |
       v
Source Code Analysis
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
Evaluator
       |
       v
Final Drift Report