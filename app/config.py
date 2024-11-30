import os
from dataclasses import dataclass
import yaml

from app.lib.utils import GB

CONFIG_ENV_NAME = 'FILE_MANAGER_CONFIG'
ERROR_MSG = "{param} is absent"
MAX_FILE_SIZE = 4  # GB


class MissingEnvironmentVariable(Exception):
    pass


@dataclass
class Config:
    port: int
    storage_dir: str
    log_path: str
    env_path: str
    db_config_path: str
    workers: int
    max_file_size: int
    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str
    max_body_size: int

    @classmethod
    def get_config(cls) -> dict:
        config_path = os.environ.get(CONFIG_ENV_NAME)
        if not config_path:
            raise MissingEnvironmentVariable(f"Environment variable {CONFIG_ENV_NAME} is not set")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"File {config_path} doesn't exist")
        with open(config_path) as conf_file:
            config = yaml.safe_load(conf_file)
        return config

    @classmethod
    def upload_config(cls) -> 'Config':
        config = cls.get_config()
        cls.validate(config)
        max_file_size = config.get('max_file_size', MAX_FILE_SIZE) * GB
        return Config(
            port=config['port'],
            storage_dir=config['storage_dir'],
            log_path=config['log_path'],
            env_path=config['env_path'],
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key=config['aws_secret_access_key'],
            endpoint_url=config['endpoint_url'],
            db_config_path=os.environ[CONFIG_ENV_NAME],
            workers=config.get('workers', 1),
            max_file_size=max_file_size,
            max_body_size=max_file_size + 1024
        )

    @classmethod
    def validate_one_param(cls, param: str, config: dict):
        if config.get(param) is None:
            raise KeyError(ERROR_MSG.format(param=param))

    @classmethod
    def validate(cls, config: dict):
        for param in ['port', 'storage_dir', 'log_path', 'env_path', 'aws_access_key_id', 'aws_secret_access_key', 'endpoint_url']:
            cls.validate_one_param(param, config)
        if 'max_file_size' in config and not isinstance(config['max_file_size'], int):
            raise ValueError("The max_file_size's type should be int")

