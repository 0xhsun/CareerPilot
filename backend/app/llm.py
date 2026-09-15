"""Shared bits for talking to OpenAI-compatible chat endpoints."""

from .config import settings


def chat_extra() -> dict:
    """Extra kwargs for chat.completions.create().

    An unconstrained reasoning model can spend its whole max_completion_tokens
    budget on the thinking trace and come back with empty content, which the
    routers surface as a 502. Capping the effort keeps the budget for the answer.

    Sends nothing when REASONING_EFFORT is unset, since the official OpenAI API
    rejects the field.
    """
    effort = settings.REASONING_EFFORT.strip().lower()
    if not effort:
        return {}
    if effort == "none":
        return {"extra_body": {"reasoning": {"enabled": False}}}
    return {"extra_body": {"reasoning": {"effort": effort}}}
