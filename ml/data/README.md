# Dataset directory

Raw dataset files live in `data/raw/`. **Do not commit raw dataset files.**

## Dataset used for URL classification (T-02)

**Hannousse & Yahiouche Phishing Dataset (dataset_B_05_2020.csv)**

| Property | Value |
|----------|-------|
| File | `data/raw/hannousse/dataset_B_05_2020.csv` |
| Source | https://data.mendeley.com/datasets/c2gw7fy2j4/3 |
| Authors | Hannousse, Abdelhak; Yahiouche, Salima |
| Title | "Towards a Benchmark of Machine Learning Methods for Phishing Websites Detection" |
| License | **CC BY 4.0** — https://creativecommons.org/licenses/by/4.0/ |
| Year | 2020 |
| Rows (raw) | 11,430 |
| Rows (after URL dedup) | 11,429 |
| Label distribution | 5,715 legitimate / 5,715 phishing (perfectly balanced) |
| Missing values | None in URL-only feature columns |
| Duplicate rows | 0 full-row duplicates; 1 duplicate URL (both phishing, deduped) |

### Feature groups

The dataset contains 88 features + 1 label column.  Only the **53 URL-only
features** are used for training and inference.

| Group | Count | Used | Reason excluded |
|-------|-------|------|-----------------|
| URL-only (lexical/structural) | 53 | **Yes** | Computable from URL string, no network access |
| Page-content (DOM/HTML) | 24 | No | Require HTTP request + DOM parsing |
| External/network | 10 | No | Require DNS, WHOIS, search-engine queries |

### Limitations

- Dataset collected in 2020. Phishing techniques evolve; the model may not
  generalise to current attacks.
- URL-only features miss page-level signals; a phishing page can have a
  clean-looking URL.
- Brand list (`allbrands.txt`, 257 entries) may miss newer brands.
- The model is a phishing-URL classifier, not a general malware detector.
- A low-risk prediction is not a safety guarantee.

## Reproducing training

```bash
python ml/train_url_model.py
```

Outputs: `ml/artifacts/url_model.joblib`, `ml/artifacts/feature_schema.json`,
`ml/artifacts/training_report.json`, `ml/reports/evaluation_report.json`.
