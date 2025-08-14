# ADR-004: Model Inference Approach

## Status
Accepted

## Context
We need to run `Jinx-gpt-oss-20b` locally on Windows/AMD with GPU acceleration. The method should be easy to install, support OpenAI API-compatible endpoints, and allow switching to other Hugging Face models in the future.

## Decision
We will start with **Ollama** for simplicity, with the option to switch to **Transformers (PyTorch ROCm)** for more control.

## Alternatives Considered
### LM Studio
- **Pros:** GUI for model management, easy API exposure.
- **Cons:** Less automation for custom integrations.

### Text-Generation-WebUI
- **Pros:** Many customization options, large community.
- **Cons:** More complex setup, heavier interface.

### vLLM
- **Pros:** High performance inference.
- **Cons:** Less straightforward on Windows/AMD.

## Consequences
**Positive:**
- Easy setup with Ollama.
- API compatible with OpenAI schema.
- Can later migrate to Transformers for advanced features.

**Negative:**
- Ollama may have fewer tuning options than direct Transformers usage.
- Windows/AMD support may require ROCm optimizations.
