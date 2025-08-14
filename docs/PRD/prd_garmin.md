# Product Requirement Document (PRD)
**Project:** Local Personal AI Assistant (“Garmin”)  
**Author:** Igor Podlecki
**Version:** 1.0  
**Date:** 2025-08-14

---

## 1. Purpose and Vision
The goal of this project is to create a desktop application powered by a local AI model, functioning as an interactive, personalized conversational assistant. The application should resemble a conversation with a real person — including the ability to adapt language (including profanity), tone, and personality to the user's preferences.  

The inspiration comes from **Jarvis from Iron Man** — the assistant will serve as a helper, remember conversation context, manage knowledge, analyze documents and files, and eventually be able to access the internet with the user's consent.  

**Priorities:**  
- Launching and operating the application should be as simple as possible.  
- The entire system runs fully **locally** (offline), with no external APIs.  
- The application should be flexible to allow swapping the model in the future.  

---

## 2. Project Scope

### 2.1. Functional Scope
1. **Local AI Model Support**
   - Default: `Jinx-gpt-oss-20b` from Hugging Face.
   - Ability to swap the model in settings to another compatible Hugging Face model.
   - Support for model parameters (temperature, max tokens, reasoning mode) with a simple UI.

2. **Chat Interface**
   - Session list on the left side (similar to ChatGPT).
   - Ability to name sessions (default: ID).
   - Different color/font settings globally and per session.
   - Conversation history stored locally with search functionality.
   - Option to manually remove or add information to the AI's memory.

3. **RAG (Retrieval-Augmented Generation)**
   - Uploading and analyzing PDFs, images, audio (preparation for video in the future).
   - File management inside the app (add/remove).
   - Search within files and use their content as chat context.

4. **Long-Term Memory and Context**
   - Automatic conversation shortening via summarization.
   - Saving facts in a database as knowledge for the model to recall.
   - User-controlled “knowledge” management.

5. **Settings**
   - Toggle “Allow AI to access the internet” (web search).
   - Simple GUI for configuring model parameters.
   - Theme, color, and font settings.

6. **Integrations and Extensions**
   - Plugin system (API for plugins) in the future.
   - Browser integration for web search.
   - Optional OS-level integration (e.g., keyboard shortcuts).

7. **Monitoring**
   - Real-time CPU/GPU/RAM usage indicators in the UI.

---

### 2.2. Non-Functional Scope
- **Target platform:** Windows 10/11 (desktop application).  
- **Backend:** Python + FastAPI (local server).  
- **Frontend:** Tauri + React (lightweight desktop app).  
- **Database:** SQLite (with option to migrate to Postgres).  
- **Model runs locally** — preferred tools: Ollama / Transformers / LM Studio API.  
- **Interface language:** initially Polish and English.  
- **Performance:** The app should run smoothly on the user's hardware, utilizing GPU (Radeon RX 7900 XT).  
- **License:** Open Source (MIT or Apache 2.0).  
- **Development Process** The project will be developed using Test Driven Development (TDD) methodology to ensure code quality, maintainability and confidence in functionality.

---

## 3. Target Users
- **Primary:** Yourself (as developer/tester).  
- **Secondary:** Potentially other AI enthusiasts looking for a local assistant, if the repo becomes public.

---

## 4. Technical Requirements
1. **Minimum hardware**:
   - GPU with at least 16 GB VRAM (target: RX 7900 XT).
   - RAM: at least 32 GB.
   - SSD storage for the model (~20–30 GB).
2. **Environment**:
   - Windows 10/11, Python 3.11+.
   - Node.js 20+ (for Tauri frontend).
3. **Dependencies**:
   - FastAPI, SQLModel, httpx, safetensors, transformers, sentence-transformers, PyTorch ROCm (for AMD).

---

## 5. MVP (Minimum Viable Product)
- Support for a single local model (`Jinx-gpt-oss-20b`).
- Basic chat with session list.
- Conversation history stored in SQLite.
- Simple RAG for PDFs.
- Model parameter settings.
- Simple dark/light theme.

---

## 6. Target Features (Post-MVP)
- Multi-model support (selectable in settings).
- RAG for images and audio.
- Advanced long-term memory with a knowledge base.
- Web search (enabled/disabled in settings).
- Plugins and integrations.
- Extensive per-session appearance customization.
- Real-time GPU/CPU/RAM usage indicators.
- Conversation summarization.

---

## 7. Risks and Challenges
- Performance of a large model on Windows/AMD (optimization required).
- RAG integration with multimedia (images, audio) requires additional models.
- Advanced long-term memory requires well-designed storage and retrieval.
- Maintaining simplicity while adding more features.

---

## 8. Success Criteria
- The application runs fully offline.
- The user can easily start a new session, return to old ones, and search history.
- The model responds fluently in a style tailored to the user’s preferences.
- Ability to upload PDFs and converse about their content.
- Simple, non-technical configuration of model parameters.
