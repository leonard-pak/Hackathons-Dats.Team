import multiprocessing
import time
import json


class ConfigManager:
    def __init__(self, initial_config_file: str):
        self._manager = multiprocessing.Manager()
        self._config = self._manager.dict(
            self._load_config(initial_config_file))
        self._config_file = initial_config_file

    def get_config(self):
        return dict(self._config)

    def start_background_update(self, interval=5):
        process = multiprocessing.Process(
            target=self._config_updater, args=(self._config_file, interval))
        process.daemon = True
        process.start()

    def _load_config(self, path_to_config):
        with open(path_to_config, 'r') as file:
            return json.load(file)

    def _config_updater(self, path_to_config, interval):
        while True:
            self._config.update(self._load_config(path_to_config))
            time.sleep(interval)


# Example usage
if __name__ == "__main__":
    # Path to the initial configuration file
    config_file = 'configs/config.json'

    # Initialize ConfigManager with the configuration file
    config_manager = ConfigManager(config_file)

    # Start background update
    config_manager.start_background_update(3)

    # Read configuration
    while True:
        config = config_manager.get_config()
        print("Current Config:", config)
        time.sleep(5)
