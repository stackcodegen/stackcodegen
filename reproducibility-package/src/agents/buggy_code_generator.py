import json
from pathlib import Path

from src.agents.base_agent import BaseAgent
from src.config.loader import ConfigLoader
from src.llm.base import LLMClient

from src.llm.prompt_loader import PromptLoader
from src.models.llm_response_format import BuggyCodeGenerationResult
from src.utils.helper import trim_messages
from src.utils.utils import Utils


class BuggyCodeGeneratorAgent(BaseAgent):
    def __init__(self,
                 llm_client: LLMClient,
                 ):
        super().__init__("BuggyCodeGenerator")
        cfg = ConfigLoader()
        prompt_loader = PromptLoader(cfg.prompt_dir)

        self.llm_client = llm_client
        self.buggy_code_prompt = prompt_loader.load("code_generation/buggy/buggy_code_generator.yaml")
        buggy_code_examples_path = cfg.root_dir / Path(
            "src/prompts/code_generation/buggy/buggy_code_generator_examples.json")
        with open(buggy_code_examples_path, "r") as f:
            self.examples = json.load(f)

    def generate_buggy_code(self, question, guidance):
        system_prompt = self.buggy_code_prompt["system_prompt"]
        prompt_template = self.buggy_code_prompt['task']
        messages = [{"role": "system", "content": system_prompt}]
        user_prompt = prompt_template.format(
            question=question,
            code_intent=guidance['buggy_code_intent'],
            functional_requirements=guidance['buggy_functional_requirements'],
            buggy_scot=guidance['buggy_scot'],
        )

        filtered_examples = Utils.remove_duplicate_example(self.examples, question)
        messages.extend(filtered_examples)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=BuggyCodeGenerationResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(BuggyCodeGenerationResult)
        return messages, parsed, json.dumps(response.token_usage, indent=2)

    def refine_buggy_code(self, messages, prev_result):
        # todo: recheck this part
        prompt_template = self.buggy_code_prompt['refine_exec_error']

        user_prompt = prompt_template.format(
            requirements=prev_result["requirements"],
            buggy_code=prev_result["buggy_code"],
            buggy_stderr=prev_result.get("buggy_stderr", ""),
            docker_error=prev_result.get("docker_error", "No docker error")
        )
        messages = trim_messages(messages, 2)
        messages.append({"role": "user", "content": user_prompt})
        response = self.llm_client.call(messages=messages, response_format=BuggyCodeGenerationResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(BuggyCodeGenerationResult)
        return messages, parsed, json.dumps(response.token_usage, indent=2)

    def refine_buggy_code_reviewed(self, messages, prev_review):
        # todo: recheck this part
        prompt_template = self.buggy_code_prompt['refine_judge_error']

        user_prompt = prompt_template.format(
            label=prev_review.label,
            rationale=prev_review.rationale,
        )
        messages = trim_messages(messages, 2)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=BuggyCodeGenerationResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(BuggyCodeGenerationResult)
        return messages, parsed, json.dumps(response.token_usage, indent=2)
