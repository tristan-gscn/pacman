from src.models import Configuration
from src.models.errors import FileFormatError
import os
import re
import json

from typing import Any


class ConfigParser:
    """Parser for the application configuration file."""

    _COMMENT_PATTERNS = [
        r'//[^\n]*',        # C++ style single-line
        r'/\*[\s\S]*?\*/',  # C style block
        r'#[^\n]*',         # Shell style
    ]
    _COMMENT_RE = re.compile('|'.join(_COMMENT_PATTERNS))

    @staticmethod
    def parse(file_path: str) -> Configuration:
        """Parse a JSON configuration file.

        Args:
            file_path (str): Path to the JSON configuration file.

        Returns:
            Configuration: The parsed configuration object.

        Raises:
            FileFormatError: If the file is not a .json file.
            FileNotFoundError: If the file does not exist.
        """
        if not file_path.endswith('.json'):
            raise FileFormatError(
                'Your configuration file must finish by .json')
        if not os.path.exists(file_path):
            raise FileNotFoundError('Your file doesn\'t exist')
        with open(file_path, 'r') as f:
            raw = f.read()

        def reject_duplicates(
            ordered_pairs: list[tuple[str, Any]]
        ) -> dict[str, str | int | None]:
            d = {}
            for key, value in ordered_pairs:
                if key in d:
                    raise ValueError(f"Duplicate keyword detected in JSON: "
                                     f"'{key}'")
                d[key] = value
            return d

        cleaned = json.loads(
            ConfigParser._COMMENT_RE.sub('', raw),
            object_pairs_hook=reject_duplicates
        )

        return Configuration.model_validate(cleaned)
