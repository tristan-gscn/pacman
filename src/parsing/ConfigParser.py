from src.models import Configuration
from src.models.errors import FileFormatError
import os


class ConfigParser():

    @staticmethod
    def parse(file_path: str) -> Configuration:
        if not file_path.endswith('.json'):
            raise FileFormatError(
                'Your configuration file must finish by .json')
        if not os.path.exists(file_path):
            raise FileNotFoundError('Your file doesn\'t exist')
        with open(file_path, 'r') as f:
            return Configuration.model_validate_json(f.read())
            
