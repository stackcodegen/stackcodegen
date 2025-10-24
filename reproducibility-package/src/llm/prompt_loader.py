from pathlib import Path
import yaml

class PromptLoader:
    def __init__(self, prompt_dir: Path):
        self.prompt_dir = Path(prompt_dir).resolve()

    def load(self, relative_path: str) -> dict:
        path = self.prompt_dir / relative_path
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)