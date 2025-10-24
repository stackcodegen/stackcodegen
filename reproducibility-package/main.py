import traceback
from datetime import datetime
from pathlib import Path
import time
from time import sleep

from dotenv import load_dotenv
import pandas as pd
from src.config.loader import ConfigLoader
from src.llm.factory import ModelFactory
from src.pipeline.buggy_code_generation_pipeline import BuggyCodeGenerationPipeline
from src.pipeline.patched_code_generation_pipeline import PatchedCodeGenerationPipeline
from src.utils.csv_logger import CsvTraceLogger

load_dotenv()
cfg = ConfigLoader()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

data_path = "./dataset/motivating_example.csv"
dataset = pd.read_csv(data_path)

generator_model_name = cfg.get("generator_llm")
generator_llm = ModelFactory(cfg, model_name=generator_model_name).get_model_client()

judge_llm_name = cfg.get("judge_llm")
judge_llm = ModelFactory(cfg, model_name=judge_llm_name).get_model_client()

# logging
output_path = cfg.root_dir / f"outputs/{timestamp}"

buggy_code_intent_logger = CsvTraceLogger(
    Path(output_path),
    timestamp=timestamp,
    schema_path=cfg.root_dir / Path("src/csv_schema/judge/judge_buggy_code_intent_csv_schema.json"),
    filename=f"buggy_code_intent_judged_{generator_model_name}_{judge_llm_name}_{timestamp}.csv"
)

buggy_functional_requirements_logger = CsvTraceLogger(
    Path(output_path),
    timestamp=timestamp,
    schema_path=cfg.root_dir / Path("src/csv_schema/judge/judge_buggy_functional_requirements_csv_schema.json"),
    filename=f"buggy_functional_requirements_judged_{generator_model_name}_{judge_llm_name}_{timestamp}.csv"
)

buggy_scot_logger = CsvTraceLogger(
    Path(output_path),
    timestamp=timestamp,
    schema_path=cfg.root_dir / Path("src/csv_schema/judge/judge_buggy_scot_csv_schema.json"),
    filename=f"buggy_scot_judged_{generator_model_name}_{judge_llm_name}_{timestamp}.csv"
)

# todo: check usage and handle accordingly
buggy_code_logger = CsvTraceLogger(
    Path(output_path),
    timestamp=timestamp,
    schema_path=cfg.root_dir / Path("src/csv_schema/judge/judge_buggy_code_csv_schema.json"),
    filename=f"buggy_code_judged_{generator_model_name}_{judge_llm_name}_{timestamp}.csv"
)

patched_code_intent_logger = CsvTraceLogger(
    Path(output_path),
    timestamp=timestamp,
    schema_path=cfg.root_dir / Path("src/csv_schema/judge/judge_patched_code_intent_csv_schema.json"),
    filename=f"patched_code_intent_judged_{generator_model_name}_{judge_llm_name}_{timestamp}.csv"
)

patched_functional_requirements_logger = CsvTraceLogger(
    Path(output_path),
    timestamp=timestamp,
    schema_path=cfg.root_dir / Path("src/csv_schema/judge/judge_patched_functional_requirements_csv_schema.json"),
    filename=f"patched_functional_requirements_judged_{generator_model_name}_{judge_llm_name}_{timestamp}.csv"
)

patched_scot_logger = CsvTraceLogger(
    Path(output_path),
    timestamp=timestamp,
    schema_path=cfg.root_dir / Path("src/csv_schema/judge/judge_patched_scot_csv_schema.json"),
    filename=f"patched_scot_judged_{generator_model_name}_{judge_llm_name}_{timestamp}.csv"
)

# todo: check usage and handle accordingly
patched_code_logger = CsvTraceLogger(
    Path(output_path),
    timestamp=timestamp,
    schema_path=cfg.root_dir / Path("src/csv_schema/judge/judge_patched_code_csv_schema.json"),
    filename=f"patched_code_judged_{generator_model_name}_{judge_llm_name}_{timestamp}.csv"
)

time_logger = CsvTraceLogger(
    Path(output_path),
    timestamp=timestamp,
    schema_path=cfg.root_dir / Path("src/csv_schema/other/time_log_csv_schema.json"),
    filename=f"post_exec_time_{generator_model_name}_{judge_llm_name}_{timestamp}.csv"
)

loggers = {
    "buggy_code_intent_logger": buggy_code_intent_logger,
    "buggy_functional_requirements_logger": buggy_functional_requirements_logger,
    "buggy_scot_logger": buggy_scot_logger,
    "buggy_code_logger": buggy_code_logger,
    "patched_code_intent_logger": patched_code_intent_logger,
    "patched_functional_requirements_logger": patched_functional_requirements_logger,
    "patched_scot_logger": patched_scot_logger,
    "patched_code_logger": patched_code_logger,
}
try:
    buggy_code_generator_pipeline = BuggyCodeGenerationPipeline(generator_llm, judge_llm, loggers)
    patched_code_generator_pipeline = PatchedCodeGenerationPipeline(generator_llm, judge_llm, loggers)

    for i, (idx, post) in enumerate(dataset.iterrows()):
        try:
            print("=" * 50)
            question_id = post["question_id"]
            print(f"[{generator_model_name}][{idx + 1}/{len(dataset)}] Starting {question_id}...")
            start_time = time.time()
            buggy_code_generation, buggy_code_judgement = buggy_code_generator_pipeline.run(post)
            if isinstance(buggy_code_judgement, dict):
                buggy_code_label = buggy_code_judgement.get("label", "").lower()
            else:
                buggy_code_label = buggy_code_judgement.label.lower()

            if buggy_code_label != "correct":
                continue

            post['buggy_code'] = buggy_code_generation.buggy_code

            patched_code_generation, patched_code_judgement = patched_code_generator_pipeline.run(post)

        except Exception as e:
            print("error:", str(e))
            traceback.print_exc()
            continue
        finally:
            # Always log time, even if skipped or failed
            end_time = time.time()
            elapsed = round(end_time - start_time, 2)
            time_logger.append_row(
                question_id=question_id,
                exec_time=elapsed,
            )
            print(f"[Post {question_id}] Time taken: {elapsed} seconds")
except Exception as e:
    print("error:", str(e))
    traceback.print_exc()

