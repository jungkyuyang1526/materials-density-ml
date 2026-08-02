# Benchmarking Machine-Learning Models for Density Prediction in Si–O and Si–Al–O Materials

This repository benchmarks regression models for predicting Materials Project density values from a small set of physically interpretable composition and structural descriptors.

## Research question

How accurately can material density be predicted from a small set of physically interpretable composition and structural descriptors, and how much does combining composition and structural information improve over simpler baselines?

## What the project compares

- Mean-prediction baseline
- Composition-focused features
- Structure-focused features
- Combined composition and structure features
- Linear regression, ridge regression, polynomial ridge, KNN, and an optional random forest when dataset size supports it

The project uses grouped train–test splitting and grouped cross-validation by reduced formula so polymorphs with the same formula are not divided across training and test data.

## Security notice

An API key was embedded in an earlier notebook version. That key must be revoked before publication. This repository never stores a credential. Set a replacement key only through the `MP_API_KEY` environment variable.

macOS/Linux:

```bash
export MP_API_KEY="your_replacement_key"
```

Windows PowerShell:

```powershell
$env:MP_API_KEY="your_replacement_key"
```

Do not commit `.env` files or notebook outputs containing secrets.

## Repository structure

```text
materials-density-ml/
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   └── materials_density_prediction.ipynb
├── data/
│   ├── materials_snapshot.csv
│   └── materials_snapshot_metadata.json
├── figures/
└── src/
    └── data_collection.py
```


## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
jupyter lab
```

Open `notebooks/materials_density_prediction.ipynb`, then use **Restart Kernel and Run All Cells**.

The notebook first tries to load `data/materials_snapshot.csv` when `USE_CACHED_DATA = True`. If the snapshot is unavailable, it falls back to the Materials Project API and requires `MP_API_KEY`.

## Methodology

1. Retrieve exact Si–O and Si–Al–O chemical systems from the Materials Project summary endpoint.
2. Validate missing, duplicate, nonfinite, and nonpositive values before removing unusable rows.
3. Calculate stoichiometrically weighted mean atomic mass and volume per atom.
4. Compare composition-only, structure-only, and combined feature sets.
5. Split by reduced formula with `GroupShuffleSplit`.
6. Tune models on the training set with grouped cross-validation.
7. Evaluate finalized candidates once on the held-out grouped test set.
8. Inspect parity, residual, and largest-error results.

## Results

The final model selected through grouped cross-validation was K-Nearest
Neighbors using structural features.

- Grouped CV RMSE: 0.2527 ± 0.1444 g/cm³
- Test RMSE: 0.2700 g/cm³
- Test MAE: 0.2025 g/cm³
- Test R²: 0.7449
- Improvement over mean baseline: 58.2%
After execution, report:

- retrieved and retained sample counts,
- number of unique formula groups,
- selected feature set and model,
- grouped CV RMSE mean and standard deviation,
- test RMSE, MAE, and R²,
- comparison with the mean baseline,
- whether combined features improved on composition-only features, and
- major limitations and observed error patterns.



## Limitations

The analysis is restricted to Si–O and Si–Al–O computational entries, uses a compact descriptor set, lacks external experimental validation, and does not establish generalization to other chemical systems. Density is also strongly constrained by the known mass–volume relationship, so the project should be interpreted as a benchmarking and representation exercise.

## References

- Materials Project API documentation
- `mp-api` client documentation
- scikit-learn grouped cross-validation and pipeline documentation

## License

Add a license appropriate for the intended reuse before publication.
