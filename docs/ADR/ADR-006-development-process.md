# ADR-006: Development Process – Test Driven Development (TDD)

## Status
Accepted

## Context
We want to ensure high code quality, maintainability, and confidence in functionality throughout the development of the Local Personal AI Assistant ("Garmin").  
Given the complexity of integrating a backend, frontend, AI model inference, and RAG, we need a disciplined approach that reduces the risk of regressions and promotes clean architecture.

## Decision
We will adopt **Test Driven Development (TDD)** as the primary development methodology.

**TDD Workflow:**
1. Write a failing test for the next piece of functionality.
2. Implement the minimal code needed to make the test pass.
3. Refactor the code while keeping the test passing.
4. Repeat for each new feature or bug fix.

**Testing Frameworks:**
- **Backend (Python/FastAPI):** `pytest` + `httpx` for API tests.
- **Frontend (Tauri + React):** `vitest` + `react-testing-library`.
- **Integration Tests:** May use `Playwright` or `Cypress` for end-to-end testing.

## Alternatives Considered
### No formal testing process
- **Pros:** Faster initial coding.
- **Cons:** Higher risk of defects, fragile codebase.

### Write tests after implementation
- **Pros:** Easier for quick prototypes.
- **Cons:** Tests may be incomplete, less guidance for architecture.

## Consequences
**Positive:**
- Ensures every feature is backed by tests.
- Facilitates safe refactoring.
- Improves long-term maintainability.

**Negative:**
- Slower initial development pace.
- Requires discipline to maintain the process.

## Notes
This decision applies to **all components** of the project – backend, frontend, and any auxiliary tools or scripts.
