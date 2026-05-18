import logging
from pathlib import Path

import pandas as pd
from src.core import (
    generate_weekly_sales_data,
    generate_wide_data,
    long_to_wide,
    pivot_table_aggregation,
    plot_store_comparison,
    plot_weekly_trend,
    reshape_weekly_data,
    wide_to_long,
)


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def demonstrate_wide_long_transforms() -> None:
    wide_df = generate_wide_data()
    long_df = wide_to_long(wide_df, id_vars="Store")
    long_to_wide(long_df, index="Store", columns="Month", values="Sales")
    pivot_table_aggregation(long_df, index="Store", columns="Month", values="Sales")
    data = pd.DataFrame(
        {
            "Store": ["A", "A", "A", "B", "B", "B"],
            "Month": ["Jan", "Feb", "Mar", "Jan", "Feb", "Mar"],
            "Sales": [100, 120, 130, 90, 100, 110],
        }
    )
    data.groupby("Store")["Sales"].sum().reset_index()
    data.groupby("Month")["Sales"].mean().reset_index()
    data.groupby(["Store", "Month"])["Sales"].sum().reset_index()
    data.groupby("Store")["Sales"].agg(["mean", "sum", "std"]).reset_index()
    (
        data.groupby("Store")["Sales"]
        .agg(avg_sales="mean", total_sales="sum", volatility="std")
        .reset_index()
    )


def main() -> None:
    configure_logging()
    output_dir = Path(".")
    demonstrate_wide_long_transforms()
    long = reshape_weekly_data(generate_weekly_sales_data())
    long.groupby("Store")["Sales"].agg(avg="mean", total="sum").reset_index()
    plot_weekly_trend(long, output_dir / "weekly_sales.png", plot=True)
    plot_store_comparison(long, output_dir / "store_weekly_sales.png", plot=True)


if __name__ == "__main__":
    main()
