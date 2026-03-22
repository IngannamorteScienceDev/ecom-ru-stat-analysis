import pandas as pd
import statsmodels.api as sm

from src.utils.paths import get_path, load_config
from src.utils.logging import print_info, print_success, print_warning


def build_factor_outputs() -> None:
    """
    Build factor correlation and regression outputs if external factors are available.
    """
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    corr_output = output_dir / "subjects_factor_correlation_matrix.csv"
    reg_output = output_dir / "subjects_factor_regression_coefficients.csv"
    fit_output = output_dir / "subjects_factor_regression_fit.csv"

    print_info("Building factor-analysis outputs for subject-level dataset.")

    if not input_file.exists():
        print_warning(f"Subjects dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)

    config = load_config()
    candidate_factors = list(config.get("external_factors", {}).keys())
    available_factors = [col for col in candidate_factors if col in df.columns and df[col].notna().any()]

    if not available_factors:
        print_warning("No external factor columns are available yet. Factor analysis skipped.")
        return

    corr_cols = ["share_online"] + available_factors
    df[corr_cols].corr().to_csv(corr_output, encoding="utf-8-sig")
    print_success(f"Saved factor correlation matrix: {corr_output}")

    model_df = df[["share_online", "year"] + available_factors].dropna().copy()
    if model_df.empty:
        print_warning("Factor regression dataset is empty after dropping NaN values.")
        return

    X = model_df[["year"] + available_factors]
    X = sm.add_constant(X)
    y = model_df["share_online"]

    model = sm.OLS(y, X).fit()

    coef_df = pd.DataFrame(
        {
            "variable": model.params.index,
            "coefficient": model.params.values,
            "p_value": model.pvalues.values,
        }
    )
    coef_df.to_csv(reg_output, index=False, encoding="utf-8-sig")

    fit_df = pd.DataFrame(
        {
            "metric": ["r_squared", "adj_r_squared", "n_obs"],
            "value": [model.rsquared, model.rsquared_adj, int(model.nobs)],
        }
    )
    fit_df.to_csv(fit_output, index=False, encoding="utf-8-sig")

    print_success(f"Saved factor regression coefficients: {reg_output}")
    print_success(f"Saved factor regression fit table: {fit_output}")