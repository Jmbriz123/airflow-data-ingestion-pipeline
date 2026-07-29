# MANIFEST: customer_care_emails

## Overview

| Property        | Value                                                                                     |
|-----------------|-------------------------------------------------------------------------------------------|
| **Source**      | [rtweera/customer_care_emails](https://huggingface.co/datasets/rtweera/customer_care_emails) |
| **Curated by**  | Ravindu Weerasinghe (`weerasinghert.21@itfac.mrt.ac.lk`)                                 |
| **License**     | GPL-3.0                                                                                   |
| **Language**    | English                                                                                   |
| **Modality**    | Text                                                                                      |
| **Format**      | CSV (auto-converted to Parquet on HuggingFace)                                            |
| **Size**        | 2,259 rows · 1.52 MB                                                                      |
| **Splits**      | `train` only (single split, 2,259 rows)                                                   |
| **Local Path**  | `sample_data/dataset.csv`                                                               |
| **Last Updated**| November 8, 2024                                                                          |


## Description

A synthetically generated dataset of customer care emails for **Aetheros**, a fictional middleware solutions company. Emails are structured as threaded conversations (typically 4–5 emails per thread) between customers and support agents. The dataset covers five Aetheros product lines:

1. **API Development** — Custom, scalable, and secure API creation
2. **API Monitoring** — Real-time monitoring and analytics
3. **IAM (Identity and Access Management)** — User identity and access permission management
4. **Mercury Language** — Proprietary high-level language for API development
5. **Cloud Management** — Cloud deployment, monitoring, optimization, and security

Generated via the **Google Gemini Pro API**. All persons, organizations, and email addresses are fictional.


## Intended Use

| Use Case                     | Supported |
|------------------------------|-----------|
| Customer sentiment analysis  | ✅        |
| Email classification (type/criticality) | ✅ |
| Agent performance evaluation | ✅        |
| NLP model training/fine-tuning | ✅      |
| PII/privacy-sensitive analysis | ❌ (no real PII) |


## Schema

| Column                  | Type           | Cardinality / Range                                                                                   | Description                                                                                                          |
|-------------------------|----------------|-------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `subject`               | `string`       | Free text · 15–118 chars                                                                              | Subject line of the email thread                                                                                     |
| `sender`                | `string`       | 90 unique values                                                                                      | Email address of the sender                                                                                          |
| `receiver`              | `string`       | 90 unique values                                                                                      | Email address of the receiver                                                                                        |
| `timestamp`             | `datetime`     | ISO 8601 with timezone · 19–32 chars                                                                  | Date and time the email was sent                                                                                     |
| `message_body`          | `string`       | 30–1,490 chars                                                                                        | Full body text of the email                                                                                          |
| `thread_id`             | `string`       | Unique per thread · format `aa{NNN}-{UUID}`                                                           | Groups individual emails into conversation threads                                                                   |
| `email_types`           | `list[string]` | `["inquiry"]`, `["issue"]`, `["suggestion"]`, or combinations                                        | Classification of the email's intent; stored as a stringified list                                                   |
| `email_status`          | `string`       | `"ongoing"` \| `"completed"`                                                                          | Whether the thread is still open or has been resolvaed                                                                |
| `email_criticality`     | `string`       | `"low"` \| `"medium"` \| `"high"`                                                                    | Severity of the issue as assessed by the dataset creator                                                             |
| `product_types`         | `list[string]` | Up to 79 unique product tag combinations across 5 product lines                                       | Which Aetheros products the email concerns; stored as a stringified list                                             |
| `agent_effectivity`     | `string`       | `"very low"` \| `"low"` \| `"medium"` \| `"high"` \| `"very high"`                                  | Quality of the support agent's response (how well they helped)                                                       |
| `agent_efficiency`      | `string`       | `"very low"` \| `"low"` \| `"medium"` \| `"high"` \| `"very high"`                                  | Timeliness of the support agent's response (how quickly they helped)                                                 |
| `customer_satisfaction` | `float64`      | –1.0 to +1.0                                                                                          | Sentiment score of the customer; negative = frustrated/angry, positive = satisfied/happy; constant within a thread  |


## Key Data Characteristics

- **Thread structure**: All rows sharing the same `thread_id` belong to one conversation. The `customer_satisfaction`, `email_criticality`, `email_status`, `email_types`, and `product_types` fields are **constant across all rows within a thread** — they are thread-level labels, not per-message labels.
- **Ordinal fields**: `agent_effectivity`, `agent_efficiency`, and `email_criticality` are stored as strings but carry ordinal meaning. Encode them before use in ML pipelines (e.g., `very low=0 … very high=4`).
- **List-valued columns**: `email_types` and `product_types` are stored as stringified Python lists (e.g., `"['inquiry', 'issue']"`). Parse with `ast.literal_eval()` before use.
- **Timestamp timezone**: Timestamps include UTC offset (`+00:00`) but vary in precision (some include microseconds). Normalize to a consistent format during ingestion.
- **Synthetic data**: All email addresses, names, API keys, and account IDs are fabricated. No anonymization is needed, but downstream models should not be expected to generalize to real email domains or naming conventions.


## Version History

| Version | Date              | Changes                                                                                      |
|---------|-------------------|----------------------------------------------------------------------------------------------|
| `v2`    | November 8, 2024  | All data files merged into a single file; fixed `agent_effectivity` / `agent_efficiency` field issues that broke the HuggingFace data viewer |
| `v1`    | September 1, 2024 | Initial upload with 16 separate CSV files                                                    |


## Loading the Dataset

**Python (HuggingFace `datasets` library)**
```python
from datasets import load_dataset

ds = load_dataset("rtweera/customer_care_emails")
df = ds["train"].to_pandas()
```

**Python (pandas, direct CSV)**
```python
import pandas as pd
import ast

df = pd.read_csv("hf://datasets/rtweera/customer_care_emails/data/train-*.csv")

# Parse list-valued columns
df["email_types"] = df["email_types"].apply(ast.literal_eval)
df["product_types"] = df["product_types"].apply(ast.literal_eval)

# Parse timestamps
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
```


## Known Limitations

- **Single domain**: All emails concern a single fictional company (Aetheros) and five tightly scoped product areas. Models trained solely on this data may not generalize to other industries or support domains.
- **Synthetic distribution**: Class distributions (criticality, satisfaction, agent ratings) reflect the generation prompt, not real-world support email distributions.
- **No ground-truth thread ordering**: Individual emails within a thread are not explicitly indexed by position. Use `timestamp` to reconstruct chronological order.
- **Imbalanced splits**: The dataset ships with only a `train` split. Users must create their own train/validation/test partitions, ideally splitting at the thread level (by `thread_id`) to avoid data leakage.