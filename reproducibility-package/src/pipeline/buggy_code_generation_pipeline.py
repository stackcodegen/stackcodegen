import subprocess
from datetime import datetime

from src.agents.buggy_code_generator import BuggyCodeGeneratorAgent
from src.agents.buggy_thought_generator import BuggyThoughtGeneratorAgent
from src.agents.judge.judge import JudgeAgent
from src.config.loader import ConfigLoader
from src.llm.base import LLMClient
from pprint import pprint
from src.pipeline.buggy_thought_pipeline import BuggyThoughtGeneratorPipeline
from src.utils.helper import clean_code_fields, is_error, summarize_docker_error
from src.validator.docker_validator import DockerValidator


class BuggyCodeGenerationPipeline:
    # todo: use logger
    def __init__(self, generator_llm: LLMClient, judge_llm: LLMClient,
                 loggers: dict = None, posts=None):
        cfg = ConfigLoader()
        self.posts = posts
        self.thought_agent = BuggyThoughtGeneratorAgent(generator_llm)
        self.thought_pipeline = BuggyThoughtGeneratorPipeline(generator_llm, judge_llm, loggers, posts)
        self.judge_agent = JudgeAgent(judge_llm)
        self.code_agent = BuggyCodeGeneratorAgent(generator_llm)
        self.loggers = loggers
        self.docker_template_path = cfg.root_dir / "src/utils/docker_template/Dockerfile.template"
        self.validator = DockerValidator(self.docker_template_path)

    def run(self, post):
        question_id = post['question_id']
        print(f"Evaluating question id: {question_id}")
        guidance = self.thought_pipeline.run(post)
        buggy_code, buggy_code_judgement = self.generate_and_evaluate_buggy_code(post, guidance)
        return buggy_code, buggy_code_judgement

    def generate_and_evaluate_buggy_code(self, post: dict, guidance, max_exec_iter=3, max_review_iter=3):
        question_id = post["question_id"]
        question = post["question"]

        generation_start_time = datetime.now()
        messages, parsed, gen_token_usage = self.code_agent.generate_buggy_code(question, guidance)
        generation_end_time = datetime.now()
        generation_duration = generation_end_time - generation_start_time

        clean_code_fields(parsed, ["buggy_code"])

        validation_result = None
        review_result = None

        exec_iter, review_iter = 0, 0
        phase = "execution"
        docker_error_msg = ""

        while exec_iter < max_exec_iter or review_iter < max_review_iter:
            print(f"[DEBUG] [BUGGY CODE] exec_iter={exec_iter}, review_iter={review_iter}, phase={phase}")
            # print(f"\n[ITERATION {exec_iter + review_iter + 1}] Phase: {phase}")

            if phase == "execution" and exec_iter < max_exec_iter:
                docker_error_msg = ""
                try:
                    validation_result = self.validator.validate(
                        script=parsed.buggy_code,
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
                        "stderr": "",
                        "exit_code": -1,
                    }
                self.loggers["buggy_code_logger"].append_row(
                    question_id=question_id,
                    question=question,
                    buggy_code_intent=guidance["buggy_code_intent"],
                    buggy_functional_requirements=guidance["buggy_functional_requirements"],
                    buggy_scot=guidance["buggy_scot"],
                    buggy_code=parsed.buggy_code,
                    stdout=validation_result.get("stdout", ""),
                    judge_buggy_code_label="not_reviewed",
                    judge_buggy_code_rational="execution phase only",
                    requirements=parsed.requirements,
                    stderr=validation_result.get("stderr", ""),
                    error=docker_error_msg,
                    exec_iteration=exec_iter + 1,
                    review_iteration=review_iter,
                    exit_code=validation_result.get("returncode", -1),
                    generation_token_usage=gen_token_usage,
                    generation_duration=round(generation_duration.total_seconds(), 2),
                    # evluation_duration=round(evaluation_duration.total_seconds(), 2),
                )
                generation_start_time = datetime.now()
                messages, parsed, gen_token_usage = self.code_agent.refine_buggy_code(messages, {
                    "requirements": parsed.requirements,
                    "buggy_code": parsed.buggy_code,
                    "buggy_stderr": validation_result.get("stderr", "") if validation_result else "",
                    "docker_error": docker_error_msg or "No docker error"
                })
                generation_end_time = datetime.now()
                generation_duration = generation_end_time - generation_start_time

                clean_code_fields(parsed, ["buggy_code"])
                exec_iter += 1 # one-exec-refinement block

            elif phase == "review" and review_iter < max_review_iter:
                evaluation_start_time = datetime.now()
                review_result, review_token_usage = self.judge_agent.evaluate_buggy_code(question, parsed.buggy_code)
                evaluation_end_time = datetime.now()
                evaluation_duration = evaluation_end_time - evaluation_start_time

                print(f"[JUDGE] label: {review_result.label}, rationale: {review_result.rationale}")
                self.loggers["buggy_code_logger"].append_row(
                    question_id=question_id,
                    question=question,
                    buggy_code_intent=guidance["buggy_code_intent"],
                    buggy_functional_requirements=guidance["buggy_functional_requirements"],
                    buggy_scot=guidance["buggy_scot"],
                    buggy_code=parsed.buggy_code,
                    stdout=validation_result.get("stdout", "") if validation_result else "",
                    judge_buggy_code_label=review_result.label,
                    judge_buggy_code_rational=review_result.rationale,
                    requirements=parsed.requirements,
                    stderr=validation_result.get("stderr", "") if validation_result else "",
                    error=docker_error_msg,
                    exec_iteration=exec_iter,
                    review_iteration=review_iter + 1,
                    exit_code=validation_result.get("returncode", -1) if validation_result else -1,
                    generation_token_usage=gen_token_usage,
                    review_token_usage=review_token_usage,
                    generation_duration=round(generation_duration.total_seconds(), 2),
                    evaluation_duration=round(evaluation_duration.total_seconds(), 2),
                )
                if review_result.label.lower() == "correct":
                    print(f"[INFO] Review passed on iteration {review_iter + 1}")
                    break
                print(f"[FAIL] Review failed. Refining buggy code.")

                generation_start_time = datetime.now()
                messages, parsed, gen_token_usage = self.code_agent.refine_buggy_code_reviewed(messages, review_result)
                generation_end_time = datetime.now()
                generation_duration = generation_end_time - generation_start_time

                clean_code_fields(parsed, ["buggy_code"])
                review_iter += 1
                if review_iter >= max_review_iter:
                    print("[INFO] Review limit reached. Stopping.")
                    break

                if exec_iter >= max_exec_iter:
                    print("[INFO] Execution limit reached after review. Stopping.")
                    break

                phase = "execution"
                review_result = None
                validation_result = None
            else:
                print("[WARN] No valid phase to execute, terminating loop.")
                break

        if review_result:
            return parsed, review_result
        else:
            return parsed, {"label": "incorrect", "rationale": "Code did not execute successfully."}
