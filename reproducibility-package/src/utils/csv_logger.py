import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import csv


class CsvTraceLogger:
    def __init__(self, base_dir: Path, tag: str = None, category: str = None, schema_path: Path = "./",
                 timestamp: str = None,
                 filename: str = None):
        self.timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
        if filename is None:
            filename = f"execution_trace_{self.timestamp}.csv"

        # self.csv_path = base_dir / "stack_overflow" / tag / category / "logs" / filename
        self.csv_path = base_dir / "stack_overflow" / "logs" / filename
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        self.columns = self._load_schema(schema_path)

    def _load_schema(self, schema_path: Path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def append_row(self, **kwargs):
        row = {}
        for col in self.columns:
            if col == "timestamp":
                row[col] = datetime.now().isoformat()
            else:
                row[col] = kwargs.get(col, "")

        df = pd.DataFrame([row])
        if self.csv_path.exists():
            df.to_csv(self.csv_path, mode="a", index=False, header=False, quoting=csv.QUOTE_ALL, lineterminator="\n",
                      encoding="utf-8")
        else:
            df.to_csv(self.csv_path, mode="w", index=False, header=True, quoting=csv.QUOTE_ALL, lineterminator="\n",
                      encoding="utf-8")
