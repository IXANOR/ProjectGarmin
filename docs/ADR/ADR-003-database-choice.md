# ADR-003: Database Choice

## Status
Accepted

## Context
We need local storage for chat history, user settings, and RAG-related data. The solution should be simple to set up for a single-user local app but allow migration to more robust storage if needed.

## Decision
We will use **SQLite** for the MVP, with the option to migrate to PostgreSQL later.

## Alternatives Considered
### PostgreSQL from start
- **Pros:** Scalable, powerful features.
- **Cons:** Requires installation and service management, overkill for MVP.

### MongoDB
- **Pros:** Flexible document storage.
- **Cons:** Requires extra service, less optimal for relational data.

### Local JSON storage
- **Pros:** Easiest to set up.
- **Cons:** Poor performance with larger datasets, lacks query capabilities.

## Consequences
**Positive:**
- No external dependencies for MVP.
- Well-supported in Python via SQLAlchemy/SQLModel.
- Good performance for small-to-medium datasets.

**Negative:**
- Not ideal for large-scale multi-user setups.
- Migration needed if scaling beyond MVP requirements.
