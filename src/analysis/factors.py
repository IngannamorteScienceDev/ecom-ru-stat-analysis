import pandas as pd
import statsmodels.api as sm

from src.utils.paths import get_path, load_config
from src.utils.logging import print_info, print_success, print_warning


def build_factor_outputs() -> None:
    """
    Build factor correlation and regression outputs using the latest common year
    with sufficient available external factors.
    """
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    corr_output = output_dir / "subjects_factor_correlation_matrix.csv"
    reg_output = output_dir / "subjects_factor_regression_coefficients.csv"
    fit_output = output_dir / "subjects_factor_regression_fit.csv"
    sample_output = output_dir / "subjects_factor_regression_sample.csv"

    print_info("Building factor-analysis outputs for subject-level dataset.")

    if not input_file.exists():
        print_warning(f"Subjects dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)

    config = load_config()
    candidate_factors = list(config.get("external_factors", {}).keys())
    available_factors = [col for col in candidate_factors if col in df.columns and df[col].notna().any()]

    if len(available_factors) < 2:
        print_warning("Fewer than two external factors are available. Factor analysis skipped.")
        return

    # choose latest year with enough non-null observations
    best_year = None
    best_factors = None
    best_n = 0

    years = sorted(df["year"].dropna().unique())
    for year in years:
        year_df = df[df["year"] == year].copy()

        usable_factors = []
        for factor in available_factors:
            non_null_count = year_df[["share_online", factor]].dropna().shape[0]
            if non_null_count >= 20:
                usable_factors.append(factor)

        if len(usable_factors) >= 2:
            candidate_df = year_df[["region", "year", "share_online"] + usable_factors].dropna()
            if candidate_df.shape[0] > best_n:
                best_year = year
                best_factors = usable_factors
                best_n = candidate_df.shape[0]

    if best_year is None or best_factors is None:
        print_warning("No year with sufficient common factor coverage was found. Factor regression skipped.")
        return

    model_df = df[df["year"] == best_year][["region", "year", "share_online"] + best_factors].dropna().copy()

    if model_df.shape[0] < 20:
        print_warning("Factor regression sample is too small after filtering.")
        return

    corr_cols = ["share_online"] + best_factors
    model_df[corr_cols].corr().to_csv(corr_output, encoding="utf-8-sig")
    print_success(f"Saved factor correlation matrix: {corr_output}")

    X = model_df[best_factors]
    X = sm.add_constant(X)
    y = model_df["share_online"]

    model = sm.OLS(y, X).fit()

    coef_df = pd.DataFrame(
        {
            "variable": model.params.index,
            "coefficient": model.params.values,
            "std_error": model.bse.values,
            "t_stat": model.tvalues.values,
            "p_value": model.pvalues.values,
        }
    )
    coef_df.to_csv(reg_output, index=False, encoding="utf-8-sig")

    fit_df = pd.DataFrame(
        {
            "metric": [
                "regression_year",
                "n_obs",
                "r_squared",
                "adj_r_squared",
                "f_statistic",
                "f_pvalue",
            ],
            "value": [
                int(best_year),
                int(model.nobs),
                model.rsquared,
                model.rsquared_adj,
                model.fvalue,
                model.f_pvalue,
            ],
        }
    )
    fit_df.to_csv(fit_output, index=False, encoding="utf-8-sig")

    model_df.to_csv(sample_output, index=False, encoding="utf-8-sig")

    print_success(f"Saved factor regression coefficients: {reg_output}")
    print_success(f"Saved factor regression fit table: {fit_output}")
    print_success(f"Saved factor regression sample: {sample_output}")