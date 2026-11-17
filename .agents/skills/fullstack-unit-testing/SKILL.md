---
name: fullstack-unit-testing
description: >-
  Standards and execution procedures for continuous fullstack unit testing across Backend (pytest) and Frontend (vitest/React Testing Library). Use this skill whenever adding or modifying code to execute unit test suites, maintain ≥80% coverage, test edge cases, and verify zero regressions.
---

# Fullstack Unit Testing Skill

This skill enforces continuous, automated unit and integration testing across both the Backend and Frontend codebases after any change.

---

## 1. Testing Mandate

Whenever changes are made to application code:
1. **Always run unit tests** for the affected stack(s) before concluding the task.
2. **Write new unit tests** covering new endpoints, state transitions, calculations, and UI components.
3. **Follow the Arrange-Act-Assert (AAA)** pattern and **F.I.R.S.T.** principles (Fast, Isolated, Repeatable, Self-Validating, Timely).
4. **Never conclude with failing tests**. All tests in the test suite must be green.

---

## 2. Backend Testing (Pytest)

### Environment & Tools
- Test Framework: `pytest`
- API Testing: `fastapi.testclient.TestClient` (`httpx`)
- Test Location: `Backend/tests/`

### Execution Command
```powershell
.\Backend\venv\Scripts\pytest.exe Backend/tests -v
```

### Coverage Requirements
- Target: **≥80% coverage** on core services, state machines, and business rules.
- Test both **happy paths** and **negative/edge conditions**:
  - Mandate expiry within safety margin
  - Unsupported pause durations
  - Early resume with payment method health checks
  - Customer-side out-of-band mandate revocation
  - Idempotency key handling

---

## 3. Frontend Testing (Vitest & React Testing Library)

### Environment & Tools
- Test Runner: `vitest`
- DOM Simulation: `jsdom`
- Component Testing: `@testing-library/react`, `@testing-library/jest-dom`
- Test Location: `Frontend/src/**/*.test.{js,jsx}`

### Execution Command
```powershell
npm.cmd --prefix Frontend test
# or
npm.cmd --prefix Frontend run test:run
```

### Component Testing Rules
- Verify all 5 UI states: Empty, Loading, Error, Success, Disabled.
- Verify WCAG 2.2 AA accessibility (accessible roles, labels, keyboard interaction).
- Verify form validation messages on blur/submit.

---

## 4. Post-Test Verification & Changelog
Immediately after running test suites, record results in `testing/changelogs.md` under `- **Verification / Test Result**:`.
