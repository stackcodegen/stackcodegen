from datetime import datetime
from typing import List
from src.agents.judge.judge import JudgeAgent
from src.agents.patched_thought_generator import PatchedThoughtGeneratorAgent
from src.llm.base import LLMClient
from pprint import pprint


class PatchedThoughtGeneratorPipeline:
    def __init__(self, llm: LLMClient, judge_llm: LLMClient, loggers: dict, posts: List[dict] = None):
        self.posts = posts
        self.agent = PatchedThoughtGeneratorAgent(llm)
        self.judge_agent = JudgeAgent(judge_llm)
        self.loggers = loggers

    def run(self, post):

        patched_code_intent, patched_code_intent_result = self.generate_and_evaluate_patched_code_intent(post)
        patched_functional_requirements, patched_functional_requirements_result = self.generate_and_evaluate_patched_functional_requirements(
            post)
        patched_scot, patched_scot_result = self.generate_and_evaluate_patched_scot(post)
        guidance = {
            "question_id": post["question_id"],
            "patched_code_intent": patched_code_intent,
            "patched_code_intent_judgment": patched_code_intent_result,
            "patched_functional_requirements": patched_functional_requirements,
            "patched_functional_requirements_judgment": patched_functional_requirements_result,
            "patched_scot": patched_scot,
            "patched_scot_judgment": patched_scot_result
        }

        return guidance

    def generate_and_evaluate_patched_code_intent(self, post: dict, max_iter: int = 3):
        question_id = post["question_id"]
        question = post["question"]
        answer = post["answer"]
        print(f"generating patched code intent for question id: {question_id}")

        generation_start_time = datetime.now()
        messages, generated_patched_code_intent, gen_token_usage = self.agent.generate_patched_code_intent(question,
                                                                                                           answer)
        generation_end_time = datetime.now()
        generation_duration = generation_end_time - generation_start_time

        evaluation_start_time = datetime.now()
        result, review_token_usage = self.judge_agent.evaluate_patched_code_intent(question, answer,
                                                                                   generated_patched_code_intent)
        evaluation_end_time = datetime.now()
        evaluation_duration = evaluation_end_time - evaluation_start_time

        for itr in range(1, max_iter + 1):
            self.loggers["patched_code_intent_logger"].append_row(
                question_id=question_id,
                question=question,
                answer=answer,
                patched_code_intent=generated_patched_code_intent,
                judge_patched_code_intent_label=result.label,
                judge_patched_code_intent_rational=result.rationale,
                iteration=itr,
                generation_token_usage=gen_token_usage,
                review_token_usage=review_token_usage,
                generation_duration=round(generation_duration.total_seconds(), 2),
                evaluation_duration=round(evaluation_duration.total_seconds(), 2)
            )

            if result.label.lower() == "correct":
                print(f"Patched code intent accepted in iteration {itr}")
                return generated_patched_code_intent, result

            generation_start_time = datetime.now()
            messages, generated_patched_code_intent, gen_token_usage = self.agent.refine_patched_code_intent(messages,
                                                                                                             result)
            generation_end_time = datetime.now()
            generation_duration = generation_end_time - generation_start_time

            evaluation_start_time = datetime.now()
            result, review_token_usage = self.judge_agent.evaluate_patched_code_intent(question, answer,
                                                                                       generated_patched_code_intent)

            evaluation_end_time = datetime.now()
            evaluation_duration = evaluation_end_time - evaluation_start_time

        print(f"Patched code intent not accepted after max iterations {max_iter}")
        return generated_patched_code_intent, result

    def generate_and_evaluate_patched_functional_requirements(self, post: dict, max_iter: int = 3):
        question_id = post["question_id"]
        question = post["question"]
        answer = post["answer"]
        print(f"generating patched functional requirements for question id: {question_id}")

        generation_start_time = datetime.now()
        messages, generated_patched_functional_requirements, gen_token_usage = self.agent.generate_patched_functional_requirements(
            question, answer)
        generation_end_time = datetime.now()
        generation_duration = generation_end_time - generation_start_time

        evaluation_start_time = datetime.now()
        result, review_token_usage = self.judge_agent.evaluate_patched_functional_requirements(question, answer,
                                                                                               generated_patched_functional_requirements)
        evaluation_end_time = datetime.now()
        evaluation_duration = evaluation_end_time - evaluation_start_time

        for itr in range(1, max_iter + 1):
            self.loggers["patched_functional_requirements_logger"].append_row(
                question_id=question_id,
                question=question,
                answer=answer,
                patched_functional_requirements=generated_patched_functional_requirements,
                judge_patched_functional_requirements_label=result.label,
                judge_patched_functional_requirements_rational=result.rationale,
                iteration=itr,
                generation_token_usage=gen_token_usage,
                review_token_usage=review_token_usage,
                generation_duration=round(generation_duration.total_seconds(), 2),
                evaluation_duration=round(evaluation_duration.total_seconds(), 2)
            )

            if result.label.lower() == "correct":
                print(f"patched functional requirements accepted in iteration {itr}")
                return generated_patched_functional_requirements, result

            generation_start_time = datetime.now()
            messages, generated_patched_functional_requirements, gen_token_usage = self.agent.refine_patched_functional_requirements(
                messages, result)
            generation_end_time = datetime.now()
            generation_duration = generation_end_time - generation_start_time
            evaluation_start_time = datetime.now()
            result, review_token_usage = self.judge_agent.evaluate_patched_functional_requirements(question, answer,
                                                                                                   generated_patched_functional_requirements)
            evaluation_end_time = datetime.now()
            evaluation_duration = evaluation_end_time - evaluation_start_time

        print(f"Patched functional requirements are not accepted after max iterations {max_iter}")
        return generated_patched_functional_requirements, result

    def generate_and_evaluate_patched_scot(self, post: dict, max_iter: int = 3):
        question_id = post["question_id"]
        question = post["question"]
        answer = post["answer"]
        print(f"generating patched scot for question id: {question_id}")

        generation_start_time = datetime.now()
        messages, generated_patched_scot, gen_token_usage = self.agent.generate_patched_scot(question, answer)
        generation_end_time = datetime.now()
        generation_duration = generation_end_time - generation_start_time

        evaluation_start_time = datetime.now()
        result, review_token_usage = self.judge_agent.evaluate_patched_scot(question, answer, generated_patched_scot)
        evaluation_end_time = datetime.now()
        evaluation_duration = evaluation_end_time - evaluation_start_time

        for itr in range(1, max_iter + 1):
            self.loggers["patched_scot_logger"].append_row(
                question_id=question_id,
                question=question,
                answer=answer,
                patched_scot=generated_patched_scot,
                judge_patched_scot_label=result.label,
                judge_patched_scot_rational=result.rationale,
                iteration=itr,
                generation_token_usage=gen_token_usage,
                review_token_usage=review_token_usage,
                generation_duration=round(generation_duration.total_seconds(), 2),
                evaluation_duration=round(evaluation_duration.total_seconds(), 2)
            )

            if result.label.lower() == "correct":
                print(f"Patched scot accepted in iteration {itr}")
                return generated_patched_scot, result
            start_time = datetime.now()
            generation_start_time = datetime.now()
            messages, generated_patched_scot, gen_token_usage = self.agent.refine_patched_scot(messages, result)
            generation_end_time = datetime.now()
            generation_duration = generation_end_time - generation_start_time
            evaluation_start_time = datetime.now()
            result, review_token_usage = self.judge_agent.evaluate_patched_scot(question, answer,
                                                                                generated_patched_scot)
            evaluation_end_time = datetime.now()
            evaluation_duration = evaluation_end_time - evaluation_start_time
        print(f"patched scot not accepted after max iterations {max_iter}")
        return generated_patched_scot, result
