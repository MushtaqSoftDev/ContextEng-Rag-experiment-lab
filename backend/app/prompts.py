"""Reasoning mode prompts for LLM."""

REASONING_MODES = {
    "direct": "",
    "chain_of_thought": (
        "You must think step by step. First analyze the question, "
        "then reason through each part, and finally provide a clear answer. "
    ),
    "atom_of_thought": (
        "Use atom-of-thought reasoning: break the problem into minimal atomic steps, "
        "solve each atom, then combine. Output your reasoning briefly before the final answer. "
    ),
}


def get_reasoning_prefix(mode: str) -> str:
    return REASONING_MODES.get((mode or "direct").lower(), "")
