# Dataset directory

Place raw dataset files here during T-02 development.

**Do not commit raw dataset files to version control.**
Add a `.gitignore` rule in this directory if needed, or rely on the
root-level `.gitignore` which already ignores common dataset extensions.

## Expected dataset for URL classification

A publicly licensed binary-label URL dataset is required.
Candidate sources (verify current access and license before downloading):

- **PhiUSIIL Phishing URL Dataset** — UCI ML Repository
  https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset
  License: CC BY 4.0 (verify at the source before use)

- **Malicious URLs Dataset (ISCX-URL-2016)** — Kaggle
  https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset
  License: verify on the dataset page before use

## After placing the dataset

Run the training script from the repository root:

```bash
python ml/train_url_model.py
```

Outputs are written to `ml/artifacts/` and `ml/reports/`.
See `ml/train_url_model.py` for reproducibility details (random seed, split).
