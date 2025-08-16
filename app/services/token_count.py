from __future__ import annotations


class TokenCounter:
    """Approximate token counting service.

    Heuristic: assume 1 token ~= 1.2 words for English-like text; use simple word splits.
    This is sufficient to enforce coarse budgets without a model-specific tokenizer.
    """

    @staticmethod
    def estimate_tokens(text: str) -> int:
        if not text:
            return 0
        words = text.split()
        # 1.2 words per token => tokens ~ words / 1.2
        return max(0, int(round(len(words) / 1.2)))


