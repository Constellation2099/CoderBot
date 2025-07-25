# utils.py

def strip_code_fence(code: str) -> str:
    """
    Strips markdown-style code fences if present.
    Example: ```python\n<code>\n``` → <code>
    """
    if code.startswith("```"):
        code = code.strip("`").strip()
        if code.startswith("python"):
            code = code[len("python"):].strip()
    return code