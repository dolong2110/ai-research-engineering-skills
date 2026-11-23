## 1. Experimental Setup

* **Datasets & Splits:**
  * **Dataset Name:** Total size, domains/categories, and exact Train / Validation / Test split counts.
* **Evaluation Metrics:**
  * Primary and secondary metrics, mathematical definitions if non-standard, and whether higher (`↑`) or lower (`↓`) is better.
* **Baselines Compared:**
  * List every compared method, its category/backbone, and whether numbers are cited from prior work or re-evaluated under unified settings.
* **Implementation Details:**
  * **Initialization / Backbone:** ...
  * **Architecture Hyperparameters:** ...
  * **Optimizer & Schedule:** Learning rate, weight decay, batch size, epochs/iterations, warmup.
  * **Hardware & Runtime:** GPU/TPU count and training/inference cost.
  * **Model Selection:** Validation criterion and number of random seeds.

## 2. Raw Numeric Data

**Table 1: Main comparison on [Dataset Name]**

| Method | Backbone / Setting | Metric 1 (↑) | Metric 2 (↑) | Metric 3 (↓) |
| :--- | :--- | :--- | :--- | :--- |
| Baseline A | ... | 0.00 | 0.00 | 0.00 |
| **Ours** | ... | **0.00** | **0.00** | **0.00** |

**Table 2: Ablation study of core components**

| Variant | Metric 1 (↑) | Metric 2 (↑) |
| :--- | :--- | :--- |
| Full Model | **0.00** | **0.00** |
| w/o Component A | 0.00 | 0.00 |
| w/o Component B | 0.00 | 0.00 |

**Table 3: Hyperparameter sensitivity**

| Hyperparameter Setting | Metric 1 (↑) | Metric 2 (↑) |
| :--- | :--- | :--- |
| Setting 1 | 0.00 | 0.00 |
| Setting 2 | **0.00** | **0.00** |

## 3. Qualitative Observations

* **Comparisons with State-of-the-Art:** Key quantitative deltas and where gains are largest.
* **Ablation Takeaways:** Which component drives the largest gain and how modules interact.
* **Failure Modes & Honest Limitations:** Specific subsets, edge cases, or compute trade-offs where the method underperforms or faces constraints.
