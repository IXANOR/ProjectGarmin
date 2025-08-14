# ADR-001: Backend Architecture

## Status
Accepted

## Context
We need a local backend to handle AI model API requests, manage chat sessions, process RAG data, and interact with the database. The backend must be lightweight, fast to start, and easy to integrate with machine learning libraries, while supporting asynchronous communication for streaming model responses.

## Decision
We will use **Python + FastAPI** for the backend.

## Alternatives Considered
### Flask
- **Pros:** Simple, popular, easy to learn.
- **Cons:** No native async support, less suited for streaming responses.

### Django
- **Pros:** Full-featured, includes ORM, admin panel, and authentication.
- **Cons:** Heavy for our use case, unnecessary complexity for an MVP.

### Node.js + Express
- **Pros:** Popular for web services, non-blocking I/O.
- **Cons:** Less direct integration with Python ML stack, requires inter-process communication.

## Consequences
**Positive:**
- Asynchronous support for streaming AI responses.
- Tight integration with Python ML libraries.
- Easy to develop, test, and deploy locally.

**Negative:**
- Smaller ecosystem compared to Node.js for frontend-related tooling.
- Requires Python runtime installation for end-users.
