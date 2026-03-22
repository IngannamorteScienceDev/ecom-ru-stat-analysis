from __future__ import annotations

import math

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter

from src.utils.paths import get_path, load_config
from src.utils.logging import print_info, print_success, print_warning


# ----------------------------
# Global plotting style
# ----------------------------
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10
plt.rcParams["legend.fontsize"] = 10
plt.rcParams["figure.titlesize"] = 15
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

sns.set_theme(style="whitegrid")


def _percent_formatter(x, pos):
    return f"{x:.1f}"


def _setup_axis(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, pad=14, weight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(FuncFormatter(_percent_formatter))
    ax.grid(True, linestyle="--", alpha=0.4)


def _annotate_line_points(ax, x_values, y_values, step: int = 1, fontsize: int = 9) -> None:
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        if i % step == 0 and pd.notna(y):
            ax.annotate(
                f"{y:.1f}",
                (x, y),
                textcoords="offset points",
                xytext=(0, 7),
                ha="center",
                fontsize=fontsize,
            )


def _annotate_bar_values(ax, fmt: str = "{:.1f}", fontsize: int = 9) -> None:
    for patch in ax.patches:
        value = patch.get_width() if patch.get_width() != 0 else patch.get_height()

        if patch.get_width() > patch.get_height():
            # horizontal bar
            x = patch.get_width()
            y = patch.get_y() + patch.get_height() / 2
            ax.annotate(
                fmt.format(x),
                (x, y),
                textcoords="offset points",
                xytext=(5, 0),
                va="center",
                fontsize=fontsize,
            )
        else:
            # vertical bar
            x = patch.get_x() + patch.get_width() / 2
            y = patch.get_height()
            ax.annotate(
                fmt.format(y),
                (x, y),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
                fontsize=fontsize,
            )


def plot_share_online_dynamics() -> None:
    input_file = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "share_online_rf_dynamics.png"

    print_info("Генерация основного графика динамики по Российской Федерации.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values("year")

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.plot(
        df["year"],
        df["share_online"],
        marker="o",
        linewidth=2.4,
        markersize=6,
        label="Доля онлайн-продаж",
    )
    _setup_axis(
        ax,
        "Динамика доли онлайн-продаж в обороте розничной торговли в Российской Федерации",
        "Год",
        "Доля онлайн-продаж, %",
    )
    _annotate_line_points(ax, df["year"], df["share_online"], step=1)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {output_file}")


def plot_rf_growth_rates() -> None:
    input_file = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "rf_growth_increment_pct.png"

    print_info("Генерация графика темпов прироста по Российской Федерации.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values("year")
    df_plot = df.dropna(subset=["growth_increment_pct"]).copy()

    fig, ax = plt.subplots(figsize=(11, 6.5))
    colors = ["#2E86DE" if val >= 0 else "#C0392B" for val in df_plot["growth_increment_pct"]]
    bars = ax.bar(df_plot["year"].astype(str), df_plot["growth_increment_pct"], color=colors)

    ax.set_title(
        "Годовые темпы прироста доли онлайн-продаж в Российской Федерации",
        pad=14,
        weight="bold",
    )
    ax.set_xlabel("Год")
    ax.set_ylabel("Темп прироста, %")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.axhline(0, color="black", linewidth=1)

    for bar, value in zip(bars, df_plot["growth_increment_pct"]):
        ax.annotate(
            f"{value:.1f}",
            (bar.get_x() + bar.get_width() / 2, value),
            textcoords="offset points",
            xytext=(0, 5 if value >= 0 else -15),
            ha="center",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {output_file}")


def plot_top_bottom_subjects() -> None:
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    top_output = output_dir / "top_subjects_latest_year.png"
    bottom_output = output_dir / "bottom_subjects_latest_year.png"

    config = load_config()
    top_n = int(config["analysis"]["latest_top_n"])

    print_info("Генерация рейтингов субъектов РФ по последнему доступному году.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    top_df = latest_df.sort_values("share_online", ascending=False).head(top_n).sort_values("share_online")
    bottom_df = latest_df.sort_values("share_online", ascending=True).head(top_n).sort_values("share_online")

    # Top
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(top_df["region"], top_df["share_online"])
    _setup_axis(
        ax,
        f"Топ-{top_n} субъектов РФ по доле онлайн-продаж, {latest_year} г.",
        "Доля онлайн-продаж, %",
        "Субъект РФ",
    )
    _annotate_bar_values(ax)
    fig.tight_layout()
    fig.savefig(top_output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Bottom
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(bottom_df["region"], bottom_df["share_online"])
    _setup_axis(
        ax,
        f"Анти-топ-{top_n} субъектов РФ по доле онлайн-продаж, {latest_year} г.",
        "Доля онлайн-продаж, %",
        "Субъект РФ",
    )
    _annotate_bar_values(ax)
    fig.tight_layout()
    fig.savefig(bottom_output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {top_output}")
    print_success(f"Сохранён график: {bottom_output}")


def plot_subject_growth_leaders() -> None:
    input_file = get_path("tables") / "subjects_first_last_comparison.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    abs_output = output_dir / "top_subjects_absolute_increase.png"
    cagr_output = output_dir / "top_subjects_cagr.png"

    print_info("Генерация графиков лидеров роста среди субъектов РФ.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file)

    top_abs = df.sort_values("absolute_increase", ascending=False).head(15).sort_values("absolute_increase")
    top_cagr = df.sort_values("cagr", ascending=False).head(15).sort_values("cagr")

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(top_abs["region"], top_abs["absolute_increase"])
    ax.set_title("Топ-15 субъектов РФ по абсолютному приросту доли онлайн-продаж", pad=14, weight="bold")
    ax.set_xlabel("Абсолютный прирост, п.п.")
    ax.set_ylabel("Субъект РФ")
    ax.grid(True, axis="x", linestyle="--", alpha=0.4)
    _annotate_bar_values(ax)
    fig.tight_layout()
    fig.savefig(abs_output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(top_cagr["region"], top_cagr["cagr"] * 100)
    ax.set_title("Топ-15 субъектов РФ по среднегодовому темпу роста (CAGR)", pad=14, weight="bold")
    ax.set_xlabel("CAGR, %")
    ax.set_ylabel("Субъект РФ")
    ax.grid(True, axis="x", linestyle="--", alpha=0.4)
    _annotate_bar_values(ax)
    fig.tight_layout()
    fig.savefig(cagr_output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {abs_output}")
    print_success(f"Сохранён график: {cagr_output}")


def plot_subject_first_last_scatter() -> None:
    input_file = get_path("tables") / "subjects_first_last_comparison.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "subjects_first_last_scatter.png"

    print_info("Генерация scatter-графика: первый и последний год по субъектам РФ.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file)

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.scatter(df["first_value"], df["last_value"], alpha=0.75)

    max_val = max(df["first_value"].max(), df["last_value"].max())
    ax.plot([0, max_val], [0, max_val], linestyle="--", linewidth=1.2, label="Линия равенства")

    ax.set_title("Сопоставление значений первого и последнего года по субъектам РФ", pad=14, weight="bold")
    ax.set_xlabel("Значение в первом году, %")
    ax.set_ylabel("Значение в последнем году, %")
    ax.xaxis.set_major_formatter(FuncFormatter(_percent_formatter))
    ax.yaxis.set_major_formatter(FuncFormatter(_percent_formatter))
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {output_file}")


def plot_subject_quartiles() -> None:
    input_file = get_path("tables") / "subjects_quartiles_by_year.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "subjects_quartiles_by_year.png"

    print_info("Генерация графика квартильной динамики по субъектам РФ.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.plot(df["year"], df["q1"], marker="o", label="Первый квартиль")
    ax.plot(df["year"], df["median"], marker="o", label="Медиана")
    ax.plot(df["year"], df["q3"], marker="o", label="Третий квартиль")
    ax.fill_between(df["year"], df["q1"], df["q3"], alpha=0.2, label="Межквартильный размах")

    _setup_axis(
        ax,
        "Квартильная динамика распределения доли онлайн-продаж по субъектам РФ",
        "Год",
        "Доля онлайн-продаж, %",
    )
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {output_file}")


def plot_subjects_boxplot_latest() -> None:
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "subjects_boxplot_latest_year.png"

    print_info("Генерация boxplot по субъектам РФ за последний год.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.boxplot(latest_df["share_online"].dropna(), vert=True, patch_artist=True)
    ax.set_title(f"Распределение доли онлайн-продаж по субъектам РФ, {latest_year} г.", pad=14, weight="bold")
    ax.set_ylabel("Доля онлайн-продаж, %")
    ax.yaxis.set_major_formatter(FuncFormatter(_percent_formatter))
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {output_file}")


def plot_subjects_heatmap() -> None:
    input_file = get_path("tables") / "subjects_heatmap_matrix.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "subjects_heatmap_top.png"

    print_info("Генерация уменьшенной тепловой карты по субъектам РФ.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file, index_col=0)

    fig, ax = plt.subplots(figsize=(12, 14))
    sns.heatmap(df, cmap="viridis", cbar=True, ax=ax)
    ax.set_title("Тепловая карта доли онлайн-продаж по ведущим субъектам РФ", pad=14, weight="bold")
    ax.set_xlabel("Год")
    ax.set_ylabel("Субъект РФ")
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {output_file}")


def plot_federal_district_dynamics() -> None:
    input_file = get_path("processed_data") / "master_federal_districts_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "federal_districts_dynamics.png"

    print_info("Генерация графика динамики по федеральным округам.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values(["region", "year"])

    fig, ax = plt.subplots(figsize=(12, 7))
    for region, group in df.groupby("region"):
        ax.plot(group["year"], group["share_online"], marker="o", linewidth=2, label=region)

    _setup_axis(
        ax,
        "Динамика доли онлайн-продаж по федеральным округам",
        "Год",
        "Доля онлайн-продаж, %",
    )
    ax.legend(fontsize=8, loc="upper left", ncol=2)
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {output_file}")


def plot_forecast_with_history() -> None:
    history_file = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    forecast_file = get_path("models") / "forecast_rf_values.csv"
    comparison_file = get_path("models") / "forecast_model_comparison.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "rf_history_and_forecast.png"

    print_info("Генерация итогового графика прогноза по Российской Федерации.")

    if not history_file.exists():
        print_warning(f"Файл не найден: {history_file}")
        return

    if not forecast_file.exists():
        print_warning(f"Файл не найден: {forecast_file}")
        return

    history_df = pd.read_csv(history_file).sort_values("year")
    forecast_df = pd.read_csv(forecast_file).sort_values("year")

    best_model_text = ""
    if comparison_file.exists():
        comparison_df = pd.read_csv(comparison_file)
        if not comparison_df.empty:
            best_model_text = f"Лучшая модель: {comparison_df.iloc[0]['model']}"

    fig, ax = plt.subplots(figsize=(11, 6.5))

    ax.plot(
        history_df["year"],
        history_df["share_online"],
        marker="o",
        linewidth=2.4,
        label="Исторические данные",
    )
    ax.plot(
        forecast_df["year"],
        forecast_df["forecast_share_online"],
        marker="o",
        linestyle="--",
        linewidth=2.2,
        label="Прогноз",
    )

    if {"lower_95", "upper_95"}.issubset(forecast_df.columns):
        ax.fill_between(
            forecast_df["year"],
            forecast_df["lower_95"],
            forecast_df["upper_95"],
            alpha=0.2,
            label="95%-ный интервал прогноза",
        )

    forecast_start = forecast_df["year"].min()
    ax.axvline(forecast_start, linestyle=":", linewidth=1.5)
    ax.annotate(
        "Начало прогнозного периода",
        (forecast_start, history_df["share_online"].max()),
        textcoords="offset points",
        xytext=(8, -10),
        fontsize=9,
    )

    _setup_axis(
        ax,
        "Динамика и прогноз доли онлайн-продаж в Российской Федерации",
        "Год",
        "Доля онлайн-продаж, %",
    )

    if best_model_text:
        ax.text(
            0.02,
            0.03,
            best_model_text,
            transform=ax.transAxes,
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", alpha=0.15),
        )

    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {output_file}")


def plot_factor_coefficients() -> None:
    input_file = get_path("tables") / "subjects_factor_regression_coefficients.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "subjects_factor_regression_coefficients.png"

    print_info("Генерация графика коэффициентов факторной регрессии.")

    if not input_file.exists():
        print_warning(f"Файл не найден: {input_file}")
        return

    df = pd.read_csv(input_file)

    df = df[df["variable"] != "const"].copy()
    if df.empty:
        print_warning("В таблице коэффициентов нет факторов для визуализации.")
        return

    df = df.sort_values("coefficient")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df["variable"], df["coefficient"])
    ax.axvline(0, color="black", linewidth=1)
    ax.set_title("Оценки коэффициентов факторной регрессии", pad=14, weight="bold")
    ax.set_xlabel("Оценка коэффициента")
    ax.set_ylabel("Фактор")
    ax.grid(True, axis="x", linestyle="--", alpha=0.4)
    _annotate_bar_values(ax, fmt="{:.3f}")
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print_success(f"Сохранён график: {output_file}")