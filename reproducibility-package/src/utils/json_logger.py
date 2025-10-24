from pathlib import Path
import json


class JsonTraceLogger:
    def __init__(self, base_dir: Path, tag: str, category: str):
        self.raw_dir = base_dir / "stack_overflow" / tag / category / "raw_response"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def save_versioned(self, question_id: str, data: dict) -> Path:
        post_dir = self.raw_dir / str(question_id)
        post_dir.mkdir(parents=True, exist_ok=True)

        existing_versions = list(post_dir.glob("*.json"))
        version_nums = [int(p.stem[1:]) for p in existing_versions if p.stem[1:].isdigit()]
        next_version = max(version_nums, default=0) + 1
        path = post_dir / f"v{next_version}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path
