# Role: Process Coordinator
# logger should be here!?
import json
import subprocess
from datetime import datetime
from typing import List

from src.agents.buggy_code_generator import BuggyCodeGeneratorAgent
from src.agents.buggy_thought_generator import BuggyThoughtGeneratorAgent
from src.agents.judge.judge import JudgeAgent
from src.agents.patched_code_generator import PatchedCodeGeneratorAgent
from src.agents.patched_thought_generator import PatchedThoughtGeneratorAgent
from src.config.loader import ConfigLoader
from src.llm.base import LLMClient
from src.llm.prompt_loader import PromptLoader
from pprint import pprint
from pprint import pprint

from src.pipeline.buggy_thought_pipeline import BuggyThoughtGeneratorPipeline
from src.pipeline.patched_thought_pipeline import PatchedThoughtGeneratorPipeline
from src.utils.helper import clean_code_fields, is_error, summarize_docker_error
from src.validator.docker_validator import DockerValidator


class PatchedCodeGenerationPipeline:
    # todo: use logger
    def __init__(self, generator_llm: LLMClient, judge_llm: LLMClient,
                 loggers: dict, posts=None):
        cfg = ConfigLoader()
        self.posts = posts
        self.loggers = loggers
        self.thought_agent = PatchedThoughtGeneratorAgent(generator_llm)
        self.judge_agent = JudgeAgent(judge_llm)
        self.code_agent = PatchedCodeGeneratorAgent(generator_llm)
        self.thought_pipeline = PatchedThoughtGeneratorPipeline(generator_llm, judge_llm, loggers, posts)
        self.docker_template_path = cfg.root_dir / "src/utils/docker_template/Dockerfile.template"
        self.validator = DockerValidator(self.docker_template_path)

    def run(self, post):
        question_id = post['question_id']
        print(f"Evaluating question id: {question_id}")
        guidance = self.thought_pipeline.run(post)
        patched_code, patched_code_judgement = self.generate_and_evaluate_patched_code(post, guidance)
        return patched_code, patched_code_judgement

    def generate_and_evaluate_patched_code(self, post: dict, guidance, max_exec_iter=3, max_review_iter=3):
        question_id = post["question_id"]
        buggy_code = post["buggy_code"]
        question = post["question"]
        answer = post["answer"]

        generation_start_time = datetime.now()
        messages, parsed, gen_token_usage = self.code_agent.generate_patched_code(buggy_code, guidance)
        generation_end_time = datetime.now()
        generation_duration = generation_end_time - generation_start_time

        clean_code_fields(parsed, ["patched_code"])

        validation_result = None
        review_result = None

        exec_iter, review_iter = 0, 0
        phase = "execution"
        docker_error_msg = ""

        while exec_iter < max_exec_iter or review_iter < max_review_iter:
            print(f"[DEBUG] [PATCHED CODE] exec_iter={exec_iter}, review_iter={review_iter}, phase={phase}")
            # print(f"\n[ITERATION {exec_iter + review_iter + 1}] Phase: {phase}")

            if phase == "execution" and exec_iter < max_exec_iter:
                docker_error_msg = ""
                try:
                    validation_result = self.validator.validate(
                        script=parsed.patched_code,
                        requirements=parsed.requirements,
                    )
                    print("Validation result:")
                    pprint(validation_result)

                    passed = not is_error(validation_result["stderr"])
                    if passed:
                        print(f"[INFO] passed on iteration: {exec_iter + 1}")
                        phase = "review"
                        continue
                    else:
                        print(f"[FAIL] Execution failed. Refining...")

                except (subprocess.CalledProcessError, RuntimeError) as e:
                    docker_error_msg = summarize_docker_error(str(e))
                    print(f"[ERROR] Docker validation failed: {docker_error_msg}")
                    validation_result = {
                        "stdout": "",
                        "stderr": docker_error_msg,
                        "exit_code": -1,
                    }
                self.loggers["patched_code_logger"].append_row(
                    question_id=question_id,
                    question=post["question"],
                    answer=post["answer"],
                    buggy_code=post["buggy_code"],
                    patched_code_intent=guidance['patched_code_intent'],
                    patched_functional_requirements=guidance['patched_functional_requirements'],
                    patched_scot=guidance['patched_scot'],
                    patched_code=parsed.patched_code,
                    stdout=validation_result.get("stdout", ""),
                    judge_patched_code_label="not_reviewed",
                    judge_patched_code_rational="execution phase only",
                    requirements=parsed.requirements,
                    stderr=validation_result.get("stderr", ""),
                    error=docker_error_msg,
                    exec_iteration=exec_iter + 1,
                    review_iteration=review_iter,
                    exit_code=validation_result.get("returncode", -1),
                    generation_token_usage=gen_token_usage,
                    generation_duration=round(generation_duration.total_seconds(), 2),
                    # evaluation_duration=round(evaluation_duration.total_seconds(), 2),
                )
                # Only refine if failed or exception occurred
                generation_start_time = datetime.now()
                messages, parsed, gen_token_usage = self.code_agent.refine_patched_code(messages, {
                    "requirements": parsed.requirements,
                    "patched_code": parsed.patched_code,
                    "stderr": validation_result.get("stderr", "") if validation_result else "",
                    "docker_error": docker_error_msg or "No docker error"
                })
                generation_end_time = datetime.now()
                generation_duration = generation_end_time - generation_start_time

                clean_code_fields(parsed, ["patched_code"])
                exec_iter += 1  # one-exec-refinement block

            elif phase == "review" and review_iter < max_review_iter:
                evaluation_start_time = datetime.now()
                review_result, review_token_usage = self.judge_agent.evaluate_patched_code(question, answer,
                                                                                           parsed.patched_code)
                evaluation_end_time = datetime.now()
                evaluation_duration = evaluation_end_time - evaluation_start_time

                print(f"[JUDGE] label: {review_result.label}, rationale: {review_result.rationale}")
                self.loggers["patched_code_logger"].append_row(
                    question_id=question_id,
                    question=question,
                    answer=post["answer"],
                    buggy_code=post["buggy_code"],
                    patched_code_intent=guidance['patched_code_intent'],
                    patched_functional_requirements=guidance['patched_functional_requirements'],
                    patched_scot=guidance['patched_scot'],
                    patched_code=parsed.patched_code,
                    stdout=validation_result.get("stdout", "") if validation_result else "",
                    judge_patched_code_label=review_result.label,
                    judge_patched_code_rational=review_result.rationale,
                    requirements=parsed.requirements,
                    stderr=validation_result.get("stderr", "") if validation_result else "",
                    exit_code=validation_result.get("returncode", -1) if validation_result else -1,
                    exec_iteration=exec_iter,
                    review_iteration=review_iter + 1,
                    generation_token_usage=gen_token_usage,
                    review_token_usage=review_token_usage,
                    generation_duration=round(generation_duration.total_seconds(), 2),
                    evaluation_duration=round(evaluation_duration.total_seconds(), 2),
                )
                if review_result.label.lower() == "correct":
                    print(f"[INFO] Review passed on iteration {review_iter + 1}")
                    break

                print(f"[FAIL] Review failed. Refining patched code.")

                generation_start_time = datetime.now()
                messages, parsed, gen_token_usage = self.code_agent.refine_patched_code_reviewed(messages,
                                                                                                 review_result)
                generation_end_time = datetime.now()
                generation_duration = generation_end_time - generation_start_time

                clean_code_fields(parsed, ["patched_code"])
                review_iter += 1
                if review_iter >= max_review_iter:
                    print("[INFO] Review limit reached. Stopping.")
                    break

                if exec_iter >= max_exec_iter:
                    print("[INFO] Execution limit reached after review. Stopping.")
                    break

                phase = "execution"
                validation_result = None
                review_result = None
            else:
                print("[WARN] No valid phase to execute, terminating loop.")
                break

        if review_result:
            return parsed, {"label": review_result.label, "rationale": review_result.rationale}
        else:
            return parsed, {"label": "incorrect", "rationale": "Code did not execute successfully."}
