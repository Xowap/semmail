import re
from os import getenv
from typing import Any, Optional

import jsonschema
import yaml

llm = getenv("SEMMAIL_LLM", "gemma")

if llm == "gemma":
    from .gemma import ask_gemma as ask
elif llm == "openai":
    from .openai import ask_closed_ai as ask
else:
    raise ImportError(f"LLM {llm} not available")


MD_START = re.compile(r"^```[^\n]*\n")
MD_END = re.compile(r"\n```$")


def parse_to_json(
    prompt: str, text: str, schema: Any, attempts: int = 3
) -> Optional[Any]:
    """
    This will ask AI and expect a JSON/YAML response. It will validate that
    we've got decent JSON and then validate the data structure against the
    provided JSON schema. If the output can't be parsed, the parsing will be
    attempted again within the configured limit.

    Parameters
    ----------
    prompt
        Prompt instructing the LLM how to reply
    text
        The text you want to parse
    schema
        The schema to validate the output
    attempts
        How many times to attempt getting a result
    """

    for _ in range(attempts):
        parsed_raw = ask(prompt, text)
        parsed_raw = MD_START.sub("", parsed_raw)
        parsed_raw = MD_END.sub("", parsed_raw)

        try:
            parsed = yaml.safe_load(parsed_raw)
            jsonschema.validate(parsed, schema)
        except (yaml.YAMLError, jsonschema.ValidationError):
            pass
        else:
            return parsed


__all__ = ["ask", "parse_to_json"]
