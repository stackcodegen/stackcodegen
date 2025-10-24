import json
from pprint import pprint

from pydantic import BaseModel, ValidationError
from typing import Type
from src.utils.helper import strip_json_code_block, strip_outer_double_braces, strip_invalid_control_chars, \
    contains_bad_control_chars, sanitize_llm_json
import re


class AssistantMessage(BaseModel):
    content: str


class LLMResponse(BaseModel):
    message: AssistantMessage
    token_usage: dict
    raw: dict

    def parse_json_as(self, schema_cls: Type[BaseModel]) -> BaseModel:
        print(self.message.content.strip())
        content = strip_json_code_block(self.message.content.strip())

        # Step 1: Try parsing as-is (valid JSON)
        try:
            return schema_cls.model_validate_json(content)
        except Exception:
            print("[DEBUG] Direct JSON parse failed. Attempting manual extraction...")
            pass

        # Step 2: Dynamic fallback using schema fields
        try:
            result = {}
            code_fields = {"buggy_code", "patched_code", "requirements"}  # Customize as needed

            for field_name, field in schema_cls.model_fields.items():
                # Build regex for each field
                # regex = rf'"{re.escape(field_name)}"\s*:\s*"([\s\S]*?)"'
                regex = rf'"{re.escape(field_name)}"\s*:\s*(?:"([\s\S]*?)"|([\w\.\-]+))'
                match = re.search(regex, content)

                if not match:
                    print(f"[DEBUG] Field '{field_name}' not found in fallback parse.")
                    continue

                value = match.group(1)

                if field_name in code_fields:
                    print(f"[DEBUG] Skipping sanitization for code field: {field_name}")
                    result[field_name] = value
                else:
                    # For non-code fields, clean control chars and escape double quotes
                    # value = re.sub(r"[\x00-\x1F\x7F]", "", value)
                    # value = value.replace('"', r'\"')
                    # result[field_name] = value.strip()

                    # Clean control characters and strip whitespace
                    value = re.sub(r"[\x00-\x1F\x7F]", "", value)
                    result[field_name] = value.strip()
            print("after cleaning\n", result)
            return schema_cls.model_validate(result)
        except Exception as e:
            raise ValueError(
                f"Manual schema-based parse failed.\nOriginal:\n{content}\n\nError:\n{e}"
            )
