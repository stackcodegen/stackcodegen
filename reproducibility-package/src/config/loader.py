from pathlib import Path
from omegaconf import OmegaConf


class ConfigLoader:
    def __init__(self, config_path: Path = None):
        self.root_dir = Path(__file__).resolve().parent.parent.parent  # adjust if needed
        if config_path is None:
            config_path = Path(__file__).resolve().parent.parent.parent / "configs" / "config.yaml"
        self.config_path = config_path
        self.config = OmegaConf.load(config_path)

    def get(self, key_path: str):
        return self.config.get(key_path)

    @property
    def default_model(self) -> str:
        return self.config.default_model

    @property
    def prompt_dir(self):
        return Path(__file__).resolve().parent.parent.parent / "src" / "prompts"

    @property
    def data_dir(self):
        return Path(__file__).resolve().parent.parent.parent / "dataset"

    @property
    def model_profiles(self):
        return self.config.models

    def get_model_config(self, model_name: str):
        return self.model_profiles[model_name]
