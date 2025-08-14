# Task XXX: [Clear, actionable title]

## Questions for Stakeholder/Owner
[List questions that need to be answered before starting the task. If the answer is "don't know", propose a recommendation.]

## Overview
[Expanded section with 3-4 sentences that clearly explains:]
- **What** this task accomplishes and its purpose in the overall system
- **Why** this is needed and how it connects to other components
- **Scope** - what is included and what is NOT included in this task
- **Key challenge** or complexity that needs to be solved

## Task Type
- [ ] **Setup/Infrastructure** - Project setup, tooling, configuration
- [ ] **Backend** - API, business logic, data handling (requires TDD)
- [ ] **Frontend** - UI components, user interactions
- [ ] **Integration** - Connecting frontend to backend
- [ ] **Documentation** - User guides, API docs, README updates

## Acceptance Criteria
### Core Functionality
- [ ] **Feature 1**: Specific, testable behavior with concrete example of what works
- [ ] **Feature 2**: Another measurable outcome with clear success criteria
- [ ] **Error Handling**: How errors are handled and what user/system sees

### Integration & Quality
- [ ] **Integration**: How this connects to existing/future components
- [ ] **Code Quality**: Code follows project conventions and is properly documented
- [ ] **Testing**: (Backend tasks) Tests written first (TDD), all tests pass
- [ ] **Performance**: Any specific performance requirements or considerations

## Backend Requirements (if applicable)
- [ ] **Tests First**: Write failing tests before implementation
- [ ] **TDD Notes**: List specific unit/integration tests to write before coding, with minimal coverage goals
- [ ] **API Design**: RESTful endpoints with proper HTTP methods and status codes
- [ ] **Data Validation**: Input validation with clear error messages
- [ ] **Error Handling**: Proper exception handling and logging
- [ ] **Documentation**: API endpoints documented (can be filled after completion)

## Frontend Requirements (if applicable)
- [ ] **Tests First**: Write failing tests before implementation
- [ ] **TDD Notes**: List specific UI/component tests to write before coding, with minimal coverage goals
- [ ] **Component Design**: Reusable, well-structured components
- [ ] **UI/UX**: Follows design system and is accessible
- [ ] **State Management**: Proper state handling and data flow
- [ ] **API Integration**: Correctly calls backend APIs with error handling
- [ ] **Responsive**: Works on different screen sizes

## Expected Outcomes
[What should exist after this task is complete:]
- **For the user**: What new capability or improvement they will see
- **For the system**: What new functionality is available for other components to use
- **For developers**: What foundation is laid for future tasks
- **For QA**: Manual steps to verify this task's success

## Document References
- Related PRD sections: [Link to specific sections that drive this task]
- Related ADRs: [Link to architectural decisions that influence this task]
- Related Roadmap item: [Link to roadmap phase/task]
- Dependencies: [Other tasks that must be completed first - be specific about what you need from them]

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: List of actual files with brief purpose
- **Key Technical Decisions**: Important choices made during implementation
- **API Endpoints**: Specific endpoints implemented (for backend tasks)
- **Components Created**: Main components built (for frontend tasks)
- **Challenges & Solutions**: Any significant problems encountered and how they were solved
- **Notes for Future Tasks**: Important information that affects dependent tasks
