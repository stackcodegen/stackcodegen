# StackCodeGen Prompts

The prompt templates used in StackCodeGen are organized by purpose:

---

### Generator LLM Prompts

These are used for generating:

- **Buggy Code Intent:** [buggy_code_intent_generator.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/generator_llm_prompts/buggy_code_intent_generator.yaml)
- **Functional Requirements:** [buggy_functional_requirements_generator.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/generator_llm_prompts/buggy_functional_requirements_generator.yaml)
- **Structured Chain of Thought (SCoT):** [buggy_scot_generator.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/generator_llm_prompts/buggy_scot_generator.yaml)
- **Code:** [buggy_code_generator.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/generator_llm_prompts/buggy_code_generator.yaml)

Patched code generation:

- **Patched Code Intent:** [patched_code_intent_generator.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/generator_llm_prompts/patched_code_intent_generator.yaml)
- **Functional Requirements:** [patched_functional_requirements_generator.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/generator_llm_prompts/patched_functional_requirements_generator.yaml)
- **Structured Chain of Thought (SCoT):** [patched_scot_generator.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/generator_llm_prompts/patched_scot_generator.yaml)
- **Code:** [patched_code_generator.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/generator_llm_prompts/patched_code_generator.yaml)

---

### Reviewer LLM Prompts

These are used for evaluating the generated outputs:

- **Code Intent:** [review_buggy_code_intent.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/reviewer_llm_prompts/judge_buggy_code_intent.yaml)
- **Functional Requirements:** [review_buggy_functional_requirements.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/reviewer_llm_prompts/judge_buggy_functional_requirements.yaml)
- **Structured Chain of Thought (SCoT):** [review_buggy_scot.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/reviewer_llm_prompts/judge_buggy_scot.yaml)
- **Code:** [review_buggy_code.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/reviewer_llm_prompts/judge_buggy_code.yaml)

Reviewing patched code:

- **Code Intent:** [review_patched_code_intent.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/reviewer_llm_prompts/judge_patched_code_intent.yaml)
- **Functional Requirements:** [review_patched_functional_requirements.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/reviewer_llm_prompts/judge_patched_functional_requirements.yaml)
- **Structured Chain of Thought (SCoT):** [review_patched_scot.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/reviewer_llm_prompts/judge_patched_scot.yaml)
- **Code:** [review_patched_code.yaml](https://github.com/stackcodegen/stackcodegen/blob/main/prompts/reviewer_llm_prompts/judge_patched_code.yaml)

---

Each YAML file defines the system, user, and few-shot configurations used by the corresponding LLM module.
