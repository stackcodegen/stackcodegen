import re
from typing import Optional


class CodeBlockParser:
    MARKDOWN_RE = re.compile(r"```(?:[\w+-]*)?\n(.*?)```", re.DOTALL)
    HTML_CODE_RE = re.compile(r"<pre[^>]*><code[^>]*>(.*?)</code></pre>", re.DOTALL | re.IGNORECASE)
    HTML_SIMPLE_RE = re.compile(r"<code[^>]*>(.*?)</code>", re.DOTALL | re.IGNORECASE)

    @classmethod
    def extract_code(cls, text: str) -> Optional[str]:
        # Try Markdown
        md_match = cls.MARKDOWN_RE.search(text)
        if md_match:
            return md_match.group(1).strip()

        # Try <pre><code>...</code></pre>
        pre_code_match = cls.HTML_CODE_RE.search(text)
        if pre_code_match:
            return cls._unescape_html(pre_code_match.group(1).strip())

        # Try simple <code>...</code>
        code_match = cls.HTML_SIMPLE_RE.search(text)
        if code_match:
            return cls._unescape_html(code_match.group(1).strip())

        return None  # No code found

    @staticmethod
    def _unescape_html(text: str) -> str:
        import html
        return html.unescape(text)