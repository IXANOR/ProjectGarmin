# ADR-002: Frontend Framework

## Status
Accepted

## Context
We need a desktop GUI with a customizable chat interface, settings, and session management. The frontend should provide a modern and responsive user experience, while remaining lightweight for distribution.

## Decision
We will use **Tauri + React** for the frontend.

## Alternatives Considered
### Electron + React
- **Pros:** Large ecosystem, many tutorials.
- **Cons:** Heavy, large app size, high memory usage.

### Native Python GUIs (PyQt, Tkinter)
- **Pros:** No separate frontend tech stack needed.
- **Cons:** Outdated UI appearance, less flexible customization.

### Web-based SPA (React in browser)
- **Pros:** Easy to share via browser.
- **Cons:** Requires hosting, not fully offline by default.

## Consequences
**Positive:**
- Smaller app size than Electron.
- Better performance and lower memory usage.
- Full access to modern React ecosystem.

**Negative:**
- Requires Node.js and Rust toolchain for development.
- Slightly steeper setup for new contributors unfamiliar with Tauri.
