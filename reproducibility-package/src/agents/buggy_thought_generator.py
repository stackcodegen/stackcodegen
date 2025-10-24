import json
from pathlib import Path

from src.agents.base_agent import BaseAgent
from src.config.loader import ConfigLoader
from src.llm.base import LLMClient

from src.llm.prompt_loader import PromptLoader
from src.models.llm_response_format import BuggyCodeIntentResult, BuggyFunctionalRequirementsResult, BuggyScotResult
from src.utils.helper import trim_messages
from src.utils.utils import Utils


class BuggyThoughtGeneratorAgent(BaseAgent):
    def __init__(self,
                 llm_client: LLMClient,
                 ):
        super().__init__("BuggyThoughtGenerator")
        self.llm_client = llm_client
        cfg = ConfigLoader()
        prompt_loader = PromptLoader(cfg.prompt_dir)
        self.buggy_code_intent_prompt = prompt_loader.load("thought_generation/buggy/buggy_code_intent_generator.yaml")
        self.buggy_functional_requirements_prompt = prompt_loader.load(
            "thought_generation/buggy/buggy_functional_requirements_generator.yaml")
        self.buggy_scot_prompt = prompt_loader.load("thought_generation/buggy/buggy_scot_generator.yaml")

        # examples
        buggy_code_intent_examples_path = cfg.root_dir / Path(
            "src/prompts/thought_generation/buggy/buggy_code_intent_examples.json")
        with open(buggy_code_intent_examples_path, "r") as f:
            self.buggy_code_intent_examples = json.load(f)

        buggy_functional_requirements_examples_path = cfg.root_dir / Path(
            "src/prompts/thought_generation/buggy/buggy_functional_requirements_examples.json")
        with open(buggy_functional_requirements_examples_path, "r") as f:
            self.buggy_functional_requirements_examples = json.load(f)

        buggy_scot_examples_path = cfg.root_dir / Path(
            "src/prompts/thought_generation/buggy/buggy_scot_examples.json")
        with open(buggy_scot_examples_path, "r") as f:
            self.buggy_scot_examples = json.load(f)

    def generate_buggy_code_intent(self, question: str):
        system_prompt = self.buggy_code_intent_prompt["system_prompt"]
        prompt_template = self.buggy_code_intent_prompt['task']
        messages = [{"role": "system", "content": system_prompt}]
        user_prompt = prompt_template.format(question=question)

        filtered_examples = Utils.remove_duplicate_example(self.buggy_code_intent_examples, question)
        messages.extend(filtered_examples)

        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=BuggyCodeIntentResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(BuggyCodeIntentResult)
        return messages, parsed.buggy_code_intent, json.dumps(response.token_usage, indent=2)

    def refine_buggy_code_intent(self, messages, result):
        label = result.label
        rationale = result.rationale
        prompt_template = self.buggy_code_intent_prompt['refine']
        refinement_prompt = prompt_template.format(label=label, rationale=rationale)

        messages = trim_messages(messages, 2)
        messages.append({"role": "user", "content": refinement_prompt})

        response = self.llm_client.call(messages=messages, response_format=BuggyCodeIntentResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(BuggyCodeIntentResult)
        return messages, parsed.buggy_code_intent, json.dumps(response.token_usage, indent=2)

    def generate_buggy_functional_requirements(self, question: str):
        system_prompt = self.buggy_functional_requirements_prompt["system_prompt"]
        prompt_template = self.buggy_functional_requirements_prompt['task']

        messages = [{"role": "system", "content": system_prompt}]
        filtered_examples = Utils.remove_duplicate_example(self.buggy_functional_requirements_examples, question)
        messages.extend(filtered_examples)

        user_prompt = prompt_template.format(question=question)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=BuggyFunctionalRequirementsResult)
        messages.append({"role": "assistant", "content": response.message.content})

        # parsed = response.parse_json_as(BuggyFunctionalRequirementsResult)
        # return messages, json.dumps(parsed.functional_requirements.dict(), indent=2), json.dumps(response.token_usage,
        #                                                                                          indent=2)
        return messages, response.message.content, json.dumps(response.token_usage, indent=2)

    def refine_buggy_functional_requirements(self, messages, result):
        label = result.label
        rationale = result.rationale

        prompt_template = self.buggy_functional_requirements_prompt['refine']
        refinement_prompt = prompt_template.format(label=label, rationale=rationale)
        messages = trim_messages(messages, 2)
        messages.append({"role": "user", "content": refinement_prompt})

        response = self.llm_client.call(messages=messages, response_format=BuggyFunctionalRequirementsResult)
        messages.append({"role": "assistant", "content": response.message.content})

        # parsed = response.parse_json_as(BuggyFunctionalRequirementsResult)
        # return messages, json.dumps(parsed.functional_requirements.dict(), indent=2), json.dumps(response.token_usage,
        #                                                                                          indent=2)
        return messages, response.message.content, json.dumps(response.token_usage, indent=2)

    def generate_buggy_scot(self, question: str):
        system_prompt = self.buggy_scot_prompt["system_prompt"]
        prompt_template = self.buggy_scot_prompt['task']

        messages = [{"role": "system", "content": system_prompt}]
        filtered_examples = Utils.remove_duplicate_example(self.buggy_scot_examples, question)
        messages.extend(filtered_examples)

        user_prompt = prompt_template.format(question=question)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=BuggyScotResult)
        parsed = response.parse_json_as(BuggyScotResult)

        messages.append({"role": "assistant", "content": response.message.content})

        return messages, parsed.buggy_scot, json.dumps(response.token_usage, indent=2)

    def refine_buggy_scot(self, messages, result):
        label = result.label
        rationale = result.rationale

        prompt_template = self.buggy_scot_prompt['refine']
        refinement_prompt = prompt_template.format(label=label, rationale=rationale)
        messages = trim_messages(messages, 2)
        messages.append({"role": "user", "content": refinement_prompt})

        response = self.llm_client.call(messages=messages, response_format=BuggyScotResult)
        parsed = response.parse_json_as(BuggyScotResult)
        messages.append({"role": "assistant", "content": response.message.content})
        return messages, parsed.buggy_scot, json.dumps(response.token_usage, indent=2)
