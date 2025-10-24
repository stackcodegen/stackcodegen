import json
from pathlib import Path

from src.agents.base_agent import BaseAgent
from src.config.loader import ConfigLoader
from src.llm.base import LLMClient
from src.llm.prompt_loader import PromptLoader
from src.models.llm_response_format import PatchedCodeGenerationResult
from src.utils.helper import trim_messages
from src.utils.utils import Utils


class PatchedCodeGeneratorAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__("PatchedCodeGenerator")

        cfg = ConfigLoader()
        prompt_loader = PromptLoader(cfg.prompt_dir)

        self.llm_client = llm_client
        self.patched_code_prompt = prompt_loader.load("code_generation/patched/patched_code_generator.yaml")

        patched_code_examples_path = cfg.root_dir / Path(
            "src/prompts/code_generation/patched/patched_code_generator_examples.json")
        with open(patched_code_examples_path, "r") as f:
            self.examples = json.load(f)

    def generate_patched_code(self, buggy_code, guidance):
        system_prompt = self.patched_code_prompt["system_prompt"]
        prompt_template = self.patched_code_prompt['task']
        messages = [{"role": "system", "content": system_prompt}]

        filtered_examples = Utils.remove_duplicate_example(self.examples, buggy_code)
        messages.extend(filtered_examples)

        user_prompt = prompt_template.format(
            buggy_code=buggy_code,
            code_intent=guidance['patched_code_intent'],
            functional_requirements=guidance['patched_functional_requirements'],
            scot=guidance['patched_scot'],
        )
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=PatchedCodeGenerationResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(PatchedCodeGenerationResult)
        return messages, parsed, json.dumps(response.token_usage, indent=2)

    def refine_patched_code(self, messages, prev_result):
        # todo: recheck this part
        prompt_template = self.patched_code_prompt['refine_exec_error']

        user_prompt = prompt_template.format(
            requirements=prev_result["requirements"],
            patched_code=prev_result["patched_code"],
            stderr=prev_result.get("stderr", ""),
            docker_error=prev_result.get("docker_error", "No docker error")
        )
        trim_messages(messages, 2)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=PatchedCodeGenerationResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(PatchedCodeGenerationResult)
        return messages, parsed, json.dumps(response.token_usage, indent=2)

    def refine_patched_code_reviewed(self, messages, prev_review):
        # todo: recheck this part
        prompt_template = self.patched_code_prompt['refine_judge_error']

        user_prompt = prompt_template.format(
            label=prev_review.label,
            rationale=prev_review.rationale,
        )
        trim_messages(messages, 2)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=PatchedCodeGenerationResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(PatchedCodeGenerationResult)
        return messages, parsed,json.dumps(response.token_usage, indent=2)
