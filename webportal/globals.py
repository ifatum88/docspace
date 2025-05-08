import yaml
import pathlib
import os

from core.utils import get_logger

LOCAL_MODE = True
CONFIG_DIR_PATH = "config"
CONFIG_FILE_NAME = "config.yaml"
LOCAL_CONFIG_FILE_NAME = "local.yaml"

class Config:
    def __init__(self, 
                 local_mode:bool, 
                 config_dir_path:str,
                 config_file_name:str,
                 local_config_file_name:str):
        self._local_mode = local_mode
        self._config_dir_path = config_dir_path
        self._config_file_name = config_file_name
        self._local_config_file_name = local_config_file_name
        self._current_dir = pathlib.Path(__file__).parent

        self._config_path = self.__get_config_path()
        self._data = self.__load()
        self._build_attributes()

    def __get_config_path(self):
        if LOCAL_MODE:
            return self._current_dir / self._config_dir_path / self._local_config_file_name
        else:
            return self._current_dir / self._config_dir_path / self._config_file_name
        
    def __load(self):
        with self._config_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _build_attributes(self):
        for key, value in self._data.items():
            setattr(self, key, value)  # оставляем значения словарями

    def as_dict(self):
        return self._data
        
class Globals:

    local_mode = LOCAL_MODE
    config_dir_path = CONFIG_DIR_PATH
    config_file_name = CONFIG_FILE_NAME
    local_config_file_name = LOCAL_CONFIG_FILE_NAME

    config = Config(local_mode, config_dir_path, config_file_name, local_config_file_name)
    logger = get_logger(
        name=config.app['name'], 
        log_dir=os.path.join(config.app['base_dir'], config.logs['dir'])
        )