---
name: project-development-sop
description: >-
  Standard Operating Procedure (SOP) for software development lifecycle: architecture design, test-driven implementation, unit/integration testing, code quality gates, security practices, and Definition of Done. Use this skill whenever planning, implementing, refactoring, testing, or reviewing features and fixes in this project.
---

# Software Project Development SOP

This skill outlines the required engineering standards, development lifecycle phases, testing requirements, and quality gates for building the **Subscription Pause in Auto-Debit System**.

---

## 1. Development Lifecycle & Workflow

Every feature, enhancement, or bug fix must progress through these structured phases:

### Phase 1: Requirements & Acceptance Criteria
- Clearly identify the business requirements before writing code.
- Define functional acceptance criteria in Given / When / Then format.
- Identify edge cases, failure scenarios, and boundary conditions upfront.

### Phase 2: Design & API Contracts
- Define the data model, API schemas, and contracts (OpenAPI / Pydantic models).
- Document non-trivial architectural decisions (ADRs) when changing system behavior.
- Plan error handling (HTTP status codes, standard JSON error responses), idempotency, and security constraints (OWASP).

### Phase 3: Implementation Standards
- **Clean Code Principles**: Apply SOLID, DRY, KISS, and YAGNI.
- **Explicit Error Handling**: Never catch exceptions silently. Validate all user and API inputs strictly.
- **No Committed Secrets**: Never hardcode API keys, passwords, or secrets. Use environment variables.
- **Conventional Commits**: Format commit messages as `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.

---

## 2. Testing Standards (The Test Pyramid)

All features must adhere to the test pyramid:

```
        /\
       /E2E\          Few: critical user journeys (Playwright/Cypress)
      /------\
     /Integr. \       Some: API endpoints + DB/services (FastAPI TestClient)
    /----------\
   /   Unit     \     Many: fast, isolated logic tests (pytest / vitest)
  /--------------\
```

### 2.1 Unit Testing Rules (F.I.R.S.T.)
- **Fast**: Milliseconds per test.
- **Isolated**: No shared state between tests; mock external dependencies (DB, payment gateways, network).
- **Repeatable**: Deterministic results on every run.
- **Self-Validating**: Automated pass/fail.

### 2.2 Test Structure: Arrange - Act - Assert (AAA)
Every unit test must follow the AAA structure:
```python
def test_pause_subscription_calculates_resumption_date_correctly():
    # Arrange
    service = SubscriptionService()
    start_date = date(2026, 12, 1)
    duration_days = 30

    # Act
    result = service.schedule_pause(subscription_id="sub_123", pause_start=start_date, duration_days=duration_days)

    # Assert
    assert result.status == "PAUSED"
    assert result.resumption_date == date(2026, 12, 31)
```

### 2.3 What to Test
- Expected happy paths.
- **Boundary conditions**: minimum pause duration, maximum allowed pause, leap years, month-end dates.
- **Edge cases & error paths**: invalid dates, pausing already paused subscriptions, debit dates falling inside pause windows.
- Regression tests for any bug fixed.

### 2.4 Test Coverage Gate
- Target **≥ 80%** test coverage on business logic and services.
- Never decrease test coverage when introducing new features.

---

## 3. Pre-Completion & Code Quality Checklist (Definition of Done)

Before completing any story, task, or bug fix, verify:

1. **Build & Syntax**:
   - Backend: Python code executes cleanly with no syntax or import errors.
   - Frontend: `npm run build` succeeds with zero errors.
2. **Automated Tests**:
   - All existing and new unit tests pass.
   - Edge cases and error states are tested.
3. **Security & OWASP**:
   - Inputs are validated and sanitized.
   - No sensitive information (passwords, tokens, payment details) logged in plain text.
   - Access control and authentication checked.
4. **Error Handling**:
   - Meaningful error messages returned to consumers; system fails safely.
5. **Documentation**:
   - API endpoints updated in Swagger/OpenAPI docs.
   - Setup instructions updated in README files if dependencies or variables changed.

---

## 4. References
- Full SOP manual: [project-development-sop.md](./references/project-development-sop.md)
