# Project Guidelines & Autonomous Agent Rules

## 1. Software Development SOP Mandate
Whenever planning, architecting, implementing, testing, or reviewing backend and frontend features:
- **Strictly enforce the procedures** defined in [.agents/skills/project-development-sop/SKILL.md](.agents/skills/project-development-sop/SKILL.md).
- **Architecture & API Contracts**: Define Pydantic models / OpenAPI schemas upfront; handle errors predictably with standard HTTP status codes.
- **Testing Pyramid**: Write unit tests following Arrange-Act-Assert (AAA) and FIRST principles. Cover happy paths, boundary conditions, edge cases, and error branches. Target ≥80% coverage on core logic.
- **Clean Code & Security**: Follow SOLID and DRY principles. Never commit secrets. Validate all inputs against OWASP guidelines. Format commits using Conventional Commits.
- **Definition of Done (DoD)**: Verify tests pass, builds succeed, error handling is implemented, and documentation is updated before completing any task.

## 2. Frontend UI/UX Standards Mandate
Whenever designing, building, modifying, or reviewing user interfaces, pages, components, forms, modals, or styling:
- **Strictly enforce the enterprise standards** defined in [.agents/skills/enterprise-ui-ux-standards/SKILL.md](.agents/skills/enterprise-ui-ux-standards/SKILL.md).
- **Accessibility (WCAG 2.2 AA)**: Ensure all interactive components have 4.5:1 contrast, visible focus rings, keyboard navigability, 44px+ touch targets, and proper ARIA labels.
- **Design Tokens**: Follow the 4pt/8pt spacing scale, semantic color palette, and relative unit typography scale.
- **Forms & Inputs**: Place explicit `<label>` tags above inputs; validate on blur/submit with constructive human-readable errors; preserve user input on failure.
- **State Handling**: Implement all 5 states (Empty, Loading, Error, Success, Disabled) for any async operations and data containers.
- **Domain Ethics**: Never use deceptive dark patterns in subscription pausing, resumption dates, or auto-debit amounts. Always provide clear, reversible confirmation for critical actions.

## 3. Habitual Changelog Tracking Mandate
Whenever creating, modifying, refactoring, or deleting any files or performing configuration/test updates:
- **Strictly follow the procedures** defined in [.agents/skills/changelog-tracking/SKILL.md](.agents/skills/changelog-tracking/SKILL.md).
- **Mandatory Log**: Document every change in [testing/changelogs.md](testing/changelogs.md) with:
  - Exact timestamp
  - Type of change (`Feature`, `Bugfix`, `Refactor`, `Config`, `Test`, `Documentation`, `Skill`)
  - Clear detection/summary of the changes made
  - Exact relative filepaths and their status (`[CREATED]`, `[MODIFIED]`, `[DELETED]`)
  - Verification/test results

## 4. Continuous Fullstack Unit Testing Mandate
Whenever modifying, enhancing, or adding code to Backend or Frontend:
- **Strictly follow the procedures** defined in [.agents/skills/fullstack-unit-testing/SKILL.md](.agents/skills/fullstack-unit-testing/SKILL.md).
- **Backend Unit Tests**: Execute `.\Backend\venv\Scripts\pytest.exe Backend/tests -v` and ensure all tests pass.
- **Frontend Unit Tests**: Execute `npm.cmd --prefix Frontend test` or `npm.cmd --prefix Frontend run test:run` and ensure all tests pass.
- Never conclude a task with broken tests, regressions, or unverified changes.
