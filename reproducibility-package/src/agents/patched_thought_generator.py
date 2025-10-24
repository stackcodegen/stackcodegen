import json
from pathlib import Path
from src.agents.base_agent import BaseAgent
from src.config.loader import ConfigLoader
from src.llm.base import LLMClient
from src.llm.prompt_loader import PromptLoader
from src.models.llm_response_format import PatchedCodeIntentResult, PatchedFunctionalRequirementsResult, \
    PatchedScotResult
from src.utils.helper import trim_messages
from src.utils.utils import Utils


class PatchedThoughtGeneratorAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, ):
        super().__init__("PatchedThoughtGenerator")
        self.llm_client = llm_client
        cfg = ConfigLoader()
        prompt_loader = PromptLoader(cfg.prompt_dir)

        self.patched_code_intent_prompt = prompt_loader.load(
            "thought_generation/patched/patched_code_intent_generator.yaml")
        self.patched_functional_requirements_prompt = prompt_loader.load(
            "thought_generation/patched/patched_functional_requirements_generator.yaml")
        self.patched_scot_prompt = prompt_loader.load("thought_generation/patched/patched_scot_generator.yaml")

        patched_code_intent_examples_path = cfg.root_dir / Path(
            "src/prompts/thought_generation/patched/patched_code_intent_examples.json")
        with open(patched_code_intent_examples_path, "r") as f:
            self.patched_code_intent_examples = json.load(f)

        patched_functional_requirements_examples_path = cfg.root_dir / Path(
            "src/prompts/thought_generation/patched/patched_functional_requirements_examples.json")
        with open(patched_functional_requirements_examples_path, "r") as f:
            self.patched_functional_requirements_examples = json.load(f)

        patched_scot_examples_path = cfg.root_dir / Path(
            "src/prompts/thought_generation/patched/patched_scot_examples.json")
        with open(patched_scot_examples_path, "r") as f:
            self.patched_scot_examples = json.load(f)

    def generate_patched_code_intent(self, question: str, answer: str):
        system_prompt = self.patched_code_intent_prompt["system_prompt"]
        prompt_template = self.patched_code_intent_prompt['task']
        messages = [{"role": "system", "content": system_prompt}]

        filtered_examples = Utils.remove_duplicate_example(self.patched_code_intent_examples, question)
        messages.extend(filtered_examples)

        user_prompt = prompt_template.format(question=question, answer=answer)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=PatchedCodeIntentResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(PatchedCodeIntentResult)
        return messages, parsed.patched_code_intent, json.dumps(response.token_usage, indent=2)

    def refine_patched_code_intent(self, messages, result):
        label = result.label
        rationale = result.rationale
        prompt_template = self.patched_code_intent_prompt['refine']
        refinement_prompt = prompt_template.format(label=label, rationale=rationale)
        messages = trim_messages(messages, 2)
        messages.append({"role": "user", "content": refinement_prompt})

        response = self.llm_client.call(messages=messages, response_format=PatchedCodeIntentResult)
        messages.append({"role": "assistant", "content": response.message.content})

        parsed = response.parse_json_as(PatchedCodeIntentResult)
        return messages, parsed.patched_code_intent, json.dumps(response.token_usage, indent=2)

    def generate_patched_functional_requirements(self, question: str, answer: str):
        system_prompt = self.patched_functional_requirements_prompt["system_prompt"]
        prompt_template = self.patched_functional_requirements_prompt['task']

        messages = [{"role": "system", "content": system_prompt}]

        filtered_examples = Utils.remove_duplicate_example(self.patched_functional_requirements_examples, question)
        messages.extend(filtered_examples)

        user_prompt = prompt_template.format(question=question, answer=answer)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=PatchedFunctionalRequirementsResult)
        messages.append({"role": "assistant", "content": response.message.content})

        # parsed = response.parse_json_as(PatchedFunctionalRequirementsResult)
        # return messages, json.dumps(parsed.functional_requirements.dict(), indent=2), json.dumps(response.token_usage,
        #                                                                                          indent=2)

        return messages, response.message.content, json.dumps(response.token_usage, indent=2)

    def refine_patched_functional_requirements(self, messages, result):
        label = result.label
        rationale = result.rationale

        prompt_template = self.patched_functional_requirements_prompt['refine']
        refinement_prompt = prompt_template.format(label=label, rationale=rationale)
        messages = trim_messages(messages, 2)
        messages.append({"role": "user", "content": refinement_prompt})

        response = self.llm_client.call(messages=messages, response_format=PatchedFunctionalRequirementsResult)
        messages.append({"role": "assistant", "content": response.message.content})

        # parsed = response.parse_json_as(PatchedFunctionalRequirementsResult)
        # return messages, json.dumps(parsed.functional_requirements.dict(), indent=2), json.dumps(response.token_usage,
        #                                                                                          indent=2)
        return messages, response.message.content, json.dumps(response.token_usage, indent=2)

    def generate_patched_scot(self, question: str, answer: str):
        system_prompt = self.patched_scot_prompt["system_prompt"]
        prompt_template = self.patched_scot_prompt['task']

        messages = [{"role": "system", "content": system_prompt}]
        filtered_examples = Utils.remove_duplicate_example(self.patched_scot_examples, question)
        messages.extend(filtered_examples)

        user_prompt = prompt_template.format(question=question, answer=answer)
        messages.append({"role": "user", "content": user_prompt})

        response = self.llm_client.call(messages=messages, response_format=PatchedScotResult)
        messages.append({"role": "assistant", "content": response.message.content})

        # parsed = response.parse_json_as(PatchedScotResult)
        return messages, response.message.content, json.dumps(response.token_usage, indent=2)

    def refine_patched_scot(self, messages, result):
        label = result.label
        rationale = result.rationale

        prompt_template = self.patched_scot_prompt['refine']
        refinement_prompt = prompt_template.format(label=label, rationale=rationale)
        messages.append({"role": "user", "content": refinement_prompt})

        response = self.llm_client.call(messages=messages, response_format=PatchedScotResult)
        messages.append({"role": "assistant", "content": response.message.content})

        # parsed = response.parse_json_as(PatchedScotResult)
        return messages, response.message.content, json.dumps(response.token_usage, indent=2)
