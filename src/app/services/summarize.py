import re


def one_sentence(text: str, max_len: int = 180) -> str:
    text = (text or "").strip()
    if not text:
        return "No description available"

    parts = re.split(r"(?<=[.!?])\s+", text)
    first = parts[0].strip() if parts else text

    if len(first) <= max_len:
        return first

    return first[: max_len - 1].rstrip() + "…"

