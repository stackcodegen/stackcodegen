from datetime import datetime
from typing import List
from src.agents.buggy_thought_generator import BuggyThoughtGeneratorAgent
from src.agents.judge.judge import JudgeAgent
from src.llm.base import LLMClient


class BuggyThoughtGeneratorPipeline:
    def __init__(self, llm: LLMClient, judge_llm: LLMClient, loggers: dict, posts: List[dict] = None, ):
        self.posts = posts
        self.agent = BuggyThoughtGeneratorAgent(llm)
        self.judge_agent = JudgeAgent(judge_llm)
        self.loggers = loggers

    def run(self, post):
        buggy_code_intent, buggy_code_intent_result = self.generate_and_evaluate_buggy_code_intent(post)
        buggy_functional_requirements, buggy_functional_requirements_result = self.generate_and_evaluate_buggy_functional_requirements(
            post)
        buggy_scot, buggy_scot_result = self.generate_and_evaluate_buggy_scot(post)

        guidance = {
            "question_id": post["question_id"],
            "buggy_code_intent": buggy_code_intent,
            "buggy_code_intent_judgment": buggy_code_intent_result,
            "buggy_functional_requirements": buggy_functional_requirements,
            "buggy_functional_requirements_judgment": buggy_functional_requirements_result,
            "buggy_scot": buggy_scot,
            "buggy_scot_judgment": buggy_scot_result
        }
        return guidance

    def generate_and_evaluate_buggy_code_intent(self, post: dict, max_iter: int = 3):
        question_id = post["question_id"]
        question = post["question"]
        print(f"generating buggy code intent for question id: {question_id}")

        generation_start_time = datetime.now()
        messages, generated_buggy_code_intent, gen_token_usage = self.agent.generate_buggy_code_intent(question)
        generation_end_time = datetime.now()
        generation_duration = generation_end_time - generation_start_time
        evaluation_start_time = datetime.now()
        result, review_token_usage = self.judge_agent.evaluate_buggy_code_intent(question, generated_buggy_code_intent)
        evaluation_end_time = datetime.now()
        evaluation_duration = evaluation_end_time - evaluation_start_time

        for itr in range(1, max_iter + 1):
            print(f"iteration: {itr}")
            self.loggers["buggy_code_intent_logger"].append_row(
                question_id=question_id,
                question=question,
                buggy_code_intent=generated_buggy_code_intent,
                judge_buggy_code_intent_label=result.label,
                judge_buggy_code_intent_rational=result.rationale,
                generation_token_usage=gen_token_usage,
                review_token_usage=review_token_usage,
                iteration=itr,
                generation_duration=round(generation_duration.total_seconds(), 2),
                evaluation_duration=round(evaluation_duration.total_seconds(), 2)
            )

            if result.label.lower() == "correct":
                print(f"Buggy code intent accepted in iteration {itr}")
                return generated_buggy_code_intent, result
            start_time = datetime.now()
            messages, generated_buggy_code_intent, gen_token_usage = self.agent.refine_buggy_code_intent(messages,
                                                                                                         result)
            result, review_token_usage = self.judge_agent.evaluate_buggy_code_intent(question,
                                                                                     generated_buggy_code_intent)
            end_time = datetime.now()
            duration = end_time - start_time
        print(f"Buggy code intent not accepted after max iterations {max_iter}")
        return generated_buggy_code_intent, result

    def generate_and_evaluate_buggy_functional_requirements(self, post: dict, max_iter: int = 3):
        # todo: refactor the str conversion
        question_id = post["question_id"]
        question = post["question"]
        print(f"generating buggy functional requirements for question id: {question_id}")

        generation_start_time = datetime.now()
        messages, generated_buggy_functional_requirements, gen_token_usage = self.agent.generate_buggy_functional_requirements(
            question)
        generation_end_time = datetime.now()
        generation_duration = generation_end_time - generation_start_time
        evaluation_start_time = datetime.now()
        result, review_token_usage = self.judge_agent.evaluate_buggy_functional_requirements(question,
                                                                                             generated_buggy_functional_requirements)
        evaluation_end_time = datetime.now()
        evaluation_duration = evaluation_end_time - evaluation_start_time

        for itr in range(1, max_iter + 1):
            print(f"iteration: {itr}")
            self.loggers["buggy_functional_requirements_logger"].append_row(
                question_id=question_id,
                question=question,
                buggy_functional_requirements=generated_buggy_functional_requirements,
                judge_buggy_functional_requirements_label=result.label,
                judge_buggy_functional_requirements_rational=result.rationale,
                iteration=itr,
                generation_token_usage=gen_token_usage,
                review_token_usage=review_token_usage,
                generation_duration=round(generation_duration.total_seconds(), 2),
                evaluation_duration=round(evaluation_duration.total_seconds(), 2)
            )

            if result.label.lower() == "correct":
                print(f"Buggy functional requirements accepted in iteration {itr}")
                return generated_buggy_functional_requirements, result

            generation_start_time = datetime.now()
            messages, generated_buggy_functional_requirements, gen_token_usage = self.agent.refine_buggy_functional_requirements(
                messages,
                result)
            generation_end_time = datetime.now()
            generation_duration = generation_end_time - generation_start_time
            evaluation_start_time = datetime.now()
            result, review_token_usage = self.judge_agent.evaluate_buggy_functional_requirements(question,
                                                                                                 generated_buggy_functional_requirements)
            evaluation_end_time = datetime.now()
            evaluation_duration = evaluation_end_time - evaluation_start_time
        print(f"Buggy functional requirements not accepted after max iterations {max_iter}")
        return generated_buggy_functional_requirements, result

    def generate_and_evaluate_buggy_scot(self, post: dict, max_iter: int = 3):
        question_id = post["question_id"]
        question = post["question"]
        print(f"generating buggy scot for question id: {question_id}")
        generation_start_time = datetime.now()
        messages, generated_buggy_scot, gen_token_usage = self.agent.generate_buggy_scot(question)
        generation_end_time = datetime.now()
        generation_duration = generation_end_time - generation_start_time
        evaluation_start_time = datetime.now()
        result, review_token_usage = self.judge_agent.evaluate_buggy_scot(question, generated_buggy_scot)
        evaluation_end_time = datetime.now()
        evaluation_duration = evaluation_end_time - evaluation_start_time

        for itr in range(1, max_iter + 1):
            print(f"iteration: {itr} ")
            self.loggers["buggy_scot_logger"].append_row(
                question_id=question_id,
                question=question,
                buggy_scot=generated_buggy_scot,
                judge_buggy_scot_label=result.label,
                judge_buggy_scot_rationale=result.rationale,
                generation_token_usage=gen_token_usage,
                review_token_usage=review_token_usage,
                iteration=itr,
                generation_duration=round(generation_duration.total_seconds(), 2),
                evaluation_duration=round(evaluation_duration.total_seconds(), 2)
            )

            if result.label.lower() == "correct":
                print(f"Buggy scot accepted in iteration {itr}")
                return generated_buggy_scot, result

            generation_start_time = datetime.now()
            messages, generated_buggy_scot, gen_token_usage = self.agent.refine_buggy_scot(messages, result)
            generation_end_time = datetime.now()
            generation_duration = generation_end_time - generation_start_time
            evaluation_start_time = datetime.now()
            result, review_token_usage = self.judge_agent.evaluate_buggy_scot(question, generated_buggy_scot)
            evaluation_end_time = datetime.now()
            evaluation_duration = evaluation_end_time - evaluation_start_time

        print(f"Buggy scot not accepted after max iterations {max_iter}")
        return generated_buggy_scot, result
