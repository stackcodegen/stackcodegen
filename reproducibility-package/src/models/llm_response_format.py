from pydantic import BaseModel


class FunctionalRequirements(BaseModel):
    input_output: str
    expected_behavior: str
    edge_cases: str

class BuggyCodeGenerationResult(BaseModel):
    buggy_code: str
    requirements: str


class JudgeResult(BaseModel):
    label: str
    rationale: str


class BuggyCodeIntentResult(BaseModel):
    buggy_code_intent: str


class BuggyFunctionalRequirementsResult(BaseModel):
    functional_requirements: FunctionalRequirements
    # functional_requirements: str


class BuggyScotResult(BaseModel):
    buggy_scot: str


class PatchedCodeIntentResult(BaseModel):
    patched_code_intent: str


class PatchedFunctionalRequirementsResult(BaseModel):
    # functional_requirements: FunctionalRequirements
    functional_requirements: str


class PatchedScotResult(BaseModel):
    patched_scot: str


class PatchedCodeGenerationResult(BaseModel):
    patched_code: str
    requirements: str
