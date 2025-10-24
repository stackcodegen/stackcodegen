import json
from pathlib import Path
from pprint import pprint

from src.agents.base_agent import BaseAgent
from src.config.loader import ConfigLoader
from src.llm.base import LLMClient
from src.llm.prompt_loader import PromptLoader
from src.models.llm_response_format import JudgeResult
from src.utils.utils import Utils


class JudgeAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__("JudgeLLM")
        self.llm_client = llm_client

        cfg = ConfigLoader()
        prompt_loader = PromptLoader(cfg.prompt_dir)
        self.judge_buggy_code_intent_prompt = prompt_loader.load(
            "judge_llm/buggy/judge_buggy_code_intent.yaml")
        self.buggy_functional_requirement_prompt = prompt_loader.load(
            "judge_llm/buggy/judge_buggy_functional_requirements.yaml")
        self.buggy_scot_prompt = prompt_loader.load(
            "judge_llm/buggy/judge_buggy_scot.yaml")
        self.buggy_code_prompt = prompt_loader.load(
            "judge_llm/buggy/judge_buggy_code.yaml")
        self.judge_patched_code_intent_prompt = prompt_loader.load(
            "judge_llm/patched/judge_patched_code_intent.yaml")
        self.judge_patched_functional_requirement_prompt = prompt_loader.load(
            "judge_llm/patched/judge_patched_functional_requirements.yaml")
        self.judge_patched_scot_prompt = prompt_loader.load(
            "judge_llm/patched/judge_patched_scot.yaml")
        self.judge_patched_code_prompt = prompt_loader.load(
            "judge_llm/patched/judge_patched_code.yaml")

        judge_buggy_code_examples_path = cfg.root_dir / Path(
            "src/prompts/judge_llm/buggy/judge_buggy_code_examples.json")
        with open(judge_buggy_code_examples_path, "r") as f:
            self.judge_buggy_code_examples = json.load(f)

        judge_buggy_code_intent_examples_path = cfg.root_dir / Path(
            "src/prompts/judge_llm/buggy/judge_buggy_code_intent_examples.json")
        with open(judge_buggy_code_intent_examples_path, "r") as f:
            self.judge_buggy_code_intent_examples = json.load(f)

        judge_buggy_functional_requirements_examples_path = cfg.root_dir / Path(
            "src/prompts/judge_llm/buggy/judge_buggy_functional_requirements_examples.json")
        with open(judge_buggy_functional_requirements_examples_path, "r") as f:
            self.judge_buggy_functional_requirements_examples = json.load(f)

        judge_buggy_scot_examples_path = cfg.root_dir / Path(
            "src/prompts/judge_llm/buggy/judge_buggy_scot_examples.json")
        with open(judge_buggy_scot_examples_path, "r") as f:
            self.judge_buggy_scot_examples = json.load(f)

        # patched
        judge_patched_code_examples_path = cfg.root_dir / Path(
            "src/prompts/judge_llm/patched/judge_patched_code_examples.json")
        with open(judge_patched_code_examples_path, "r") as f:
            self.judge_patched_code_examples = json.load(f)

        judge_patched_code_intent_examples_path = cfg.root_dir / Path(
            "src/prompts/judge_llm/patched/judge_patched_code_intent_examples.json")
        with open(judge_patched_code_intent_examples_path, "r") as f:
            self.judge_patched_code_intent_examples = json.load(f)

        judge_patched_functional_requirements_examples_path = cfg.root_dir / Path(
            "src/prompts/judge_llm/patched/judge_patched_functional_requirements_examples.json")
        with open(judge_patched_functional_requirements_examples_path, "r") as f:
            self.judge_patched_functional_requirements_examples = json.load(f)

        judge_patched_scot_examples_path = cfg.root_dir / Path(
            "src/prompts/judge_llm/patched/judge_patched_scot_examples.json")
        with open(judge_patched_scot_examples_path, "r") as f:
            self.judge_patched_scot_examples = json.load(f)

    def evaluate_buggy_code_intent(self, question: str, generated_buggy_code_intent: str):
        system_prompt = self.judge_buggy_code_intent_prompt["system_prompt"]
        prompt_template = self.judge_buggy_code_intent_prompt['task']
        messages = [{"role": "system", "content": system_prompt}]
        user_prompt = prompt_template.format(question=question, buggy_code_intent=generated_buggy_code_intent)
        filtered_examples = Utils.remove_duplicate_example(self.judge_buggy_code_intent_examples, question)
        messages.extend(filtered_examples)
        messages.append({"role": "user", "content": user_prompt})
        response = self.llm_client.call(messages=messages, response_format=JudgeResult)
        return response.parse_json_as(JudgeResult), json.dumps(response.token_usage, indent=2)

    def evaluate_buggy_functional_requirements(self, question: str, generated_buggy_functional_requirements):
        system_prompt = self.buggy_functional_requirement_prompt["system_prompt"]
        prompt_template = self.buggy_functional_requirement_prompt['task']
        messages = [{"role": "system", "content": system_prompt}]
        user_prompt = prompt_template.format(question=question,
                                             functional_requirements=generated_buggy_functional_requirements)
        filtered_examples = Utils.remove_duplicate_example(self.judge_buggy_functional_requirements_examples, question)
        messages.extend(filtered_examples)

        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=JudgeResult)
        return response.parse_json_as(JudgeResult), json.dumps(response.token_usage, indent=2)

    def evaluate_buggy_scot(self, question: str, generated_buggy_scot: str):
        system_prompt = self.buggy_scot_prompt["system_prompt"]
        prompt_template = self.buggy_scot_prompt['task']

        messages = [{"role": "system", "content": system_prompt}]
        filtered_examples = Utils.remove_duplicate_example(self.judge_buggy_scot_examples, question)
        messages.extend(filtered_examples)
        user_prompt = prompt_template.format(question=question,
                                             buggy_scot=generated_buggy_scot)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=JudgeResult)
        return response.parse_json_as(JudgeResult), json.dumps(response.token_usage, indent=2)

    def evaluate_buggy_code(self, question: str, generated_buggy_code: str):
        system_prompt = self.buggy_code_prompt["system_prompt"]
        prompt_template = self.buggy_code_prompt['task']

        messages = [{"role": "system", "content": system_prompt}]
        filtered_examples = Utils.remove_duplicate_example(self.judge_buggy_code_examples, question)
        messages.extend(filtered_examples)
        user_prompt = prompt_template.format(question=question,
                                             buggy_code=generated_buggy_code)
        messages.append({"role": "user", "content": user_prompt})
        # pprint(messages)
        response = self.llm_client.call(messages=messages, response_format=JudgeResult)
        return response.parse_json_as(JudgeResult), json.dumps(response.token_usage, indent=2)

    def evaluate_patched_code_intent(self, question: str, answer: str, generated_patched_code_intent):
        system_prompt = self.judge_patched_code_intent_prompt["system_prompt"]
        prompt_template = self.judge_patched_code_intent_prompt['task']
        messages = [{"role": "system", "content": system_prompt}]
        filtered_examples = Utils.remove_duplicate_example(self.judge_patched_code_intent_examples, question)
        messages.extend(filtered_examples)
        user_prompt = prompt_template.format(question=question, answer=answer,
                                             patched_code_intent=generated_patched_code_intent)

        messages.append({"role": "user", "content": user_prompt})
        # pprint(messages)
        response = self.llm_client.call(messages=messages, response_format=JudgeResult)
        return response.parse_json_as(JudgeResult), json.dumps(response.token_usage, indent=2)

    def evaluate_patched_functional_requirements(self, question: str, answer: str,
                                                 generated_patched_functional_requirements):
        system_prompt = self.judge_patched_functional_requirement_prompt["system_prompt"]
        prompt_template = self.judge_patched_functional_requirement_prompt['task']

        messages = [{"role": "system", "content": system_prompt}]
        filtered_examples = Utils.remove_duplicate_example(self.judge_patched_functional_requirements_examples,
                                                           question)
        messages.extend(filtered_examples)
        user_prompt = prompt_template.format(question=question,
                                             answer=answer,
                                             functional_requirements=generated_patched_functional_requirements)
        messages.append({"role": "user", "content": user_prompt})
        # pprint(messages)
        response = self.llm_client.call(messages=messages, response_format=JudgeResult)
        return response.parse_json_as(JudgeResult), json.dumps(response.token_usage, indent=2)

    def evaluate_patched_scot(self, question: str, answer: str, generated_patched_scot: str):
        system_prompt = self.judge_patched_scot_prompt["system_prompt"]
        prompt_template = self.judge_patched_scot_prompt['task']

        messages = [{"role": "system", "content": system_prompt}]
        filtered_examples = Utils.remove_duplicate_example(self.judge_patched_scot_examples, question)
        messages.extend(filtered_examples)
        user_prompt = prompt_template.format(question=question, answer=answer,
                                             patched_scot=generated_patched_scot)
        messages.append({"role": "user", "content": user_prompt})
        # pprint(messages)
        response = self.llm_client.call(messages=messages, response_format=JudgeResult)
        result = response.parse_json_as(JudgeResult)

        return result, json.dumps(response.token_usage, indent=2)

    def evaluate_patched_code(self, question: str, answer: str, generated_patched_code: str):
        system_prompt = self.judge_patched_code_prompt["system_prompt"]
        prompt_template = self.judge_patched_code_prompt['task']

        messages = [{"role": "system", "content": system_prompt}]
        filtered_examples = Utils.remove_duplicate_example(self.judge_patched_code_examples, question)
        messages.extend(filtered_examples)
        user_prompt = prompt_template.format(question=question,
                                             answer=answer,
                                             patched_code=generated_patched_code)
        messages.append({"role": "user", "content": user_prompt})
        # pprint(messages)
        response = self.llm_client.call(messages=messages, response_format=JudgeResult)

        return response.parse_json_as(JudgeResult), json.dumps(response.token_usage, indent=2)
