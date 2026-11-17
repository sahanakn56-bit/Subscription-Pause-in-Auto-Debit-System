# Standard Operating Procedure: Software Project Development

A repeatable procedure for taking a software project from idea to production and maintenance. It covers planning, design, implementation, unit testing and other test levels, code review, CI/CD, release, and operations. Adapt the depth of each step to team size and project risk.

---

## 0. How to Use This SOP

- **Roles** referenced: Product Owner (PO), Tech Lead (TL), Developer (Dev), QA Engineer (QA), DevOps/SRE, Security Reviewer.
- On small teams, one person may hold several roles. The steps still apply.
- Each phase lists **Inputs**, **Activities**, **Outputs**, and **Exit Criteria**. Do not move to the next phase until exit criteria are met.

---

## 1. Phase 1: Initiation and Requirements

**Inputs:** Business problem, stakeholder needs, constraints (budget, time, compliance).

**Activities**
1. Write a one-page **problem statement**: who has the problem, why it matters, what success looks like.
2. Identify stakeholders and users; run interviews or review existing data.
3. Capture requirements:
   - **Functional**: user stories with acceptance criteria (Given / When / Then)
   - **Non-functional**: performance, security, availability, scalability, accessibility, compliance
4. Define scope: in scope, out of scope, assumptions, dependencies.
5. Identify risks and record them in a risk register (likelihood, impact, mitigation, owner).
6. Define measurable success metrics (KPIs).

**Outputs:** Problem statement, Software Requirements Specification (SRS) or product backlog, risk register.

**Exit Criteria:** Requirements reviewed and signed off by PO and TL; acceptance criteria are testable.

---

## 2. Phase 2: Planning

**Activities**
1. Break work into epics → stories → tasks; estimate (story points or time).
2. Prioritise the backlog (MoSCoW or value vs. effort).
3. Choose a delivery methodology (Scrum, Kanban, or hybrid) and set cadence (e.g. 2-week sprints).
4. Define milestones, a release plan, and resourcing.
5. Agree on the **Definition of Ready** and **Definition of Done** (see Section 15).
6. Set up tooling: issue tracker, repository, CI/CD, documentation space, communication channels.

**Outputs:** Roadmap, prioritised backlog, sprint plan, tooling in place.

**Exit Criteria:** Team understands scope and plan; first sprint is committed.

---

## 3. Phase 3: Architecture and Design

**Activities**
1. Choose architecture style (monolith, modular monolith, microservices, serverless) and justify the choice.
2. Produce design artefacts:
   - System context and component diagrams
   - Data model / ER diagram
   - API contracts (OpenAPI/Swagger, GraphQL schema)
   - Sequence diagrams for critical flows
3. Record significant decisions as **Architecture Decision Records (ADRs)**: context, decision, alternatives, consequences.
4. Perform **threat modelling** (e.g. STRIDE) and define security controls (authentication, authorisation, encryption, secrets management).
5. Plan for observability (logging, metrics, tracing) and failure handling (retries, timeouts, idempotency).
6. For UI work: wireframes, prototypes, and adherence to the design system and accessibility standards.
7. Select the **test strategy** (see Section 7) at design time, not after coding.

**Outputs:** Design document, ADRs, API specs, threat model, test strategy.

**Exit Criteria:** Design review completed by TL and at least one peer; security review passed for high-risk components.

---

## 4. Phase 4: Environment and Repository Setup

**Activities**
1. Create the repository with a standard structure:
   ```
   project/
   ├── src/            # application code
   ├── tests/          # unit, integration, e2e tests
   ├── docs/           # architecture, ADRs, runbooks
   ├── scripts/        # automation helpers
   ├── .github/        # CI workflows, PR templates (or equivalent)
   ├── README.md
   ├── CONTRIBUTING.md
   ├── CHANGELOG.md
   └── LICENSE
   ```
2. Define the **branching strategy** (Section 5).
3. Configure linting, formatting, and type checking; enforce with **pre-commit hooks**.
4. Set up dependency management with lockfiles; enable automated dependency and vulnerability scanning.
5. Configure environments: local, dev, staging, production. Keep them as similar as possible (containers, infrastructure as code).
6. Manage configuration and secrets outside the code (environment variables, secret manager). **Never commit secrets.**
7. Write a README covering: purpose, setup in under 15 minutes, how to run tests, how to contribute.

**Exit Criteria:** A new developer can clone, build, run, and test the project by following the README alone.

---

## 5. Phase 5: Implementation

### 5.1 Branching and Commits
- Recommended: **trunk-based development** with short-lived branches, or **GitHub Flow**. Use GitFlow only if release cycles demand it.
- Branch naming: `feature/<ticket>-short-description`, `fix/<ticket>-...`, `chore/...`
- Commits are small and focused. Use **Conventional Commits**:
  `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Link every branch and PR to a ticket.

### 5.2 Coding Standards
- Follow the language's style guide and the project linter (e.g. PEP 8, Google Java Style, Airbnb JS).
- Principles: **SOLID**, **DRY**, **KISS**, **YAGNI**; prefer composition over inheritance.
- Keep functions small and single-purpose; use meaningful names; avoid magic numbers.
- Validate all inputs; handle errors explicitly; never swallow exceptions silently.
- Comment the *why*, not the *what*; keep public APIs documented (docstrings/JSDoc).

### 5.3 Secure Coding
- Follow **OWASP Top 10** and ASVS guidance.
- Parameterise queries; encode output; enforce least privilege.
- Do not log sensitive data (passwords, tokens, personal data).
- Review third-party dependencies before adding them (licence, maintenance, vulnerabilities).

### 5.4 Daily Developer Workflow
1. Pull the latest main branch; create a feature branch.
2. Understand the acceptance criteria; write the tests first or alongside the code (Section 6).
3. Implement in small increments; run tests locally on every change.
4. Run linter, formatter, and type checks (pre-commit enforces this).
5. Push and open a Pull Request early (draft PRs are fine).
6. Address review feedback; merge when all checks pass.

---

## 6. Unit Testing Standards

Unit tests verify the smallest testable pieces of code (functions, methods, classes) **in isolation**, quickly and deterministically.

### 6.1 Principles (F.I.R.S.T.)
- **Fast**: milliseconds per test; the full unit suite runs in seconds to a couple of minutes
- **Isolated/Independent**: no dependence on test order or shared state
- **Repeatable**: same result every run, in any environment
- **Self-validating**: pass/fail is automatic, with no manual inspection
- **Timely**: written with or before the production code

### 6.2 Structure: Arrange-Act-Assert (AAA)
```python
def test_apply_discount_reduces_total_by_percentage():
    # Arrange
    cart = Cart(items=[Item("book", price=100)])

    # Act
    total = cart.apply_discount(percent=10)

    # Assert
    assert total == 90
```

### 6.3 What to Test
- Happy paths and expected outputs
- **Boundary values** (0, 1, max, min, empty, null)
- **Edge cases and invalid inputs**
- **Error paths** (exceptions, failures from dependencies)
- Business rules and branching logic
- Bug fixes: write a failing test that reproduces the bug first (regression test)

### 6.4 What Not to Test
- Third-party library internals
- Trivial getters/setters with no logic
- Private implementation details (test behaviour through public interfaces)

### 6.5 Test Doubles
| Type | Purpose |
|---|---|
| **Stub** | Returns canned data |
| **Mock** | Verifies interactions (calls, arguments) |
| **Fake** | Lightweight working implementation (e.g. in-memory repository) |
| **Spy** | Records calls while delegating to the real object |

Mock only external boundaries (network, database, filesystem, clock, randomness). Over-mocking makes tests brittle.

### 6.6 Naming and Organisation
- Name tests by behaviour: `test_<unit>_<scenario>_<expected result>`
- One logical assertion focus per test
- Mirror the source structure in the test directory
- Use fixtures/factories for shared setup; avoid duplicated setup code

### 6.7 Coverage
- Track **line and branch coverage**; a common target is **≥ 80%** overall with higher coverage on critical business logic
- Coverage is a floor, not a goal. High coverage with weak assertions is false confidence.
- Enforce a coverage gate in CI, and require **no coverage decrease** on new code
- Consider **mutation testing** (e.g. Stryker, PIT, mutmut) on critical modules to verify test quality

### 6.8 Common Tools
| Language | Frameworks |
|---|---|
| Python | pytest, unittest, pytest-cov |
| JavaScript/TypeScript | Jest, Vitest, Mocha |
| Java | JUnit 5, Mockito |
| C# | xUnit, NUnit, Moq |
| Go | `testing`, testify |

### 6.9 Optional Practice: TDD
Red → Green → Refactor: write a failing test, write the minimum code to pass, then refactor with the test as a safety net.

---

## 7. Overall Test Strategy (Test Pyramid)

```
        /\
       /E2E\          Few: critical user journeys
      /------\
     /Integr. \       Some: components + real dependencies
    /----------\
   /   Unit     \     Many: fast, isolated logic tests
  /--------------\
```

| Level | Scope | Speed | Run when |
|---|---|---|---|
| **Unit** | Single function/class | Very fast | Every commit |
| **Integration** | Modules + DB/queues/APIs | Moderate | Every PR |
| **Contract** | API compatibility between services (e.g. Pact) | Fast | Every PR |
| **End-to-End (E2E)** | Full user flows (Playwright, Cypress, Selenium) | Slow | PR/merge/nightly |
| **Performance/Load** | Throughput, latency under load (k6, JMeter, Locust) | Slow | Before release / scheduled |
| **Security** | SAST, DAST, dependency scan, penetration tests | Varies | CI + periodic |
| **Accessibility** | axe, Lighthouse, manual checks | Fast-moderate | UI changes |
| **Smoke** | Minimal checks that the deployment works | Fast | After every deploy |
| **Regression** | Previously fixed defects stay fixed | Varies | Every release |
| **UAT** | Stakeholders validate against business needs | Manual | Before release |

**Test data:** use synthetic or anonymised data; never real production personal data in lower environments.

**Flaky tests:** quarantine and fix quickly; do not ignore. A flaky suite erodes trust.

---

## 8. Code Review Procedure

**Author checklist (before requesting review)**
- [ ] Code builds and all tests pass locally
- [ ] New/changed behaviour has tests
- [ ] Linter and formatter pass
- [ ] PR is small (ideally under ~400 changed lines) and has a clear description: what, why, how tested, screenshots for UI
- [ ] Documentation and changelog updated where relevant
- [ ] No secrets, debug code, or commented-out code

**Reviewer checklist**
- [ ] Correctness: does it meet the acceptance criteria?
- [ ] Design: fits architecture, no unnecessary complexity
- [ ] Readability and naming
- [ ] Test quality: meaningful assertions, edge cases covered
- [ ] Security: input validation, authorisation, data exposure
- [ ] Performance: obvious inefficiencies (N+1 queries, unbounded loops)
- [ ] Error handling and logging
- [ ] Backward compatibility and migrations

**Rules**
- At least **one approval** (two for high-risk or core modules); the author does not approve their own PR
- Respond to review requests within one working day
- Be specific and kind; distinguish blocking issues from suggestions (e.g. `nit:`)
- Resolve all blocking comments before merging; prefer **squash merge** for a clean history

---

## 9. Continuous Integration (CI)

Every push and PR triggers an automated pipeline. A merge is **blocked** if any required stage fails.

**Typical pipeline stages**
1. Checkout and dependency install (cached)
2. Lint, format check, type check
3. Build / compile
4. **Unit tests** with coverage report
5. Integration and contract tests
6. Static analysis (SAST, e.g. SonarQube, CodeQL, Semgrep)
7. Dependency and licence scan (e.g. Dependabot, Snyk, Trivy)
8. Secret scanning
9. Build artefact (container image, package), versioned and stored in a registry
10. Publish test and coverage reports

**Quality gates (example)**
- All required checks green
- Coverage on new code ≥ 80%
- No new critical/high vulnerabilities
- No new code smells above agreed threshold

Keep the pipeline fast (target **under 10 minutes** for PR feedback); run slower suites on merge or nightly.

---

## 10. Continuous Delivery and Deployment (CD)

1. **Infrastructure as Code** (Terraform, CloudFormation, Pulumi) for all environments.
2. Deploy automatically to **dev** on merge; promote to **staging**, then **production**.
3. Staging mirrors production; run smoke, E2E, and performance tests there.
4. Use safe rollout strategies: **blue/green**, **canary**, or **feature flags**.
5. Database migrations are versioned (Flyway, Alembic, Liquibase), backward compatible, and tested; follow the expand-then-contract pattern.
6. Every deployment has a documented, tested **rollback plan**.
7. Production deployments require an approval gate for high-risk changes and are avoided at high-risk times (e.g. Friday evenings).

---

## 11. Release Management

**Pre-release checklist**
- [ ] All planned stories meet the Definition of Done
- [ ] Regression, performance, and security testing complete
- [ ] UAT signed off by the PO
- [ ] Documentation, API docs, and release notes ready
- [ ] Monitoring, dashboards, and alerts ready for new features
- [ ] Rollback plan verified
- [ ] Stakeholders and support teams informed

**Versioning:** use **Semantic Versioning** (`MAJOR.MINOR.PATCH`): breaking change, backward-compatible feature, backward-compatible fix.

**Release artefacts:** git tag, changelog entry, release notes, deployed artefact reference.

---

## 12. Monitoring and Operations

- **Observability:** structured logs, metrics (latency, traffic, errors, saturation), distributed tracing
- Define **SLIs/SLOs** (e.g. 99.9% availability, p95 latency < 300 ms) and alert on SLO burn, not noise
- Maintain **runbooks** for common incidents; keep an on-call rotation for production services
- Run **post-release verification** (smoke tests, dashboards) after every deploy

### Incident Response
1. Detect and triage; assign severity (SEV1-SEV4)
2. Communicate status to stakeholders
3. Mitigate first (rollback, feature flag off), then diagnose
4. Resolve and verify
5. Hold a **blameless post-mortem** within a few days: timeline, root cause, contributing factors, action items with owners

---

## 13. Maintenance and Continuous Improvement

- Triage bugs by severity and priority; fix critical issues immediately
- Schedule regular **dependency updates** and security patching
- Budget time for **refactoring and tech debt** (e.g. 10-20% of capacity); track debt visibly
- Hold **retrospectives** each sprint; turn findings into concrete actions
- Review metrics regularly (Section 14) and adjust the process accordingly
- Archive or retire unused features and services deliberately

---

## 14. Metrics to Track

| Area | Metrics |
|---|---|
| Delivery (DORA) | Deployment frequency, lead time for changes, change failure rate, time to restore service |
| Quality | Defect escape rate, test pass rate, flaky test count, coverage trend |
| Process | Cycle time, PR review time, sprint predictability |
| Reliability | Uptime, error rate, SLO attainment, MTTR |
| Security | Open vulnerabilities by severity, time to patch |

Use metrics to improve the process, not to rank individuals.

---

## 15. Definitions

### Definition of Ready (story can enter a sprint)
- [ ] Clear description and acceptance criteria
- [ ] Dependencies identified and unblocked
- [ ] Estimated and small enough for one sprint
- [ ] Design/UX inputs available if needed

### Definition of Done (story is complete)
- [ ] Code implemented and merged via reviewed PR
- [ ] **Unit tests written and passing; coverage thresholds met**
- [ ] Integration/E2E tests added or updated where relevant
- [ ] CI pipeline green (lint, build, tests, security scans)
- [ ] No known critical or high defects
- [ ] Accessibility and performance requirements met
- [ ] Documentation updated (README, API docs, ADRs, runbooks)
- [ ] Deployed to staging and verified against acceptance criteria
- [ ] PO acceptance obtained

---

## 16. Documentation Standards

| Document | Purpose | Owner |
|---|---|---|
| README | Setup, usage, contribution | Dev team |
| Architecture / design docs + ADRs | Why the system is built this way | TL |
| API documentation (OpenAPI) | Contract for consumers | Dev team |
| Runbooks | How to operate and recover | DevOps/SRE |
| Test plan/strategy | What and how we test | QA/TL |
| Release notes / CHANGELOG | What changed per version | PO/TL |
| Post-mortems | Learning from incidents | Incident lead |

Keep docs **in the repository** next to the code where possible, and review them in PRs.

---

## 17. Quick-Reference Summary

1. **Understand** the problem and write testable requirements.
2. **Plan** the work; agree on Definition of Ready/Done.
3. **Design** the architecture, security, and test strategy up front.
4. **Set up** the repo, tooling, and CI from day one.
5. **Implement** in small branches with coding standards and secure coding practices.
6. **Test** at every level: many unit tests, some integration tests, few E2E tests.
7. **Review** every change through a pull request.
8. **Automate** build, test, scan, and deploy through CI/CD with quality gates.
9. **Release** with versioning, a rollback plan, and verification.
10. **Operate** with monitoring, runbooks, and blameless post-mortems.
11. **Improve** continuously using metrics and retrospectives.

---

> This SOP is a baseline. Tailor thresholds (coverage, review count, pipeline time) to your team's size, risk profile, and any regulatory requirements, and review the SOP itself at least once a year.
