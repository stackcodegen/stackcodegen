import re
from typing import Any

from src.utils.code_block_parser import CodeBlockParser
from pprint import pprint


def strip_json_code_block(text: str) -> str:
    if text.strip().startswith("```"):
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    return text


# def strip_invalid_control_chars(s: str) -> str:
#     return re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", s)

def contains_bad_control_chars(text: str) -> bool:
    match = re.search(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", text)
    if match:
        print(f"[BAD CHAR] pos={match.start()}, char={repr(match.group())}, ord={ord(match.group())}")
        return True
    return False


def strip_outer_double_braces(text: str) -> str:
    stripped = text.strip()
    if re.fullmatch(r"\{\{.*\}\}", stripped, flags=re.DOTALL):
        return stripped[1:-1].strip()
    return stripped


def trim_messages(messages: list[dict], max_pairs: int = 1) -> list[dict]:
    """Keeps system prompt + last N user-assistant message pairs,
    optionally including a trailing user message if assistant hasn't replied yet."""

    print("current message length:", len(messages))

    system_messages = [m for m in messages if m["role"] == "system"]
    dialog_messages = [m for m in messages if m["role"] != "system"]

    # Check if the last message is from the user (incomplete pair)
    ends_with_user = dialog_messages and dialog_messages[-1]["role"] == "user"

    # Exclude that last user if it's incomplete, we'll add it back later
    if ends_with_user:
        dialog_body = dialog_messages[:-1]
        trailing_user = dialog_messages[-1]
    else:
        dialog_body = dialog_messages
        trailing_user = None

    # Collect last N user-assistant pairs
    pairs = []
    i = len(dialog_body) - 1
    while i > 0 and len(pairs) < max_pairs:
        if dialog_body[i]["role"] == "assistant" and dialog_body[i - 1]["role"] == "user":
            pairs.insert(0, dialog_body[i - 1])
            pairs.insert(1, dialog_body[i])
            i -= 2
        else:
            i -= 1

    # Add the final user message back (if assistant hasn't responded yet)
    if trailing_user:
        pairs.append(trailing_user)

    filtered_messages = system_messages + pairs
    print("filtered message length:", len(filtered_messages))
    return filtered_messages


def is_error(stderr: str) -> bool:
    if not stderr.strip():
        return False  # empty = no error

    # Full text match for warning keywords
    warning_only = re.fullmatch(
        r"(?s).*(RuntimeWarning|DeprecationWarning|UserWarning|FutureWarning|SettingWithCopyWarning).*",
        stderr.strip()
    )

    # Look for actual error markers
    has_fatal_error = re.search(r"(Traceback|Error|Exception)", stderr, re.IGNORECASE)

    # If there's a fatal error, treat it as error regardless of warnings
    return bool(has_fatal_error)


def summarize_docker_error(log: str, limit: int = 40) -> str:
    lines = log.strip().splitlines()
    if len(lines) <= limit:
        return "\n".join(lines)
    return "[...truncated...]\n" + "\n".join(lines[-limit:])


def select_best_answer(post):
    accepted_id = post.get("metadata", {}).get("accepted_answer_id")
    answers = post["answers"]

    if accepted_id:
        for a in answers:
            if a["answer_id"] == accepted_id:
                return a["body"]

    # Fallback: get the top-voted answer
    top_answer = max(answers, key=lambda a: a.get("score", 0))
    return top_answer["body"]


def clean_code_fields(obj: Any, fields: list[str]) -> Any:
    for attr in fields:
        if hasattr(obj, attr):
            raw = getattr(obj, attr)
            cleaned = CodeBlockParser.extract_code(raw)
            if cleaned:
                setattr(obj, attr, cleaned)
    return obj


def strip_invalid_control_chars(s: str) -> str:
    # Keep \n and \t, remove others like \x00-\x08, \x0b, \x0c, \x0e-\x1f
    return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', s)


def escape_raw_newlines_and_tabs(s: str) -> str:
    # Turn raw newlines into escaped ones
    return s.replace('\t', '\\t').replace('\n', '\\n')


def fix_smart_quotes(s: str) -> str:
    return s.replace("“", '"').replace("”", '"')


def fix_unescaped_inner_quotes(s: str) -> str:
    # Escape quotes inside string values that are likely to break JSON
    def repl(match):
        key, val = match.group(1), match.group(2)
        val_fixed = val.replace('"', r'\"')
        return f'"{key}": "{val_fixed}"'

    return re.sub(r'"(\w+)"\s*:\s*"([^"]*?"[^"]*?)"', repl, s)


def remove_trailing_commas(s: str) -> str:
    return re.sub(r',\s*([\]}])', r'\1', s)


def sanitize_llm_json(raw: str) -> str:
    s = raw.strip()
    s = fix_smart_quotes(s)
    s = strip_invalid_control_chars(s)
    s = escape_raw_newlines_and_tabs(s)
    s = fix_unescaped_inner_quotes(s)
    s = remove_trailing_commas(s)
    return s
