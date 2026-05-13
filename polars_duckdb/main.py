#!/usr/bin/env python3
"""Tidy data reshaping — Polars + DuckDB rewrite (UNPIVOT / PIVOT / GROUP BY)."""

import sys
import argparse
import yaml
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import (
    generate_wide_data, generate_weekly_sales_data,
    wide_to_long, long_to_wide, pivot_table_aggregation,
    groupby_aggregation, reshape_weekly_data,
    plot_weekly_trend, plot_store_comparison,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_config(config_path: Path = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Tidy data — Polars + DuckDB")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = Path(args.output_dir) if args.output_dir else Path(config["output"]["figures_dir"])
    output_dir.mkdir(exist_ok=True)

    stores = config["data"]["stores"]
    months = config["data"]["months"]

    # ── wide → long (UNPIVOT) ─────────────────────────────────────────────────
    if config["transformations"]["wide_to_long"]:
        wide_df = generate_wide_data(stores, months)
        long_df = wide_to_long(wide_df, "Store", months)
        logging.info(f"Wide format:\n{wide_df}")
        logging.info(f"Long format (UNPIVOT):\n{long_df}")

    # ── long → wide (PIVOT) ───────────────────────────────────────────────────
    if config["transformations"]["long_to_wide"]:
        back_to_wide = long_to_wide(long_df, "Store", "Month", "Sales")
        logging.info(f"Back to wide (PIVOT):\n{back_to_wide}")

    # ── pivot table with aggregation ──────────────────────────────────────────
    if config["transformations"]["pivot_table"]:
        pivot_df = pivot_table_aggregation(long_df, "Store", "Month", "Sales", "sum")
        logging.info(f"Pivot table (SUM):\n{pivot_df}")

    # ── groupby aggregation ───────────────────────────────────────────────────
    if config["transformations"]["groupby"]:
        weekly_stores = config["data"]["weekly_stores"]
        weekly_df = generate_weekly_sales_data(weekly_stores, config["data"]["weeks"])
        week_cols = [c for c in weekly_df.columns if c != "Store"]
        long_weekly = reshape_weekly_data(weekly_df, week_cols)
        agg_df = groupby_aggregation(
            long_weekly, ["Store"], "Sales",
            {"total": "sum", "avg": "mean", "min": "min", "max": "max"},
        )
        logging.info(f"GROUP BY aggregation:\n{agg_df}")

    # ── weekly analysis ───────────────────────────────────────────────────────
    if config["transformations"]["weekly_analysis"]:
        weekly_stores = config["data"]["weekly_stores"]
        weekly_df = generate_weekly_sales_data(weekly_stores, config["data"]["weeks"])
        week_cols = [c for c in weekly_df.columns if c != "Store"]
        long_weekly = reshape_weekly_data(weekly_df, week_cols)
        logging.info(f"Weekly long format (UNPIVOT):\n{long_weekly}")
        plot_weekly_trend(long_weekly, output_dir / "weekly_trend.png")
        plot_store_comparison(long_weekly, output_dir / "store_comparison.png")

    logging.info(f"Done. Figures saved to {output_dir}")


if __name__ == "__main__":
    main()
