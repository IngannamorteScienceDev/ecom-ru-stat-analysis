# ecom-ru-stat-analysis

Statistical analysis of the Russian e-commerce market for a master's thesis in Business Informatics.

## Project goal

Build a reproducible analytical pipeline for:
- collecting and consolidating official and industry data,
- calculating key statistical indicators,
- analyzing dynamics and structure of the market,
- estimating factor relationships,
- building forecast scenarios,
- exporting figures and tables for insertion into a Word thesis.

## Data sources

Core sources:
- Rosstat
- Bank of Russia Data Service API
- EMISS
- Data Insight
- AKIT

## Project structure

- `config/` — configuration files
- `data/raw/` — original downloaded data
- `data/interim/` — temporary transformed files
- `data/processed/` — clean analytical datasets
- `outputs/figures/` — exported plots
- `outputs/tables/` — exported tables
- `outputs/models/` — saved model artifacts
- `outputs/logs/` — logs
- `notebooks/` — exploratory notebooks
- `src/` — source code
- `scripts/` — entrypoint scripts
- `tests/` — tests

## Main workflow

1. Collect raw data
2. Clean and harmonize datasets
3. Merge into analytical dataset
4. Calculate metrics
5. Produce analysis and plots
6. Fit models and generate forecasts
7. Export artifacts for thesis

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt