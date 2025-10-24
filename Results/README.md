
# StackCodeGen Results

This directory contains the evaluation outcomes and artifacts generated from the StackCodeGen experiments.

---

### Evaluation Summaries

- **[StackCodeGen_Results.xlsx](https://github.com/stackcodegen/stackcodegen/blob/main/Results/StackCodeGen%20Results.xlsx)** — consolidated evaluation reports for all research questions (RQ1–RQ3), including model-level metrics (Precision, Recall, F1, F3, Execution Success Rate, Levenshtein Distance, etc.).

---

### Metrics Reported

Each evaluation artifact includes:

- **Execution Success Rate (ESR)** — percentage of code successfully compiled/executed.
- **CodeBERTScore Precision / Recall / F1 / F3** — textual and semantic similarity to reference implementations.
- **Levenshtein Distance (LD)** — character-level difference between generated and reference code.
- **Coverage** — proportion of tasks for which valid outputs were produced.

---

### Research Questions (RQs)

- **RQ1:** Effectiveness — How effective is StackCodeGen in generating buggy and patch executable codes from StackOverflow posts?
- **RQ2:** Reliability — How reliable is the generated buggy and patched code that reproduces the bug and applies the patches?
- **RQ3:** Efficiency — WWhat is the time and budget to generate and assess the patches from Stack Overflow posts, and the number of iterations?

---

All results were produced using the unified evaluation pipeline described in the paper, ensuring consistent benchmarking and reproducibility.
