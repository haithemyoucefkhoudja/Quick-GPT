import re
from typing import Any, Dict


def parse_config(config_text: str) -> Dict[str:Any]:
    """Parses the configuration text and extracts relevant information.

    Args:
        config_text: The configuration script text.

    Returns:
        A dictionary containing the extracted information.
    """

    result = {}
    current_section = None

    for line in config_text.splitlines():
        line = line.strip()

        # Check for section headers
        current_section = line[1:-1]

        # Skip if no current section
        if not current_section:
            continue
        _SPECIAL_INDICATOR = current_section.split(' ', 1)[0]
        section = current_section[len(_SPECIAL_INDICATOR) + 1:]
        result[_SPECIAL_INDICATOR] = {}
        Pairs = re.findall(r"(.+?)='(.+?)'", section)
        if Pairs:
            for pair in Pairs:
                key, value = pair
                result[_SPECIAL_INDICATOR][key] = value

    return result
