from src.models import Configuration
from src.models.errors import FileFormatError
import os


class ConfigParser:
    """Parser for the application configuration file."""

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
            return Configuration.model_validate_json(f.read())
